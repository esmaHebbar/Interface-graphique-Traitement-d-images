from brian2 import *
import matplotlib.pyplot as plt

# Définir la taille du pas de temps pour le solveur d'équations différentielles
defaultclock.dt = 0.01*ms

# Paramètres du modèle de Hodgkin-Huxley
Cm = 1.0*ufarad
El = 10.6*mV
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
HH = NeuronGroup(1, eqs, threshold='v>-20*mV', reset='v=El', refractory=5*ms,method='rk4')

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

# Traçage des résultats
plt.figure()
plt.subplot(2, 1, 1)
plt.plot(statemon.t/ms, statemon.v[0])
plt.xlabel('Time (ms)')
plt.ylabel('V')

plt.subplot(2, 1, 2)
plt.plot(statemon.t/ms, statemon.I[0]/uA, label='Applied Current')
plt.xlabel('Time (ms)')
plt.ylabel('Current (uA)')
plt.legend()
plt.show()

plt.figure()
plt.plot(spikemon.t/ms, spikemon.i, '.k')
plt.xlabel('Time (ms)')
plt.ylabel('Neuron index')
plt.show()