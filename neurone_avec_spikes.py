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

defaultclock.dt = 0.01*ms

nb_neuron=50

# Paramètres du modèle de Hodgkin-Huxley
Cm = 1.0*ufarad
El = 0*mV
ENa = 120.0*mV
EK = -12.0*mV
gl0 = 0.3*msiemens
gNa0 = 120.0*msiemens
gK0 = 36.0*msiemens

# Équations différentielles pour le modèle de Hodgkin-Huxley
eqs = '''
dv/dt = (I - gl * (v-El) - gNa * m**3 * h * (v-ENa) - gK * n**4 * (v-EK))/Cm : volt
I : amp (constant)  # Courant appliqué

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

# Créer un groupe de neurones avec les équations définies
HH = NeuronGroup(nb_neuron, eqs, threshold='v>20*mV', refractory=3*ms, method='rk4')

# Initialisation des variables
HH.v = El
HH.h = 0.75
HH.m = 0.15
HH.n = 0.35

HH.gNa = gNa0
HH.gK = gK0
HH.gl = gl0

# Enregistrer les variables d'état et les spikes
statemon = StateMonitor(HH, True, record=True)
I_monitor = StateMonitor(HH, 'I', record=True)
spikemon = SpikeMonitor(HH)

# Créer explicitement un objet Network et y ajouter les objets de simulation
net = Network(HH, statemon, spikemon, I_monitor)  # Ajout de I_monitor au réseau

# Simulation avec différents courants appliqués
HH.I = 0.0*uA
net.run(50*ms, report='text')

# Définir des courants aléatoires proches de 60 µA pour chaque neurone
HH.I = np.random.normal(60, 15, nb_neuron) * uA
net.run(50*ms, report='text')

HH.I = 0.0*uA
net.run(50*ms, report='text')

# Onglet pour l'oscilloscope
tab1 = QWidget()
tab_widget.addTab(tab1, "Oscilloscope")
tab1.layout = QVBoxLayout()
tab1.setLayout(tab1.layout)
plot1_widget = pg.PlotWidget()
tab1.layout.addWidget(plot1_widget)
# Affichage du résultat de la simulation
plot1_widget.plot(statemon.t/ms, statemon.v[0], pen='k')
# Ajout des labels
plot1_widget.setLabel('left', 'Membrane potential (V)')
plot1_widget.setLabel('bottom', 'Time (ms)')

plot3_widget = pg.PlotWidget()
tab1.layout.addWidget(plot3_widget)
# Affichage du résultat de la stimulation
#plot3_widget.plot(statemon.t/ms, statemon.I[0]/uA, label='Applied Current', pen='r')
for i in range(nb_neuron):
    plot3_widget.plot(I_monitor.t/ms, I_monitor.I[i]/uA, pen=(i, nb_neuron))
# Ajout des labels
plot3_widget.setLabel('left', 'Currents (uA)')
plot3_widget.setLabel('bottom', 'Time (ms)')

# Ajout d'un quadrillage
plot1_widget.showGrid(x=True, y=True, alpha=0.3)  # Affiche la grille sur les axes X et Y avec une transparence de 30%

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

# Affichage de la fenêtre
window.show()
app.exec_()
