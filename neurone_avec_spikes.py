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
C = 1000
sparseness = float(C)/N
J = .1*mV
muext = 25*mV
sigmaext = 1*mV

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

# Premier onglet :
    
tab1 = QWidget() # cration d'un widget pour le premier onglet
tab_widget.addTab(tab1, "Oscilloscope")# ajout de l'onglet à la barre d'onglets
tab1.layout = QVBoxLayout() # création et définition d'une disposition verticale pour l'onglet
tab1.setLayout(tab1.layout)

#Premier widget :
plot_widget = pg.PlotWidget()# Crée un widget de tracé pour l'oscilloscope
tab1.layout.addWidget(plot_widget) # Ajoute le widget de tracé à l'onglet 1 (tab1)

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

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

#Second onglet :
    
tab2 = QWidget()
tab_widget.addTab(tab2, "Spikes")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

window.show() # Affiche la fenêtre principale
app.exec_()# Démarre la boucle principale de l'application
