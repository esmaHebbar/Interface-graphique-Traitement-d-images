"""
Created on Wed Jun  5 10:29:16 2024
@authors: esma et guillaume

"""

#Importation des bibliothèques nécessaires :
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
# Importation de Brian2 (simulateur pour les réseaux de neurones à impulsions) :
from brian2 import *

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

# On met la couleur de fond de pyqtgraph (pg) en blanc
pg.setConfigOption('background', 'w') 

# Création de la fenêtre principale, et création des instances QApplication et QMainWindow
app = QApplication([])
window = QMainWindow()
window.setWindowTitle('Interface graphique modulaire - Oscilloscope')

# Configuration des onglets de la fenêtre principale
tab_widget = QTabWidget()# création d'un widget d'onglets
window.setCentralWidget(tab_widget) # définition du widget d'onglets comme widget central de la fenêtre

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
N = 5000
Vr = 10*mV
theta = 20*mV
tau = 20*ms
delta = 2*ms
taurefr = 2*ms
duration = .1*second


# Fonction de simulation neuronale
def run_neuron_simulation():
    start_scope() # initialisation d'un nouveau contexte de simulation avec Brian2

    tau = 10*ms  # constante de temps du modèle neuronal
    
    # Équations différentielles décrivant le modèle du neurone
    eqs = '''
    dv/dt = (1-v)/tau : 1
    '''  
    # Création d'un groupe de neurones :
    G = NeuronGroup(1, eqs, threshold='v>0.8', reset='v = 0', method='exact')
    
    # Surveille et enregistre la variable 'v'
    M = StateMonitor(G, 'v', record=True)  # Enregistrement de la variable 'v'
    Sp = SpikeMonitor(G)# Surveille et enregistre les moments des spikes
    
    run(50*ms)
    
    spike_times = Sp.t/ms if len(Sp.t) > 0 else np.array([])  # Renvoie les moments d'apparition des spikes en ms,  retourne un array vide si aucun spikes car sinon erreur
    
    return M.t/ms, M.v[0], spike_times  # Retourne le temps en ms, la tension membranaire, et les moments d'apparition des spikes

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

# Paramètres du modèle de Hodgkin-Huxley
Cm = 1.0*ufarad
El = 10.6*mV
ENa = 120.0*mV
EK = -12.0*mV
gl0 = 0.3*msiemens
gNa0 = 120.0*msiemens
gK0 = 36.0*msiemens

defaultclock.dt = 0.01*ms

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
HH = NeuronGroup(10, eqs, threshold='v>-20*mV', reset='v=0*mV', refractory=5*ms, method='rk4')
#reset='v=El'
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
spikemon = SpikeMonitor(HH)

# Simulation avec différents courants appliqués
HH.I = 0.0*uA
run(50*ms, report='text')
HH.I = 60.0*uA
run(50*ms, report='text')
HH.I = 0.0*uA
run(50*ms, report='text')


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

# Premier onglet :
    
tab1 = QWidget() # cration d'un widget pour le premier onglet
tab_widget.addTab(tab1, "Oscilloscope")# ajout de l'onglet à la barre d'onglets
tab1.layout = QVBoxLayout() # création et définition d'une disposition verticale pour l'onglet
tab1.setLayout(tab1.layout)

#Premier widget :
plot_widget = pg.PlotWidget()# Crée un widget de tracé pour l'oscilloscope
tab1.layout.addWidget(plot_widget) # Ajoute le widget de tracé à l'onglet 1 (tab1)

#HH :
plot1_widget = pg.PlotWidget()
tab1.layout.addWidget(plot1_widget)
plot1_widget.plot(statemon.t/ms, statemon.v[0], pen='k')  # Affichage du résultat de la simulation HH
plot1_widget.setLabel('left', 'Membrane potential (mV)')
plot1_widget.setLabel('bottom', 'Time (ms)')
plot1_widget.showGrid(x=True, y=True, alpha=0.2)
#fin HH


# Graphique du potentiel membranaire
time, voltage, spikes = run_neuron_simulation() # Lance la simulation neuronale et récupère les données
plot_widget.plot(time, voltage, pen='b') # Trace le potentiel membranaire en bleu ('b')

# Configuration des axes
plot_widget.setTitle("Matrice d'oscilloscope")
plot_widget.setXRange(0, max(time) if len(time) > 0 else 50)

plot_widget.setLabel('left', 'Potentiel membranaire v') 
plot_widget.setLabel('bottom', 'Temps (ms)') 
plot_widget.showGrid(x=True, y=True, alpha=0.2)

# Second widget :
scatter_widget = pg.PlotWidget()
tab1.layout.addWidget(scatter_widget)# Ajoute ce widget à l'onglet 1 (tab1)

# Configuration des axes
scatter_widget.setTitle("Scatter Plot des Spikes")
scatter_widget.setXRange(0, max(time) if len(time) > 0 else 50)

scatter_widget.setLabel('left', 'Spikes')
scatter_widget.setLabel('bottom', 'Temps (ms)')

if len(spikes) > 0:
    scatter_widget.plot(spikes, np.ones_like(spikes) * 1, pen=None, symbol='o', symbolSize=5, symbolBrush='r')# Trace les spikes

#spikes HH :
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

#fin spikes HH

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

#Second onglet :
    
tab2 = QWidget()
tab_widget.addTab(tab2, "Spikes")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

window.show() # Affiche la fenêtre principale
app.exec_()# Démarre la boucle principale de l'application