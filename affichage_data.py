import zmq
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog
from PyQt5.QtCore import pyqtSignal

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Configure ZeroMQ context and socket
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.connect("tcp://127.0.0.1:5555")

        # Window creation 
        self.plot_graph = pg.PlotWidget()
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground("w")
        pen = pg.mkPen(color=(255, 0, 0))
        self.plot_graph.setTitle("Temperature vs Time", color="b", size="20pt")
        styles = {"color": "red", "font-size": "18px"}
        self.plot_graph.setLabel("left", "Temperature (°C)", **styles)
        self.plot_graph.setLabel("bottom", "Time (min)", **styles)
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.setYRange(20, 40)
        self.time = list(range(10))
        self.temperature = [0] * 10  # Initialize with zeroes or any default value
        # Get a line reference
        self.line = self.plot_graph.plot(
            self.time,
            self.temperature,
            name="Temperature Sensor",
            pen=pen,
            symbol="+",
            symbolSize=15,
            symbolBrush="b",
        )
        # Add a timer to update the plot with new data
        self.timer = QtCore.QTimer()
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        try:
            # Receive new temperature data from the generator
            message = self.socket.recv_json(flags=zmq.NOBLOCK)
            new_temperature = message["temperature"]
            # Update the plot data
            self.time = self.time[1:] + [self.time[-1] + 1]
            self.temperature = self.temperature[1:] + [new_temperature]
            self.line.setData(self.time, self.temperature)
        except zmq.Again:
            # No new data received, just return
            return

app = QtWidgets.QApplication([])
main = MainWindow()
main.setWindowTitle('Modular Graphical Interface')
tab_widget = QTabWidget()
main.setCentralWidget(tab_widget)
main.show()
app.exec()