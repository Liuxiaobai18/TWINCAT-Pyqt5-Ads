# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np
import pyads

plc = pyads.Connection("192.168.0.9.1.1", 851)
plc.open()

X_axis_points = 3000  # 图像中绘制的点数

def shujuhuoqu():
    i = plc.read_by_name("GVL.ch7")  # 读取TWINCAT中全局变量GVL中的ch7变量
    return i

class DataAnalysisApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.data_queue = []
        self.max_value = None
        self.min_value = None
        self.current_value = None

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.update_line)
        self.timer.start()

    def initUI(self):
        self.setWindowTitle("Data Analysis")
        self.setGeometry(100, 100, 800, 600)
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.centralWidget.setLayout(self.layout)
        
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

    def update_line(self):
        new_data_point = shujuhuoqu()
        
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
        plc.open()
        self.max_value = None
        self.min_value = None
        self.current_value = None
        self.data_queue = []

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = DataAnalysisApp()
    mainWindow.show()
    sys.exit(app.exec_())
