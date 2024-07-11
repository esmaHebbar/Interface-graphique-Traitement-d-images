# -*- coding: utf-8 -*-
"""
Created on Jun 2024

@authors : Demets Guillaume & Hebbar Esma
"""
from brian2 import *
import numpy as np

def Calculate_mfr(nb_neuron,spikemon):
    # Convert spike times to milliseconds
    spike_index=spikemon.i
    index=np.arange(1,nb_neuron,1)
    res=np.zeros(nb_neuron-1)

    for i in range(nb_neuron-1):
        for j in range(len(spike_index)-1):
            if(spike_index[j]==i):
                res[i] += 1
    return index, res

def Calculate_isi(nb_neuron,spikemon):
    isi_values = [] #contenant les valeurs des intervalles interspikes
    
    for m in range (nb_neuron):
        spike_times = np.array(spikemon.t[spikemon.i == m]) / ms
        
        if len(spike_times) > 1:
            # Calcul des intervalles interspikes
            isi = np.diff(spike_times)
            isi_values.extend(isi)  # ajout de isi dans isi_values
    
    if isi_values:
        # Convertir la liste en un array numpy pour l'histogramme
        isi_values = np.array(isi_values)
        
        # Création de l'histogramme
        # y, x = np.histogram(isi_values, bins=np.linspace(0, max(isi_values)+1, num=int(max(isi_values)+1)//2 + 1))
        bins = np.logspace(np.log10(min(isi_values)), np.log10(max(isi_values)), 50)  # Utilisez une échelle logarithmique pour les bins
        y, x = np.histogram(isi_values, bins=bins)
    return x,y

def Calculate_active_neurons(nb_neuron, spikemon):
    spike_counts = [np.sum(spikemon.i == neuron_idx) for neuron_idx in range(nb_neuron)]
    simulation_time = np.max(spikemon.t/ms) - np.min(spikemon.t/ms)
    mfr = [count / simulation_time * 1000 for count in spike_counts]  # Conversion en Hz (spikes/s)
    
    active_neurons = sorted([(i, mfr[i]) for i in range(nb_neuron)], key=lambda x: x[1], reverse=True)
    
    return active_neurons
     