# -*- coding: utf-8 -*-
"""
Created on Jun 2024

@authors : Demets Guillaume & Hebbar Esma

"""
#--------------------------------------
# Importation des bibliothèques
#--------------------------------------
import sys
import numpy as np
import pyqtgraph as pg
import random
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel
from brian2 import *
from random import randint
from ModularGUI_Brian2.simulate_hh import Simulate_hh
from ModularGUI_Brian2.analysis_graphs import Calculate_mfr, Calculate_isi

#--------------------------------------
# On lance le modèle
#--------------------------------------
nb_neuron, statemon, I_monitor, spikemon, S = Simulate_hh()
from ModularGUI_Brian2.analysis_graphs import Calculate_mfr, Calculate_isi, Calculate_active_neurons

#--------------------------------------
# Configure the appearance of pyqtgraph
#--------------------------------------

pg.setConfigOption('background', 'w')

# Application and main window creation
app = QApplication([])
window = QMainWindow()
window.setWindowTitle('Modular Graphical Interface')

# Tab configurations
tab_widget = QTabWidget()
window.setCentralWidget(tab_widget)

#--------------------------------------
# Custom interactive plot widget class
#--------------------------------------
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
                point_data_with_color = (point_data, color)
                self.pointClicked.emit(point_data_with_color)
               
            else:
                self.pointClicked.emit((None,None))
        super().mousePressEvent(event)

#--------------------------------------
# First page : preferences
#--------------------------------------
tab_preferences = QWidget()
tab_widget.addTab(tab_preferences, "Preferences")
tab_preferences.layout = QVBoxLayout()
tab_preferences.setLayout(tab_preferences.layout)

# Button 1 to run HH model
button_run = QPushButton("Run HH model")
button_run.setMaximumWidth(200) 
tab_preferences.layout.addWidget(button_run)

nb_neuron, statemon, I_monitor, spikemon, S = Simulate_hh()

button_run.clicked.connect(Simulate_hh)

# Button 2to import data
button_import = QPushButton("Import data in .csv")
button_import.setMaximumWidth(200) 
tab_preferences.layout.addWidget(button_import)

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

button_import.clicked.connect(import_data)

#--------------------------------------
# Oscilloscope tab
#--------------------------------------

tab_oscilloscope = QWidget()
tab_widget.addTab(tab_oscilloscope, "Oscilloscope")
tab_oscilloscope.layout = QVBoxLayout()
tab_oscilloscope.setLayout(tab_oscilloscope.layout)

#first graph : membrane potential as a function of time
plot_scatterplot = pg.PlotWidget()
tab_oscilloscope.layout.addWidget(plot_scatterplot)

for i in range(nb_neuron):
    plot_scatterplot.plot(statemon.t/ms, statemon.v[i], pen=(i, nb_neuron))
plot_scatterplot.setLabel('left', 'Membrane potential (V)')
plot_scatterplot.setLabel('bottom', 'Time (ms)')
plot_scatterplot.showGrid(x=True, y=True, alpha=0.3)

#second plot : current as a function of time
plot_input_current  = pg.PlotWidget()
tab_oscilloscope.layout.addWidget(plot_input_current)
for i in range(nb_neuron):
    plot_input_current.plot(statemon.t/ms, statemon.I[i]/uA, pen=(i, nb_neuron))
plot_input_current.setLabel('left', 'Currents (uA)')
plot_input_current.setLabel('bottom', 'Time (ms)')

#--------------------------------------
# Rasterplot tab
#--------------------------------------
tab_rasterplot = QWidget()
tab_widget.addTab(tab_rasterplot, "Rasterplot")
tab_rasterplot.layout = QVBoxLayout()
tab_rasterplot.setLayout(tab_rasterplot.layout)

#first graph : neuron index as a function of time
plot_rasterplot = InteractivePlotWidget()
tab_rasterplot.layout.addWidget(plot_rasterplot)

# Création d'une liste de couleurs, une pour chaque neurone
colors = [pg.mkColor((randint(0, 255), randint(0, 255), randint(0, 255))) for _ in range(nb_neuron)]

spike_data = []
for t, i in zip(spikemon.t, spikemon.i):
    spike_data.append({'pos': (t/ms, i), 'data': (t/ms, i), 'brush': colors[i], 'size': 5})

scatter = pg.ScatterPlotItem(pen=None, symbol='o')
plot_rasterplot.addItem(scatter)
scatter.addPoints(spike_data)
plot_rasterplot.scatter = scatter

# window for text and data
descriptive_data = QTextEdit()
descriptive_data.setReadOnly(True)

plot_rasterplot.setLabel('left', 'Neuron index')
plot_rasterplot.setLabel('bottom', 'Time (ms)')

details_layout = QVBoxLayout()
tab_rasterplot.layout.addLayout(details_layout)
details_plot = pg.PlotWidget()
details_layout.addWidget(details_plot)

def on_point_clicked(data_with_color):
    if data_with_color[0]==None:
        descriptive_data.append("Aucun point de données n'a été cliqué.\n")
        return
    else :
        data, color = data_with_color 
        
        message = f'-------------------------------------------------------------------------------------------------------------\n'
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
tab_rasterplot.layout.addWidget(descriptive_data)

plot_rasterplot.pointClicked.connect(on_point_clicked)

#--------------------------------------
#  Tab for stats
#--------------------------------------
tab_stats = QWidget()
tab_widget.addTab(tab_stats, "Stats")
tab_stats.layout = QVBoxLayout()
tab_stats.setLayout(tab_stats.layout)

index, data = Calculate_mfr(nb_neuron, spikemon)

# Créer le widget de tracé avec PyQtGraph
mfr_plot_widget = pg.PlotWidget()
tab_stats.layout.addWidget(mfr_plot_widget)

# Créer l'élément BarGraphItem et l'ajouter au PlotWidget
bar_graph = pg.BarGraphItem(x=index, height=data, width=0.6, brush='b')
mfr_plot_widget.addItem(bar_graph)

# Définir les étiquettes des axes et le titre du graphique
mfr_plot_widget.setLabel('left', 'Nombre de Spikes par Secondes (Hz)')
mfr_plot_widget.setLabel('bottom', 'Numéro du neurone')
mfr_plot_widget.setTitle('Mean Firing Rate Network (MFR)')

# ISI

#ISI
x,y=Calculate_isi(nb_neuron,spikemon)

isi_plot_widget = pg.PlotWidget()
tab_stats.layout.addWidget(isi_plot_widget)

isi_plot_widget.clear()
isi_plot_widget.plot(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 150))
isi_plot_widget.setLabel('left', 'Nombre d\'intervalles')
isi_plot_widget.setLabel('bottom', 'Intervalle interspikes (ms)')
isi_plot_widget.setTitle('Inter Spike Interval (ISI)')  # Ajouter un titre au graphique

# IBI
# TODO
#--------------------------------------
#  Tab for some data (simple functions)
#--------------------------------------

tab_active_neurons = QWidget()
tab_widget.addTab(tab_active_neurons, "Active neurons")
tab_active_neurons.layout = QVBoxLayout()
tab_active_neurons.setLayout(tab_active_neurons.layout)

#actives neurons
active_neurons = Calculate_active_neurons(nb_neuron,spikemon)

data_label = QLabel()
data_text = "Neurones les plus actifs par ordre décroissant :\n"
data_text += "\n".join([f"Neurone {idx} : {rate:.4f} Hz" for idx, rate in active_neurons])
data_label.setText(data_text)
tab_active_neurons.layout.addWidget(data_label)

#--------------------------------------
#  Tab for synapses
#--------------------------------------

tab_synapses = QWidget()
tab_widget.addTab(tab_synapses, "Synapse Connectivity")
tab_synapses.layout = QVBoxLayout()
tab_synapses.setLayout(tab_synapses.layout)

plot_synapses = pg.GraphicsLayoutWidget()
tab_synapses.layout.addWidget(plot_synapses)

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

#--------------------------------------
# Tab for data export
#--------------------------------------
tab_export = QWidget()
tab_widget.addTab(tab_export, "Export")
tab_export.layout = QVBoxLayout()
tab_export.setLayout(tab_export.layout)

# Button to export data
button_export = QPushButton("Export data in .csv")
button_export.setMaximumWidth(200) 
tab_export.layout.addWidget(button_export)

# Function to export data
def export_data():
    import csv
    with open('spike_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (ms)", "Neuron Index"])
        for t, i in zip(spikemon.t/ms, spikemon.i):
            writer.writerow([t, i])
    print("Data exported successfully!")

button_export.clicked.connect(export_data)

#--------------------------------------
# Show the main window and start the application
#--------------------------------------
window.show()
app.exec_()
