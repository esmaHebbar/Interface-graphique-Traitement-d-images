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
import matplotlib.pyplot as plt

from HH_model import Calculer

nb_neuron, statemon, I_monitor, spikemon, S = Calculer()

#--------------------------------------
# Configure the appearance of pyqtgraph
pg.setConfigOption('background', 'w')

# Application and main window creation
app = QApplication([])
window = QMainWindow()
window.setWindowTitle('Interface Graphique Modulaire')

# Tab configurations
tab_widget = QTabWidget()
window.setCentralWidget(tab_widget)

#--------------------------------------
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
                color = colors[point_data[1]]  # Récupérer la couleur en utilisant l'index du neurone
                point_data_with_color = (point_data, color)
                self.pointClicked.emit(point_data_with_color)
               
            else:
                self.pointClicked.emit((None,None))
        super().mousePressEvent(event)

#--------------------------------------
# Tab 0 for the first page
#--------------------------------------

tab0 = QWidget()
tab_widget.addTab(tab0, "Préférences")
tab0.layout = QVBoxLayout()
tab0.setLayout(tab0.layout)

# Button 1 in order to run HH model
bouton1 = QPushButton("Run le modèle HH")
bouton1.setMaximumWidth(200) 
tab0.layout.addWidget(bouton1)
bouton1.clicked.connect(Calculer)

# Button 2 pour importer des données
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
#--------------------------------------
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
for i in range(nb_neuron):
    plot3_widget.plot(statemon.t/ms, statemon.I[i]/uA, pen=(i, nb_neuron))
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
details_layout = QVBoxLayout()
tab2.layout.addLayout(details_layout)
details_plot = pg.PlotWidget()
details_layout.addWidget(details_plot)

def on_point_clicked(data_with_color):
    if data_with_color is None:
        descriptive_data.append("Aucun point de données n'a été cliqué.\n")
        return
    
    data, color = data_with_color  
    
    message = f'-------------------------------------------------------------------------------------------------------------\n'
    descriptive_data.append(message)
    message = f'Données sur le point cliqué : \n'
    descriptive_data.append(message)
    
    neuron_index = data[1]
    message = f'        Neuron index : {neuron_index}\n'
    descriptive_data.append(message)
    
    # times = spikemon.t[spikemon.i == neuron_index]/ms
    times=statemon.t/ms
    voltages=statemon.v[neuron_index]
    details_plot.clear()
    details_plot.plot(times, voltages, pen={'color':color,'width':2})
    details_plot.setLabel('bottom', 'Time (ms)')
    details_plot.setLabel('left', 'Voltage')
    
    spikes=spikemon.t[spikemon.i==neuron_index]/ms
    for i,spike_time in enumerate (spikes) :
        message = f"        Spike n°{i+1} détecté à l'instant : {spike_time} ms\n"
        descriptive_data.append(message)

descriptive_data.setMinimumHeight(200)
tab2.layout.addWidget(descriptive_data)

plot2_widget.pointClicked.connect(on_point_clicked)

#--------------------------------------
# Third tab for Statistics
#--------------------------------------
#tab for stats
tab_stats = QWidget()
tab_widget.addTab(tab_stats, "Stats")
tab_stats.layout = QVBoxLayout()
tab_stats.setLayout(tab_stats.layout)

isi_plot_widget = pg.PlotWidget()
tab_stats.layout.addWidget(isi_plot_widget)

def plot_isi_histogram():
    isi_plot_widget.clear()
    isi_values = [] #contenant les valeurs des intervalles interspikes
    
    for m in range (nb_neuron):
        spike_times = np.array(spikemon.t[spikemon.i == m]) / ms
        
        if len(spike_times) > 1:
            # Calcul des intervalles interspikes
            isi = np.diff(spike_times)
            isi_values.extend(isi)  # ajout de isi dans isi_values
    
    if isi_values:
        # Convertir la liste en un array numpy pour l'histogramme
        isi_values = np.array(isi_values)
        
        # Création de l'histogramme
        # y, x = np.histogram(isi_values, bins=np.linspace(0, max(isi_values)+1, num=int(max(isi_values)+1)//2 + 1))
        bins = np.logspace(np.log10(min(isi_values)), np.log10(max(isi_values)), 50)  # Utilisez une échelle logarithmique pour les bins
        y, x = np.histogram(isi_values, bins=bins)

        isi_plot_widget.plot(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 150))
        isi_plot_widget.setLabel('left', 'Nombre d\'intervalles')
        isi_plot_widget.setLabel('bottom', 'Intervalle interspikes (ms)')
        
    else:
        isi_plot_widget.setTitle("No sufficient spike data for ISI calculation")

# update_isi_button = QPushButton("Update ISI Histogram")
# tab_stats.layout.addWidget(update_isi_button)
# update_isi_button.clicked.connect(plot_isi_histogram)


# MFR_plot_widget = pg.PlotWidget()
# tab_stats.layout.addWidget(MFR_plot_widget)

# def MFR():
#     duree_totale = 150  # en ms
#     taille_intervalle = 5  # en ms

#     # Générer les intervalles successifs de 1 ms
#     intervalles = [(start, start + taille_intervalle) for start in range(0, duree_totale, taille_intervalle)]

#     # Dictionnaire pour stocker les indices pour chaque intervalle
#     resultats = {}

#     # Parcourir chaque intervalle
#     for intervalle_min, intervalle_max in intervalles:
#         # Récupérer les indices correspondants aux temps dans l'intervalle courant
#         indices_cibles = [i for t, i in zip(spikemon.t/ms, spikemon.i) if intervalle_min <= t < intervalle_max]
#         # Stocker le résultat dans le dictionnaire
#         resultats[f"{intervalle_min}-{intervalle_max}"] = indices_cibles

#     # Préparer les données pour l'histogramme
#     hist_data = []
#     for intervalle, indices_cibles in resultats.items():
#         hist_data.append(len(indices_cibles) / nb_neuron)  # Normaliser par le nombre de neurones

#     # Générer les labels pour les intervalles
#     labels = [f"{intervalle_min}" for intervalle_min, intervalle_max in intervalles]

#     MFR_plot_widget.plot(labels, hist_data)
#     MFR_plot_widget.setLabel('left', 'Fréquences de spikes')
#     MFR_plot_widget.setLabel('bottom', 'Intervalle de temps (ms)')


plot_isi_histogram()
# MFR()


#--------------------------------------
#  tab for synapses
#--------------------------------------
tab_synapses = QWidget()
tab_widget.addTab(tab_synapses, "Synapse Connectivity")
tab_synapses.layout = QVBoxLayout()
tab_synapses.setLayout(tab_synapses.layout)

plot_synapses = pg.GraphicsLayoutWidget()
tab_synapses.layout.addWidget(plot_synapses)

def plot_synapses_histogram():
    glw = plot_synapses
    glw.clear()
    
    Ns = len(S.source)
    Nt = len(S.target)
    
    p1 = glw.addPlot(title="Source and Target Neurons")
    p1.plot(zeros(Ns), arange(Ns), pen=None, symbol='o', symbolBrush='k', symbolSize=10)
    p1.plot(ones(Nt), arange(Nt), pen=None, symbol='o', symbolBrush='k', symbolSize=10)
    for i, j in zip(S.i, S.j):
        p1.plot([0, 1], [i, j], pen='k')
    p1.getAxis('bottom').setTicks([[(0, 'Source'), (1, 'Target')]])
    p1.getAxis('left').setLabel('Neuron index')

    # Plot source neuron index vs. target neuron index
    p2 = glw.addPlot(title="Source vs Target Neuron Index")
    p2.plot(np.array(S.i), np.array(S.j), pen=None, symbol='o', symbolBrush='k')
    p2.setLabel('bottom', 'Source neuron index')
    p2.setLabel('left', 'Target neuron index')


#     plot1_widget.plot(statemon.t/ms, statemon.v[i], pen=(i, nb_neuron))
# plot1_widget.setLabel('left', 'Membrane potential (V)')
# plot1_widget.setLabel('bottom', 'Time (ms)')

    

plot_synapses_histogram()


#--------------------------------------

#--------------------------------------
# Fourth tab for data export
#--------------------------------------
tab4 = QWidget()
tab_widget.addTab(tab4, "Exporter")
tab4.layout = QVBoxLayout()
tab4.setLayout(tab4.layout)

# Button to export data
bouton_exporter = QPushButton("Exporter les données en .csv")
bouton_exporter.setMaximumWidth(200) 
tab4.layout.addWidget(bouton_exporter)

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
