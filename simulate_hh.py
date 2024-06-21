"""
Created on Jun 2024

@authors : Demets Guillaume & Hebbar Esma

"""

import numpy as np
from brian2 import *

def Simulate_hh():
    defaultclock.dt = 0.01*ms
    
    # Number of neurons in the group
    nb_neuron = 100
    
    # Hodgkin-Huxley model parameters
    Cm = 1.0*ufarad # Membrane capacitance
    
    El = 0*mV # Leakage reversal potential
    ENa = 120.0*mV # Sodium reversal potential
    EK = -12.0*mV # Potassium reversal potential
    
    gl0 = 0.3*msiemens # Leakage conductance
    gNa0 = 120.0*msiemens  # Sodium conductance
    gK0 = 36.0*msiemens # Potassium conductance
    
    # Differential equations for the Hodgkin-Huxley model
    eqs = '''
    dv/dt = (I+I_noise - gl * (v-El) - gNa * m**3 * h * (v-ENa) - gK * n**4 * (v-EK))/Cm : volt
    I : amp (constant)  # Applied current
    
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
    
    # Create a group of neurons with the defined equations
    HH = NeuronGroup(nb_neuron, eqs, threshold='v>20*mV', refractory=3*ms, method='rk4')
    
    # Initialization of variables
    HH.v = El
    HH.h = 0.75
    HH.m = 0.15
    HH.n = 0.35
    
    HH.gNa = gNa0
    HH.gK = gK0
    HH.gl = gl0
    
    # Add random noise to the current
    I_noise = np.random.normal(0.1, 0.1)*uA 
    S = Synapses(HH, HH, on_pre='v_post += 0.2*mV')
    S.connect(p=0.015, condition='i != j')
    
    # Record state variables and spikes
    statemon = StateMonitor(HH, True, record=True)
    I_monitor = StateMonitor(HH, 'I', record=True)
    spikemon = SpikeMonitor(HH)
    
    # Create a Network object and add simulation objects to it
    net = Network(HH, statemon, spikemon, I_monitor)
    
    # Simulation with different applied currents
    HH.I = 0.0*uA
    net.run(10*ms, report='text')
    
    HH.I = np.random.normal(60, 1.5, nb_neuron) * uA
    #HH.I = 60 * uA

    net.run(50*ms, report='text')
    
    HH.I = 0.0*uA
    net.run(10*ms, report='text')
    
    # Returns the number of neurons, the monitors, and the synapses
    return nb_neuron, statemon, I_monitor, spikemon, S

