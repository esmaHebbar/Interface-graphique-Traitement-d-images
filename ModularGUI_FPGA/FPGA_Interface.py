from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QTimer
import zmq
import pyqtgraph as pg
import numpy as np
from config import *
from filter import butter_bandpass_filter

class Interface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Interface graphique')
        self.timer_interval = 100  # maj 100 ms
        self.setup_ui()

    def setup_ui(self):
        ### Fenêtre principale ###
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        ### zone pour les boutons ###
        self.main_widget.setLayout(self.layout)
        self.btn_layout = QHBoxLayout()

        ### Zone de texte pour l'adresse ###
        self.address_input = QLineEdit("tcp://192.168.137.128:5557")
        self.layout.addWidget(self.address_input)
        
        ### Bouton connexion ###
        self.listen_button = QPushButton('Connect')
        self.listen_button.clicked.connect(self.start_listening)
        self.btn_layout.addWidget(self.listen_button)

        ### Bouton déconnexion ###
        self.stop_listen_button = QPushButton('Disconnect')
        self.stop_listen_button.clicked.connect(self.stop_listening)
        self.btn_layout.addWidget(self.stop_listen_button)

        ### Ajout du layout des boutons au layout principal ###
        self.layout.addLayout(self.btn_layout)

        ### Scatter Plot ###
        pg.setConfigOption('background', 'w')
        self.plot_widget1 = pg.PlotWidget()  
        self.layout.addWidget(self.plot_widget1) 
        self.scatter = pg.ScatterPlotItem(size=3, pen=pg.mkPen(width=3, color='k'))
        self.plot_widget1.addItem(self.scatter) 
        self.plot_widget1.setTitle("Moments de décharges",color="k")
        self.plot_widget1.setLabel('left', 'Indice du neurone')
        self.plot_widget1.setLabel('bottom', 'Temps (ms)')
        self.plot_widget1.showGrid(x=True, y=True, alpha=0.3)

        ### Sum Plot ###
        pg.setConfigOption('background', 'w')
        self.plot_widget2 = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget2)
        self.plot_widget2.setTitle("Nombre de décharges (intervalle = 100ms)",color="k")
        self.plot_widget2.setLabel('left', 'Nombre de décharges')
        self.plot_widget2.setLabel('bottom', 'Temps (ms)')
        self.curve_total_spikes = self.plot_widget2.plot(pen='b', name="Total Spikes")

        ### Signal Plot ###
        pg.setConfigOption('background', 'w')
        self.plot_widget3 = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget3)
        self.plot_widget3.setTitle("Filtrage du signal",color="k")
        self.plot_widget3.setLabel('left', 'Fréquence (Hz)')
        self.plot_widget3.setLabel('bottom', 'Temps (ms)')
        self.curve_filtered_spikes = self.plot_widget3.plot(pen='r', name="Filtered Spikes")

        ### Initialisation de ZeroMQ ###
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)

        ### Initialiser le QTimer ###
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scatter)

        ### variables pour les res ###
        self.mfr= np.zeros(NB_NRN)
        self.timestamps = []
        self.total_spikes = []
        self.interval=[0,99]

    def start_listening(self):
        ### Démarrer le timer pour vérifier les messages ###
        address = self.address_input.text()
        self.socket.connect(address)
        self.timer.start(self.timer_interval)

    def stop_listening(self):
        ### stop la socket ###
        self.socket.close()

    def update_scatter(self):
        try :     
            ### Variables pour stocker les résultats ###
            x = []
            y = []

            ### Réception des données ###
            spk_tab = self.socket.recv(flags=zmq.NOBLOCK)
            for z in range(NB_FRAME_PER_BUFFER):
                nid=0
                tstamp = int.from_bytes(spk_tab[ (z*SIZE_BYTE_FRAME + 0)
                                            : (z*SIZE_BYTE_FRAME + DATAWIDTH_BYTE_FRAME)], 
                                            "little")

                for i in range(NB_SPK_DATA_PER_FRAME):
                    reg = int.from_bytes(spk_tab[ z*(SIZE_BYTE_FRAME) + (i+1)*DATAWIDTH_BYTE_FRAME + 0
                                                : z*(SIZE_BYTE_FRAME) + (i+1)*DATAWIDTH_BYTE_FRAME + DATAWIDTH_BYTE_FRAME], 
                                                "little")
                    for k in range(DATAWIDTH_BIT_FRAME):
                        if reg & (1<<k) != 0:
                            x.append(tstamp)
                            y.append(nid)
                        nid += 1

            ### MAJ des graphes ###
            self.scatter.addPoints(x, y)
            self.update_plot(x)
        except:
            pass

    def update_plot(self, x):

        if len(x) == 0:  # Vérifie si la liste x est vide
            return
        res = 0  
        for valeur in x:
            if valeur == 0:
                continue  
            while not (self.interval[0] <= valeur <= self.interval[1]):
                self.interval[0] += 100
                self.interval[1] += 100
            res += 1
        
        self.timestamps.append(self.interval[0])
        self.total_spikes.append(res)

        filtered_x = butter_bandpass_filter(self.total_spikes, 8, 12, 256.0, order=6) 

        self.curve_total_spikes.setData(self.timestamps, self.total_spikes)
        self.curve_filtered_spikes.setData(self.timestamps, filtered_x)

if __name__ == '__main__':
    app = QApplication([])
    window = Interface()
    window.show()
    app.exec()