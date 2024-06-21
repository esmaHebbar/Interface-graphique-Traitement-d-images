import zmq
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Configure ZeroMQ context and socket
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.connect("tcp://127.0.0.1:5555")

        # Set up the main layout with tabs
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # First tab: Oscilloscope
        self.widget1 = QWidget()
        self.widget1.layout = QVBoxLayout(self.widget1)
        self.tab_widget.addTab(self.widget1, "Oscilloscope")

        # First graph: membrane potential as a function of time
        self.oscilloscope_plot = pg.PlotWidget()
        self.widget1.layout.addWidget(self.oscilloscope_plot)

        # Oscilloscope graph settings
        self.oscilloscope_plot.setBackground("w")
        oscilloscope_pen = pg.mkPen(color=(0, 0, 255))
        self.oscilloscope_plot.setTitle("Membrane Potential vs Time", color="b", size="20pt")
        oscilloscope_styles = {"color": "blue", "font-size": "18px"}
        self.oscilloscope_plot.setLabel("left", "Membrane Potential (mV)", **oscilloscope_styles)
        self.oscilloscope_plot.setLabel("bottom", "Time (ms)", **oscilloscope_styles)
        self.oscilloscope_plot.addLegend()
        self.oscilloscope_plot.showGrid(x=True, y=True)
        self.oscilloscope_time = list(range(10))
        self.oscilloscope_data = [0] * 10  # Initialize with zeroes or any default value
        # Get a line reference for the oscilloscope
        self.oscilloscope_line = self.oscilloscope_plot.plot(
            self.oscilloscope_time,
            self.oscilloscope_data,
            name="Membrane Potential",
            pen=oscilloscope_pen,
            symbol="o",
            symbolSize=10,
            symbolBrush="b",
        )

        # Second tab: Raster plot
        self.widget2 = QWidget()
        self.widget2.layout = QVBoxLayout(self.widget2)
        self.tab_widget.addTab(self.widget2, "Raster Plot")

        # Raster plot: neural activity
        self.raster_plot = pg.PlotWidget()
        self.widget2.layout.addWidget(self.raster_plot)

        # Raster plot settings
        self.raster_plot.setBackground("w")
        raster_pen = pg.mkPen(color=(255, 0, 0))
        self.raster_plot.setTitle("Neural Activity Raster Plot", color="r", size="20pt")
        raster_styles = {"color": "red", "font-size": "18px"}
        self.raster_plot.setLabel("left", "Neuron Index", **raster_styles)
        self.raster_plot.setLabel("bottom", "Time (ms)", **raster_styles)
        self.raster_plot.addLegend()
        self.raster_plot.showGrid(x=True, y=True)
        self.raster_time = list(range(10))
        self.raster_data = [0] * 10  # Initialize with zeroes or any default value
        # Get a line reference for the raster plot
        self.raster_line = self.raster_plot.plot(
            self.raster_time,
            self.raster_data,
            name="Neural Activity",
            pen=raster_pen,
            symbol="+",
            symbolSize=15,
            symbolBrush="r",
        )

        # Add a timer to update the plots with new data
        self.timer = QtCore.QTimer()
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        try:
            # Receive new data from the generator
            message = self.socket.recv_json(flags=zmq.NOBLOCK)
            new_temperature = message["temperature"]
            # Update the oscilloscope plot data
            self.oscilloscope_time = self.oscilloscope_time[1:] + [self.oscilloscope_time[-1] + 1]
            self.oscilloscope_data = self.oscilloscope_data[1:] + [new_temperature]
            self.oscilloscope_line.setData(self.oscilloscope_time, self.oscilloscope_data)

            # Update the raster plot data
            self.raster_time = self.raster_time[1:] + [self.raster_time[-1] + 1]
            self.raster_data = self.raster_data[1:] + [new_temperature]
            self.raster_line.setData(self.raster_time, self.raster_data)
        except zmq.Again:
            # No new data received, just return
            return

app = QtWidgets.QApplication([])
main = MainWindow()
main.setWindowTitle('Modular Graphical Interface')
main.show()
app.exec()
