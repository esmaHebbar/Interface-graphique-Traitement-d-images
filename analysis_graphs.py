# -*- coding: utf-8 -*-
"""
Created on Jun 2024

@authors : Demets Guillaume & Hebbar Esma
"""
from brian2 import *



def Calculate_mfr(nb_neuron,spikemon):
    # Convert spike times to milliseconds
    spike_times_ms = spikemon.t / ms

    # Define duration and result arrays
    duree = range(0, 151, 1)
    res = [0] * len(duree)

    # Iterate over time bins
    for i, time_bin in enumerate(duree):
        count = 0
        for spike_time in spike_times_ms:
            if time_bin <= spike_time < time_bin + 1:
                count += 1
        res[i] = count
    if count > 0:
        res[i] = count / 1.0  # Divide count by bin width (1 ms) to get rate in Hz
    else:
        res[i] = 0  # No spikes in this time bin

    return duree, res



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
        


