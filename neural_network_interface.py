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

from HH_model import Calculer

nb_neuron, statemon, I_monitor, spikemon = Calculer()

# Configure the appearance of pyqtgraph
pg.setConfigOption('background', 'w')

# Application and main window creation
app = QApplication([])
window = QMainWindow()
window.setWindowTitle('Interface Graphique Modulaire')
tab_widget = QTabWidget()
window.setCentralWidget(tab_widget)


# Custom interactive plot widget class
class InteractivePlotWidget(pg.PlotWidget):
    pointClicked = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scatter = None

    def mousePressEvent(self, event):
        if self.scatter:
            pos = self.plotItem.vb.mapSceneToView(event.pos())
            points = self.scatter.pointsAt(pos) 
            if points:
                point = points[0]
                point_data = point.data()
                color = colors[point_data[1]]
                self.pointClicked.emit((point_data, color))   
            else:
                self.pointClicked.emit((None,None))
        super().mousePressEvent(event)



#--------------------------------------
# Tab 0 for preferences
tab0 = QWidget()
tab_widget.addTab(tab0, "Préférences")
tab0.layout = QVBoxLayout()
tab0.setLayout(tab0.layout)

# -----

# Button 1 to run HH model
bouton1 = QPushButton("Run le modèle HH")
bouton1.setMaximumWidth(200) 
tab0.layout.addWidget(bouton1)

def run_HH_model():
    HH.v = El
    HH.h = 0.75
    HH.m = 0.15
    HH.n = 0.35
    HH.I = 30.0*uA
    run(100*ms, report='text')
    plot1_widget.clear()
    plot1_widget.plot(statemon.t/ms, statemon.v[0], pen='k')
    plot3_widget.clear()
    plot3_widget.plot(statemon.t/ms, statemon.I[0]/uA, pen='r')

bouton1.clicked.connect(run_HH_model)

# -----

# Button to import data
bouton2 = QPushButton("Importer les données en .csv")
bouton2.setMaximumWidth(200) 
tab0.layout.addWidget(bouton2)

def import_data():
    import csv
    options = QFileDialog.Options()
    fileName, _ = QFileDialog.getOpenFileName(window, "Open CSV file", "", "CSV Files (*.csv)", options=options)
    if fileName:
        print("Importing data from:", fileName)
        with open(fileName, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                print(row) 
    print("Data imported successfully!")

bouton2.clicked.connect(import_data)

#--------------------------------------

# Oscilloscope tab
tab1 = QWidget()
tab_widget.addTab(tab1, "Oscilloscope")
tab1.layout = QVBoxLayout()
tab1.setLayout(tab1.layout)
plot1_widget = pg.PlotWidget()
tab1.layout.addWidget(plot1_widget)

for i in range(nb_neuron):
    plot1_widget.plot(statemon.t/ms, statemon.v[i], pen=(i, nb_neuron))
    
plot1_widget.setLabel('left', 'Membrane potential (V)')
plot1_widget.setLabel('bottom', 'Time (ms)')
plot3_widget = pg.PlotWidget()
tab1.layout.addWidget(plot3_widget)
plot3_widget.plot(statemon.t/ms, statemon.I[0]/uA, pen='r')
plot3_widget.setLabel('left', 'Currents (uA)')
plot3_widget.setLabel('bottom', 'Time (ms)')
plot1_widget.showGrid(x=True, y=True, alpha=0.3)

# Rasterplot tab
tab2 = QWidget()
tab_widget.addTab(tab2, "Rasterplot")
tab2.layout = QVBoxLayout()
tab2.setLayout(tab2.layout)
plot2_widget = InteractivePlotWidget()
tab2.layout.addWidget(plot2_widget)

# Création d'une liste de couleurs, une pour chaque neurone
colors = [pg.mkColor((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))) for _ in range(nb_neuron)]

spike_data = []
for t, i in zip(spikemon.t, spikemon.i):
    spike_data.append({'pos': (t/ms, i), 'data': (t/ms, i), 'brush': colors[i], 'size': 5})

scatter = pg.ScatterPlotItem(pen=None, symbol='o')
plot2_widget.addItem(scatter)
scatter.addPoints(spike_data)
plot2_widget.scatter = scatter

descriptive_data = QTextEdit()
descriptive_data.setReadOnly(True)

plot2_widget.setLabel('left', 'Neuron index')
plot2_widget.setLabel('bottom', 'Time (ms)')

membrane_potential_plot = pg.PlotWidget()
membrane_potential_plot.setLabel('left', 'Membrane Potential (V)')
membrane_potential_plot.setLabel('bottom', 'Time (ms)')
tab2.layout.addWidget(membrane_potential_plot)


def on_point_clicked(data_with_color):
    if data_with_color is None:
        descriptive_data.append("Aucun point de données n'a été cliqué.\n")
        return
    
    data, color = data_with_color  
    neuron_index = data[1]
    
    times = statemon.t/ms
    voltages = statemon.v[neuron_index]
    
    message = f'-------------------------------------------------------------------------------------------------------------\n'
    descriptive_data.append(message)
    message = f'Données sur le point cliqué : \n'
    descriptive_data.append(message)
    message = f'        Neuron index : {neuron_index}\n'
    descriptive_data.append(message)
    
    membrane_potential_plot.clear()
    membrane_potential_plot.plot(times, voltages, pen={'color': color, 'width': 2})
    membrane_potential_plot.setLabel('bottom', 'Time (ms)')
    membrane_potential_plot.setLabel('left', 'Membrane Potential (V)')
    
    spikes = spikemon.t[spikemon.i == neuron_index]/ms
    for i, spike_time in enumerate(spikes):
        message = f"        Spike n°{i+1} détecté à l'instant : {spike_time} ms\n"
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

bouton_exporter.clicked.connect(export_data)

#--------------------------------------

# Show the main window and start the application
window.show()
app.exec_()
