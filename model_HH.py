# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 10:14:08 2024

@author: Guillaume
"""

import numpy as np
from brian2 import *

def Calculer():
    defaultclock.dt = 0.01*ms
    
    nb_neuron=10
    
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
    dv/dt = (I+I_noise - gl * (v-El) - gNa * m**3 * h * (v-ENa) - gK * n**4 * (v-EK))/Cm : volt
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
    
    I_noise=np.random.normal(0.1,0.1)*uA 
    
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
    HH.I = np.random.normal(60, 5, nb_neuron) * uA
    net.run(50*ms, report='text')
    
    HH.I = 0.0*uA
    net.run(50*ms, report='text')
    
    return nb_neuron, statemon, I_monitor, spikemon



