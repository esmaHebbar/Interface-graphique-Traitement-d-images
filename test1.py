# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 10:29:16 2024

@author: esma et guillaume
"""
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from brian2 import *

# Création de l'application et de la fenêtre principale
app = QApplication([])
window = QMainWindow()
window.setWindowTitle('Oscilloscope Modulaire')

# Création et configuration des onglets
tab_widget = QTabWidget()
window.setCentralWidget(tab_widget)

# Onglet pour l'oscilloscope
tab1 = QWidget()
tab_widget.addTab(tab1, "Oscilloscope")
tab1.layout = QVBoxLayout()
tab1.setLayout(tab1.layout)
plot_widget = pg.PlotWidget()
tab1.layout.addWidget(plot_widget)
time = list(range(1000))  # Données temporelles

#voltage = np.sin(np.linspace(0, 20, 1000))  # Signal sinusoïdal
#plot_widget.plot(time, voltage)

num_neurons = 1
duration = 2*second
# Parameters
area = 20000*umetre**2
Cm = 1*ufarad*cm**-2 * area
gl = 5e-5*siemens*cm**-2 * area
El = -65*mV
EK = -90*mV
ENa = 50*mV
g_na = 100*msiemens*cm**-2 * area
g_kd = 30*msiemens*cm**-2 * area
VT = -63*mV#équations de HH

eqs = Equations('''
dv/dt = (gl*(El-v) - g_na*(m*m*m)*h*(v-ENa) - g_kd*(n*n*n*n)*(v-EK) + I)/Cm : volt
dm/dt = 0.32*(mV**-1)*4*mV/exprel((13.*mV-v+VT)/(4*mV))/ms*(1-m)-0.28*(mV**-1)*5*mV/exprel((v-VT-40.*mV)/(5*mV))/ms*m : 1
dn/dt = 0.032*(mV**-1)*5*mV/exprel((15.*mV-v+VT)/(5*mV))/ms*(1.-n)-.5*exp((10.*mV-v+VT)/(40.*mV))/ms*n : 1
dh/dt = 0.128*exp((17.*mV-v+VT)/(18.*mV))/ms*(1.-h)-4./(1+exp((40.*mV-v+VT)/(5.*mV)))/ms*h : 1
I : amp
''')
# group = NeuronGroup(num_neurons, eqs,
#                 threshold='v > -40*mV',
#                 refractory='v > -40*mV',
#                 method='exponential_euler')

# start_scope()
# tau = 10*ms
# eqs = '''
# dv/dt = (1-v)/tau : 1
# '''
# G = NeuronGroup(1, eqs, method='exact')
# run(100*ms)
# plot(G.t/ms, G.v[0])
# xlabel('Time (ms)')
# ylabel('v');

tau = 10*ms
# eqs = '''
# dv/dt = (2-v)/tau : 1
# '''
start_scope()

G = NeuronGroup(1, eqs,threshold='v > -40*mV',
                    refractory='v > -40*mV',
                    method='exponential_euler')

statemon = StateMonitor(G, 'v', record=0)
spikemon = SpikeMonitor(G)

run(100*ms)

#plot(statemon.t/ms, statemon.v[0])
for t in spikemon.t:
    axvline(t/ms, ls='--', c='C1', lw=3)
axhline(0.7, ls=':', c='C2', lw=3)
xlabel('Time (ms)')
ylabel('v');

#plot(group.I/nA, monitor.count / duration)
plot_widget.plot(statemon.t/ms, statemon.v[0])


# Onglet pour les Spikes
tab2 = QWidget()
tab_widget.addTab(tab2, "Spikes")

# Affichage de la fenêtre
window.show()
app.exec_()


#idée : faire une fonction Brian qui prend en argument un jeu de données, et qui ressort les fenetres