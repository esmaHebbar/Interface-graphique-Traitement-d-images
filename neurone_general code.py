"""
Created on Thu Jun  6 11:00:36 2024
@authors: esma et guillaume

"""

#Importation des bibliothèques nécessaires :
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from brian2 import *

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

# Paramètres de la simulation
model_params = {
    'N': 5000, #nombre de neurones
    'Vr': 0*mV,  # potentiel de repos
    'theta': 20*mV,  # seuil de décharge
    'tau': 10*ms,  # constante de temps
    'delta' : 2*ms, #délai de la synapse
    'taurefr' : 2*ms, #période réfractaire
    'reset': 'v = 0',  # réinitialisation après spike
    'duration': 0.1*second,  # durée de la simulation
    
    'eqs': '''
    dv/dt = (1-v)/tau : 1
    ''' ,
    
    'method': 'exact'  # méthode de résolution de l'équation différentielle
    
}

# Fonction de simulation neuronale :
def run_neuron_simulation(params):
    start_scope()
    G = NeuronGroup(params['N'], params['eqs'], threshold='v>0.8', reset=params['reset'], refractory=params['taurefr'],method=params['method'])
    M = StateMonitor(G, 'v', record=True) 
    Sp = SpikeMonitor(G)
    run(params['duration'])
    spike_times = Sp.t/ms if len(Sp.t) > 0 else np.array([])
    
    return M.t/ms, M.v[0], spike_times

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

# On met la couleur de fond de pyqtgraph (pg) en blanc
pg.setConfigOption('background', 'w') 

# Création de la fenêtre principale, et création de l'application
app = QApplication([])
window = QMainWindow()
window.setWindowTitle('Interface graphique modulaire - Oscilloscope')

# Configuration des onglets de la fenêtre principale
tab_widget = QTabWidget()# création d'un widget d'onglets
window.setCentralWidget(tab_widget) # définition du widget d'onglets comme widget central de la fenêtre
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
time, voltage, spikes = run_neuron_simulation(model_params) # Lance la simulation neuronale et récupère les données
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
