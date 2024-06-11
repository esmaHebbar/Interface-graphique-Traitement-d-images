# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 10:29:16 2024
@author: esma et guillaume
"""
import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog
from PyQt5.QtCore import pyqtSignal
from brian2 import *
import random


# Configure the appearance of pyqtgraph
pg.setConfigOption('background', 'w')

# Application and main window creation
app = QApplication([])
window = QMainWindow()
window.setWindowTitle('Oscilloscope Modulaire')

# Tab configurations
tab_widget = QTabWidget()
window.setCentralWidget(tab_widget)

defaultclock.dt = 0.01*ms

# Hodgkin-Huxley model parameters
Cm = 1.0*ufarad
El = 0*mV
ENa = 120.0*mV
EK = -12.0*mV
gl0 = 0.3*msiemens
gNa0 = 120.0*msiemens
gK0 = 36.0*msiemens

# Differential equations for the Hodgkin-Huxley model
eqs = '''
dv/dt = (I - gl * (v-El) - gNa * m**3 * h * (v-ENa) - gK * n**4 * (v-EK))/Cm : volt
I : amp (constant)  # Applied current

dn/dt = alphan * (1-n) - betan * n : 1
dm/dt = alpham * (1-m) - betam * m : 1
dh/dt = alphah * (1-h) - betah * h : 1

alphan = (0.01/mV) * 10*mV/exprel((-v+10*mV)/(10*mV))/ms : Hz
betan = 0.125*exp(-v/(80*mV))/ms : Hz

alpham = (0.1/mV) * 10*mV/exprel((-v+25*mV)/(10*mV))/ms : Hz
betam = 4 * exp(-v/(18*mV))/ms : Hz

alphah = 0.07 * exp(-v/(20*mV))/ms : Hz
betah = 1/(exp((-v+30*mV) / (10*mV)) + 1)/ms : Hz

gNa : siemens
gK : siemens
gl : siemens
'''

# Create a neuron group with the defined equations
HH = NeuronGroup(10, eqs, threshold='v>20*mV', refractory=5*ms, method='rk4')
HH.v = El
HH.h = 0.75
HH.m = 0.15
HH.n = 0.35
HH.gNa = gNa0
HH.gK = gK0
HH.gl = gl0

# Monitoring state variables and spikes
statemon = StateMonitor(HH, True, record=True)
spikemon = SpikeMonitor(HH)

# Running simulations with different applied currents
HH.I = 0.0*uA
run(50*ms, report='text')
HH.I = 30.0*uA
run(50*ms, report='text')
HH.I = 0.0*uA
run(50*ms, report='text')

# Custom interactive plot widget class
class InteractivePlotWidget(pg.PlotWidget):
    pointClicked = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scatter = None

    def mousePressEvent(self, event):
        if self.scatter:
            pos = self.plotItem.vb.mapSceneToView(event.pos())
            # print(f"Position du clic : {pos}")
            points = self.scatter.pointsAt(pos)
            # print(f"Points trouvés : {points}")
            # print(points)
            
            if points:  
            
                # for point in points:
                #     print(f"Point details: {point.data()}, pos: {point.pos()}, index: {point.index()}")
                point = points[0]
                point_data = point.data()
                color = colors[point_data[1]]  # Récupérer la couleur en utilisant l'index du neurone
                point_data_with_color = (point_data, color)
                
                # self.pointClicked.emit(points[0].data())
                self.pointClicked.emit(point_data_with_color)
                # print(f"Point cliqué : {points[0].data()}")
            else:
                self.pointClicked.emit((None,None))
                # print("Aucun point cliqué..")
        super().mousePressEvent(event)



#--------------------------------------
# Tab 0 pour la première page
tab0 = QWidget()
tab_widget.addTab(tab0, "Préférences")
tab0.layout = QVBoxLayout()
tab0.setLayout(tab0.layout)

# -----

# Button 1 pour run le modèle HH
bouton1 = QPushButton("Run le modèle HH")
bouton1.setMaximumWidth(200) 
tab0.layout.addWidget(bouton1)

# Function pour run le modele HH
def run_HH_model():
    # Reinitialize the neuron group's membrane potential
    HH.v = El  # Reset membrane potential to initial level
    HH.h = 0.75
    HH.m = 0.15
    HH.n = 0.35
    HH.I = 30.0*uA  # Apply a current

    run(100*ms, report='text')  # Run the model for 100 ms

    # Update the plots with the new data
    plot1_widget.clear()
    plot1_widget.plot(statemon.t/ms, statemon.v[0], pen='k')
    plot3_widget.clear()
    plot3_widget.plot(statemon.t/ms, statemon.I[0]/uA, pen='r')

    print("HH model running!")

# Connect the export button to the function
bouton1.clicked.connect(run_HH_model)

# -----

# Button 2 pour importer des données
bouton2 = QPushButton("Importer les données en .csv")
bouton2.setMaximumWidth(200) 
tab0.layout.addWidget(bouton2)

# Function pour importer des données
def import_data():
    import csv
    options = QFileDialog.Options()
    fileName, _ = QFileDialog.getOpenFileName(window, "Open CSV file", "", "CSV Files (*.csv)", options=options)
    if fileName:
        print("Importing data from:", fileName)
        with open(fileName, 'r') as file:
            reader = csv.reader(file)
            print(reader)
            for row in reader:
                print(row) 
    
    print("Data imported successfully!")

# Connect the export button to the function
bouton2.clicked.connect(import_data)
#--------------------------------------

# Oscilloscope tab
tab1 = QWidget()
tab_widget.addTab(tab1, "Oscilloscope")
tab1.layout = QVBoxLayout()
tab1.setLayout(tab1.layout)
plot1_widget = pg.PlotWidget()
tab1.layout.addWidget(plot1_widget)
plot1_widget.plot(statemon.t/ms, statemon.v[0], pen='k')
plot1_widget.setLabel('left', 'Membrane potential (V)')
plot1_widget.setLabel('bottom', 'Time (ms)')
plot3_widget = pg.PlotWidget()
tab1.layout.addWidget(plot3_widget)
plot3_widget.plot(statemon.t/ms, statemon.I[0]/uA, pen='r')
plot3_widget.setLabel('left', 'Currents (uA)')
plot3_widget.setLabel('bottom', 'Time (ms)')
plot1_widget.showGrid(x=True, y=True, alpha=0.3)

# Spikes tab
tab2 = QWidget()
tab_widget.addTab(tab2, "Rasterplot")
tab2.layout = QVBoxLayout()
tab2.setLayout(tab2.layout)
plot2_widget = InteractivePlotWidget()
tab2.layout.addWidget(plot2_widget)

# Création d'une liste de couleurs, une pour chaque neurone
colors = [pg.mkColor((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))) for _ in range(len(HH))]


spike_data = []
for t, i in zip(spikemon.t, spikemon.i):
    spike_data.append({'pos': (t/ms, i), 'data': (t/ms, i), 'brush': colors[i], 'size': 5})


scatter = pg.ScatterPlotItem(pen=None, symbol='o')
plot2_widget.addItem(scatter)
scatter.addPoints(spike_data)
plot2_widget.scatter = scatter

# Ajout d'un QTextEdit pour afficher les messages de débogage
descriptive_data = QTextEdit()
descriptive_data.setReadOnly(True)
# tab2.layout.addWidget(descriptive_data)

plot2_widget.setLabel('left', 'Neuron index')
plot2_widget.setLabel('bottom', 'Time (ms)')
details_layout = QVBoxLayout()
tab2.layout.addLayout(details_layout)
details_plot = pg.PlotWidget()
details_layout.addWidget(details_plot)

def on_point_clicked(data_with_color):
    if data_with_color is None:
        descriptive_data.append("Aucun point de données n'a été cliqué.\n")
        return
    
    data, color = data_with_color  # Décomposer les données reçues
    # descriptive_data.clear()  # Clear previous messages
    message = f'-------------------------------------------------------------------------------------------------------------\n'
    descriptive_data.append(message)
    message = f'Données sur le point cliqué : \n'
    descriptive_data.append(message)
    
    
    
    neuron_index = data[1]
    message = f'        Neuron index : {neuron_index}\n'
    descriptive_data.append(message)
    
    times = spikemon.t[spikemon.i == neuron_index]/ms
    details_plot.clear()
    details_plot.plot(times, np.ones_like(times), pen=None, symbol='t', symbolBrush=color, symbolSize=10)
    details_plot.setLabel('bottom', 'Time (ms)')
    details_plot.setLabel('left', 'Spike Marker')
    
    # message = f"Spikes détectés aux instants : {times}\n"
    # descriptive_data.append(message)
    
    for i in range (len(times)) :
        message = f"        Spike n°{i+1} détecté à l'instant : {times[i]} ms\n"
        descriptive_data.append(message)




descriptive_data.setMinimumHeight(200)
tab2.layout.addWidget(descriptive_data)

plot2_widget.pointClicked.connect(on_point_clicked)


#--------------------------------------
# Third tab for data export
tab3 = QWidget()
tab_widget.addTab(tab3, "Exporter")
tab3.layout = QVBoxLayout()
tab3.setLayout(tab3.layout)

# Button to export data
bouton_exporter = QPushButton("Exporter les données en .csv")
bouton_exporter.setMaximumWidth(200) 
tab3.layout.addWidget(bouton_exporter)

# Function to export data
def export_data():
    import csv
    with open('spike_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (ms)", "Neuron Index"])
        for t, i in zip(spikemon.t/ms, spikemon.i):
            writer.writerow([t, i])
    print("Data exported successfully!")

# Connect the export button to the function
bouton_exporter.clicked.connect(export_data)



#--------------------------------------

# Show the main window and start the application

window.show()
app.exec_()
