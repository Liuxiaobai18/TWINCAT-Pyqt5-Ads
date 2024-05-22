# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np
import pyads

X_axis_points = 3000  # 图像中绘制的点数

class DataAnalysisApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.plc = None
        self.connected = False
        self.initUI()
        self.data_queue = []
        self.max_value = None
        self.min_value = None
        self.current_value = None

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.update_line)

    def initUI(self):
        self.setWindowTitle("Data Analysis")
        self.setGeometry(100, 100, 800, 600)
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)

        self.layout = QtWidgets.QVBoxLayout()
        self.centralWidget.setLayout(self.layout)

        # Input fields for IP address, port, and variable name
        self.ipInput = QtWidgets.QLineEdit(self)
        self.ipInput.setPlaceholderText("Enter IP address (e.g., 192.168.0.9.1.1)")
        self.layout.addWidget(self.ipInput)

        self.portInput = QtWidgets.QLineEdit(self)
        self.portInput.setPlaceholderText("Enter port (e.g., 851)")
        self.layout.addWidget(self.portInput)

        self.variableInput = QtWidgets.QLineEdit(self)
        self.variableInput.setPlaceholderText("Enter variable name (e.g., GVL.ch7)")
        self.layout.addWidget(self.variableInput)

        # Connect button
        self.connectButton = QtWidgets.QPushButton("连接")
        self.connectButton.clicked.connect(self.connect_to_plc)
        self.layout.addWidget(self.connectButton)

        # Plot widget
        self.plotWidget = pg.PlotWidget()
        self.layout.addWidget(self.plotWidget)
        self.plotDataItem = self.plotWidget.plot([], [])

        # Labels for max/min and current values
        self.maxMinLabel = QtWidgets.QLabel("最大值: , 最小值: ")
        self.layout.addWidget(self.maxMinLabel)
        self.currentValueLabel = QtWidgets.QLabel("当前值: ")
        self.layout.addWidget(self.currentValueLabel)

        # Reset button
        self.resetButton = QtWidgets.QPushButton("复位")
        self.resetButton.clicked.connect(self.rester)
        self.layout.addWidget(self.resetButton)

    def connect_to_plc(self):
        ip_address = self.ipInput.text()
        try:
            port = int(self.portInput.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "Port must be an integer.")
            return
        
        variable_name = self.variableInput.text()

        if not ip_address or not port or not variable_name:
            QtWidgets.QMessageBox.warning(self, "Missing Input", "Please fill in all fields.")
            return
        
        try:
            self.plc = pyads.Connection(ip_address, port)
            self.plc.open()
            self.variable_name = variable_name
            self.connected = True
            self.timer.start()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Connection Error", f"Could not connect to PLC: {e}")

    def shujuhuoqu(self):
        if self.connected:
            try:
                return self.plc.read_by_name(self.variable_name)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Read Error", f"Could not read variable: {e}")
                self.connected = False
                self.timer.stop()
        return None

    def update_line(self):
        new_data_point = self.shujuhuoqu()
        if new_data_point is None:
            return

        if len(self.data_queue) > X_axis_points:
            self.data_queue.pop(0)
        self.data_queue.append(new_data_point)

        if self.max_value is None or new_data_point > self.max_value:
            self.max_value = new_data_point
        if self.min_value is None or new_data_point < self.min_value:
            self.min_value = new_data_point

        x_data = np.linspace(0, len(self.data_queue) - 1, X_axis_points)
        y_data = np.interp(x_data, np.arange(len(self.data_queue)), self.data_queue)

        self.plotDataItem.setData(x_data, y_data)

        self.maxMinLabel.setText(f"最大值: {self.max_value:.2f}, 最小值: {self.min_value:.2f}")
        self.current_value = new_data_point
        self.currentValueLabel.setText(f"当前值: {self.current_value:.2f}")

    def rester(self):
        if self.plc:
            self.plc.close()
        self.connected = False
        self.max_value = None
        self.min_value = None
        self.current_value = None
        self.data_queue = []
        self.timer.stop()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = DataAnalysisApp()
    mainWindow.show()
    sys.exit(app.exec_())
