"""
Created on Fri Jun 14 09:46:49 2024

@authors: esma and guillaume
"""

import numpy as np
from brian2 import *
import matplotlib.pyplot as plt


def Calculer_synapses():
    defaultclock.dt = 0.01*ms
    
    # Number of neurons in the group
    nb_neuron_s=5
    
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
    
    # Create a group of neurons with the defined equations
    HH = NeuronGroup(nb_neuron, eqs, threshold='v>20*mV', refractory=3*ms, method='rk4')
    
    P = NeuronGroup(nb_neuron, eqs, threshold='v>20*mV', refractory=3*ms, method='rk4')
    Q = NeuronGroup(nb_neuron, eqs, threshold='v>20*mV', refractory=3*ms, method='rk4')
    
    P.I = [2, 0]
    P.tau = [10, 100]*ms
    Q.I = [2, 0]
    Q.tau = [10, 100]*ms

    
    w = 1*mV
    S = Synapses(P, Q, on_pre='v += w')# does not create synapses, it only specifies their dynamics
    #S = Synapses(P, Q, model='w : volt', on_pre='v += w')

    # Initialization of variables
    HH.v = El
    HH.h = 0.75
    HH.m = 0.15
    HH.n = 0.35
    
    HH.gNa = gNa0
    HH.gK = gK0
    HH.gl = gl0
    
    # Add random noise to the current
    I_noise=np.random.normal(0.1,0.1)*uA 
    
    # Record state variables and spikes
    statemon_s = StateMonitor(HH, True, record=True)
    I_monitor_s = StateMonitor(HH, 'I', record=True)
    spikemon_s = SpikeMonitor(HH)
    
    # Create a Network object and add simulation objects to it
    net = Network(HH, statemon, spikemon, I_monitor)
    
    # 1-to-1 connection :
    S.connect(j='i')
    #creates a synapse between neuron 5 in the source group and neuron 10 in the target group :
    #S.connect(i=5, j=10)
#   S.connect() #connects all neuron pairs.
#   S.connect(i=[1, 2], j=[3, 4])#synapses between neurons 1 and 3, and between neurons 2 and 4
#   S.connect(i=numpy.arange(10), j=1)#synapses between the first ten neurons in the source group and neuron 1 in the target group
    

    # Simulation with different applied currents
    HH.I = 0.0*uA
    net.run(500*ms, report='text')
    
    HH.I = np.random.normal(60, 5, nb_neuron) * uA
    net.run(500*ms, report='text')
    
    HH.I = 0.0*uA
    net.run(500*ms, report='text')
    
    # Returns the number of neurons and the monitors
    return nb_neuron_s, statemon_s, I_monitor_s, spikemon_s


