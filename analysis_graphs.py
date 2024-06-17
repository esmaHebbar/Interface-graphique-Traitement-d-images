# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 14:52:33 2024

@author: Guillaume
"""
import matplotlib.pyplot as plt
from brian2 import *
from HH_model import Calculer

# Appeler la fonction pour obtenir les données
nb_neuron, statemon, I_monitor, spikemon,S = Calculer()

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

# Création de l'histogramme
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(labels, hist_data, width=0.8, color='blue', label='Histogramme des Spikes')

# Ajout de la courbe qui suit l'histogramme
ax.plot(labels, hist_data, color='red', linestyle='-', label='Courbe des Spikes')

# Configuration des axes et du titre
ax.set_xlabel('Intervalles de Temps (ms)')
ax.set_ylabel('Nombre de Spikes par Neurone')
ax.set_title('Histogramme et Courbe des Spikes par Intervalle de Temps')
ax.grid(axis='y')

# Masquer les labels des ticks de l'axe des x
ax.set_xticklabels([])

plt.tight_layout()

# Ajout de la légende
ax.legend()

# Affichage du graphique
plt.show()

