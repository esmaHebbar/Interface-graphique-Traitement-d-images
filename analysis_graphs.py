# -*- coding: utf-8 -*-
"""
Created on Jun 2024

@authors : Demets Guillaume & Hebbar Esma
"""
from brian2 import *

def Calculate_mfr(nb_neuron,spikemon):
    duree_totale = 150  # en ms
    taille_intervalle = 5  # en ms
    
    # Générer les intervalles successifs de 1 ms
    intervalles = [(start, start + taille_intervalle) for start in range(0, duree_totale, taille_intervalle)]
    
    # Dictionnaire pour stocker les indices pour chaque intervalle
    resultats = {}
    
    # Parcourir chaque intervalle
    for intervalle_min, intervalle_max in intervalles:
        # Récupérer les indices correspondants aux temps dans l'intervalle courant
        indices_cibles = [i for t, i in zip(spikemon.t/ms, spikemon.i) if intervalle_min <= t < intervalle_max]
        # Stocker le résultat dans le dictionnaire
        resultats[f"{intervalle_min}-{intervalle_max}"] = indices_cibles
    
    # Préparer les données pour l'histogramme
    hist_data = []
    for intervalle, indices_cibles in resultats.items():
        hist_data.append(len(indices_cibles) / nb_neuron)  # Normaliser par le nombre de neurones
    
    # Générer les labels pour les intervalles
    labels = [f"{intervalle_min}" for intervalle_min, intervalle_max in intervalles]
    if intervalles:
        labels.append(f"{intervalles[-1][1]}")  # Ajoute la limite supérieure du dernier intervalle
    
    return labels, hist_data

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
