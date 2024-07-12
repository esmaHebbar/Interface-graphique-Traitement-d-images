# Interfaces graphiques et traitement d'images pour réseaux de neurones

## Vue d'ensemble

Ces travaux ont été réalisés dans le cadre d'un stage de première année à l'ENSC par Guillaume Demets et Esma Hebbar. Notre stage s'est déroulé à l'IMS, sous la supervision de Monsieur Timothée Levi. Le premier sujet de notre stage était de développer une interface graphique permettant de représenter l'activité neuronale et de fournir des graphiques d'analyses, d'abord à partir de Brian2 (répertoire ModularGUI_Brian2), puis à partir d'une carte FPGA (répertoire ModularGUI_FPGA). Le second consistait à implémenter un traitement d'image permettant de détecter les zones d'activation d'un réseau neuronal (répertoire ImageProcessing).

## Structure du répertoire

Voici la structure du répertoire :

```
├── README.md
├── ImageProcessing
│   ├── image_processing.py
│   ├── data_image.xlsx
│   └── README.md
├── ModularGUI_Brian2
│   ├── analysis_graphs.py
│   ├── neural_network_interface.py
│   ├── simulate_hh.py
│   └── README.md
└── ModularGUI_FPGA
    ├── config.py
    ├── filter.py
    ├── FPGA_Interface.py
    └── README.md
```

### Détails des répertoires

- **ImageProcessing** : Ce répertoire contient le code visant à détecter les zones d'activation d'un réseau neuronal (sujet 2). 
  - `image_processing.py` : Script principal.
  - `data_image.xlsx` : Exemple de données d'image.
  - [Lien vers le README](./ImageProcessing/README.md)

- **ModularGUI_Brian2** : Ce répertoire contient les scripts relatifs à l'interface graphique pour la simulation neuronale utilisant Brian2 (sujet 1 - première partie).
  - `analysis_graphs.py` : Génère des graphiques d'analyses de l'activité neuronale.
  - `neural_network_interface.py` : Interface graphique.
  - `simulate_hh.py` : Simulation du modèle de Hodgkin-Huxley.
  - [Lien vers le README](./ModularGUI_Brian2/README.md)

- **ModularGUI_FPGA** : Ce répertoire contient les scripts pour l'interface graphique utilisant une carte FPGA pour les simulations neuronales (sujet 1 - seconde partie).
  - `config.py` : Script de configuration pour l'interface FPGA.
  - `filter.py` : Script pour les filtres appliqués aux signaux neuronaux.
  - `FPGA_Interface.py` : Interface graphique.
  - [Lien vers le README](./ModularGUI_FPGA/README.md)

## Installation

Pour installer les dépendances nécessaires, vous pouvez utiliser le fichier `requirements.txt` fourni avec ce projet :

```bash
pip install -r requirements.txt
```

## Contacts

- Guillaume Demets : gdemets@ensc.fr
- Esma Hebbar : ehebbar001@ensc.fr

Merci de votre intérêt pour nos travaux !
