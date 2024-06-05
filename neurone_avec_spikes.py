# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 10:29:16 2024
@author: esma et guillaume
"""
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from brian2 import *

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

# Simulation Neuronale avec Brian2
def run_neuron_simulation():
    start_scope()  # Initialisation de Brian2 pour un nouveau scope de simulation

    tau = 10*ms  # Constante de temps
    eqs = '''
    dv/dt = (1-v)/tau : 1
    '''  # Équations différentielles décrivant le modèle du neurone

    G = NeuronGroup(1, eqs, threshold='v>0.8', reset='v = 0', method='exact')
    M = StateMonitor(G, 'v', record=True)  # Enregistrement de la variable 'v'
    run(50*ms)  # Durée de la simulation

    return M.t/ms, M.v[0]  # Retourne le temps en ms et la tension membranaire

# Onglet pour l'oscilloscope
tab1 = QWidget()
tab_widget.addTab(tab1, "Oscilloscope")
tab1.layout = QVBoxLayout()
tab1.setLayout(tab1.layout)
plot_widget = pg.PlotWidget()
tab1.layout.addWidget(plot_widget)

time, voltage = run_neuron_simulation()  # Exécution de la simulation neuronale
plot_widget.plot(time, voltage)  # Affichage du résultat de la simulation

# Ajout des labels
plot_widget.setLabel('left', 'Membrane potential v')
plot_widget.setLabel('bottom', 'Time (ms)')

# Ajout d'un quadrillage
plot_widget.showGrid(x=True, y=True, alpha=0.3)  # Affiche la grille sur les axes X et Y avec une transparence de 30%

# Onglet pour les Spikes (vous pouvez étendre avec votre propre code)
tab2 = QWidget()
tab_widget.addTab(tab2, "Spikes")

# Affichage de la fenêtre
window.show()
app.exec_()
