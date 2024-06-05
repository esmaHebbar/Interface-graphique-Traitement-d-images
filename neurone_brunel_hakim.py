# -*- coding: utf-8 -*-
"""
Créé le Wed Jun  5 10:29:16 2024
Auteurs: Esma et Guillaume
"""

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from brian2 import *

# Configuration de l'apparence de pyqtgraph
pg.setConfigOption('background', 'w')  # Fond blanc

# Création de l'application et de la fenêtre principale
app = QApplication([])
window = QMainWindow()
window.setWindowTitle('Interface graphique modulaire - Oscilloscope')

# Configuration des onglets de la fenêtre principale
tab_widget = QTabWidget()
window.setCentralWidget(tab_widget)

# Paramètres du modèle neuronal
N = 1  # Nombre de neurones
Vr = 10*mV  # Potentiel de repos
theta = 20*mV  # Seuil de décharge
tau = 20*ms  # Constante de temps
delta = 2*ms  # Délai de la synapse
taurefr = 2*ms  # Temps réfractaire
duration = 0.1*second  # Durée de la simulation
C = 1000  # Nombre de connexions
sparseness = float(C)/N  # Densité de connexion
J = 0.1*mV  # Amplitude du potentiel post-synaptique
muext = 25*mV  # Potentiel moyen externe
sigmaext = 1*mV  # Variabilité du bruit externe

# Fonction de simulation neuronale
def run_neuron_simulation():
    start_scope()
    
    eqs = """
    dv/dt = (-v + muext + sigmaext * sqrt(tau) * xi) / tau : volt
    """
    
    G = NeuronGroup(N, eqs, threshold='v > theta', reset='v = Vr', refractory=taurefr, method='euler')
    G.v = Vr  # Initialisation de la variable 'v'
    
    M = StateMonitor(G, 'v', record=True)
    Sp = SpikeMonitor(G)
    
    conn = Synapses(G, G, on_pre='v += -J', delay=delta)
    conn.connect(p=sparseness)
    
    LFP = PopulationRateMonitor(G)
    
    run(duration)
    
    spike_times = Sp.t/ms if len(Sp.t) > 0 else np.array([])  # Temps des spikes
    
    return M.t/ms, M.v[0], spike_times  # Temps en ms, tension membranaire, et temps des spikes

# Configuration des onglets
tab1 = QWidget()
tab_widget.addTab(tab1, "Oscilloscope")
tab1.layout = QVBoxLayout()
tab1.setLayout(tab1.layout)

plot_widget = pg.PlotWidget()
tab1.layout.addWidget(plot_widget)
plot_widget.setTitle("Matrice d'oscilloscope")
time, voltage, spikes = run_neuron_simulation()
plot_widget.plot(time, voltage, pen='b')

plot_widget.setXRange(0, max(time) if len(time) > 0 else 50)
plot_widget.setLabel('left', 'Potentiel membranaire v')
plot_widget.setLabel('bottom', 'Temps (ms)')
plot_widget.showGrid(x=True, y=True, alpha=0.2)

# Configuration et ajout d'étiquettes aux axes du scatter plot
scatter_widget = pg.PlotWidget()  # Correct instantiation of PlotWidget
tab1.layout.addWidget(scatter_widget)
scatter_widget.setTitle("Scatter Plot des Spikes")
scatter_widget.setXRange(0, max(time) if len(time) > 0 else 50)
scatter_widget.setLabel('left', 'Spikes')  # Correct method to set the y-axis label
scatter_widget.setLabel('bottom', 'Temps (ms)')  # Correct method to set the x-axis label
if len(spikes) > 0:
    scatter_widget.plot(spikes, np.ones_like(spikes) * 1, pen=None, symbol='o', symbolSize=5, symbolBrush='r')

tab2 = QWidget()
tab_widget.addTab(tab2, "Spikes")

window.show()
app.exec_()
