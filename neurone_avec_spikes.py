# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 10:29:16 2024
@author: esma et guillaume
"""
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from brian2 import *

from model_HH import Calculer

nb_neuron,statemon,I_monitor ,spikemon= Calculer()

# Configure the appearance of pyqtgraph
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

# Création de l'application et de la fenêtre principale
app = QApplication([])
window = QMainWindow()
window.setWindowTitle('Oscilloscope Modulaire')

# Configurations des onglets
tab_widget = QTabWidget()
window.setCentralWidget(tab_widget)

# Onglet pour l'oscilloscope
tab1 = QWidget()
tab_widget.addTab(tab1, "Oscilloscope")
tab1.layout = QVBoxLayout()
tab1.setLayout(tab1.layout)

plot1_widget = pg.PlotWidget()
tab1.layout.addWidget(plot1_widget)
# Affichage du résultat de la simulation
for i in range(nb_neuron):
    plot1_widget.plot(statemon.t/ms, statemon.v[i], pen=(i, nb_neuron))
# Ajout des labels
plot1_widget.setLabel('left', 'Membrane potential (V)')
plot1_widget.setLabel('bottom', 'Time (ms)')
# Ajout d'un quadrillage
plot1_widget.showGrid(x=True, y=True, alpha=0.3)

plot3_widget = pg.PlotWidget()
tab1.layout.addWidget(plot3_widget)
# Affichage du résultat de la stimulation
for i in range(nb_neuron):
    plot3_widget.plot(I_monitor.t/ms, I_monitor.I[i]/uA, pen=(i, nb_neuron))
# Ajout des labels
plot3_widget.setLabel('left', 'Applied currents (uA)')
plot3_widget.setLabel('bottom', 'Time (ms)')

# Onglet pour les Spikes
tab2 = QWidget()
tab_widget.addTab(tab2, "Spikes")
tab2.layout = QVBoxLayout()
tab2.setLayout(tab2.layout)
plot2_widget = pg.PlotWidget()
tab2.layout.addWidget(plot2_widget)

# Affichage des spikes
plot2_widget.plot(spikemon.t/ms, np.array(spikemon.i), pen=None, symbol='o')

# Ajout des labels pour le graphique des spikes
plot2_widget.setLabel('left', 'Neuron index')
plot2_widget.setLabel('bottom', 'Time (ms)')

# Onglet pour les stats
tab3 = QWidget()
tab_widget.addTab(tab3, "Stats")
tab3.layout = QVBoxLayout()
tab3.setLayout(tab3.layout)
#plot3_widget = pg.PlotWidget()
#tab3.layout.addWidget(plot3_widget)

# Affichage de la fenêtre
window.show()
app.exec_()
