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

data = { 'Cm' : 200/10**12,
'gl' : 10/10**12,
'u_rest' : -60, #El
'th_rh' : -50, #Vt
'Dt' : 2,
'tau_a' : 200,#tau_w
'Va' : -50,
'Da' : 5,
'ga_max' : 10/10**12,#ga_bar
'Ea' : -70,
'Is' : 200/10**12,
'th' : -40, # threshold - seuil
'u_reset' : -55,#Vr
'b':1/10**12, #Dga 
'R': 5*10**9,
'step':0/10**12
}

# Simulation Neuronale avec Brian2

N = 5000
Vr = 10*mV
theta = 20*mV
tau = 20*ms
delta = 2*ms
taurefr = 2*ms
duration = .1*second
C = 1000
sparseness = float(C)/N
J = .1*mV
muext = 25*mV
sigmaext = 1*mV

eqs = """
dV/dt = (-V+muext + sigmaext * sqrt(tau) * xi)/tau : volt
"""

group = NeuronGroup(N, eqs, threshold='V>theta',
                    reset='V=Vr', refractory=taurefr, method='euler')
group.V = Vr
conn = Synapses(group, group, on_pre='V += -J', delay=delta)
conn.connect(p=sparseness)
M = SpikeMonitor(group)
LFP = PopulationRateMonitor(group)

run(duration)

subplot(211)
plot(M.t/ms, M.i, '.')
xlim(0, duration/ms)

subplot(212)
plot(LFP.t/ms, LFP.smooth_rate(window='flat', width=0.5*ms)/Hz)
xlim(0, duration/ms)

show()

# # Onglet pour l'oscilloscope
# tab1 = QWidget()
# tab_widget.addTab(tab1, "Oscilloscope")
# tab1.layout = QVBoxLayout()
# tab1.setLayout(tab1.layout)
# plot1_widget = pg.PlotWidget()
# tab1.layout.addWidget(plot1_widget)

# plot1_widget.plot(LFP.t/ms, LFP.smooth_rate(window='flat', width=0.5*ms)/Hz,pen='k')  # Affichage du résultat de la simulation
# #plot1_widget.plot(G.v0, M.count, pen='k')  # Affichage du résultat de la simulation

# # Ajout des labels
# plot1_widget.setLabel('left', 'Membrane potential (mV)')
# plot1_widget.setLabel('bottom', 'Time (ms)')

# # Ajout d'un quadrillage
# plot1_widget.showGrid(x=True, y=True, alpha=0.3)  # Affiche la grille sur les axes X et Y avec une transparence de 30%

# # Onglet pour les Spikes
# tab2 = QWidget()
# tab_widget.addTab(tab2, "Spikes")
# tab2.layout = QVBoxLayout()
# tab2.setLayout(tab2.layout)
# plot2_widget = pg.PlotWidget()
# tab2.layout.addWidget(plot2_widget)

# # Affichage des spikes
# plot2_widget.plot(M.t/ms, M.i, pen='.b')

# # Ajout des labels pour le graphique des spikes
# plot2_widget.setLabel('left', 'Neuron index')
# plot2_widget.setLabel('bottom', 'Time (ms)')

# # Affichage de la fenêtre
# window.show()
# app.exec_()
