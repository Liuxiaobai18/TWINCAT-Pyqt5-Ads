# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import pyads
from matplotlib import animation

plc = pyads.Connection("192.168.0.9.1.1", 851)
plc.open()

X_axis_points = 3000 #图像中绘制的点数

def shujuhuoqu():
    i = plc.read_by_name("GVL.ch7")  #读取TWINCAT中全局变量GVL中的ch7变量
    return i


# 创建一个Tkinter窗口
root = tk.Tk()
root.title("Data analysis7")


# 设置窗口不可调节
root.resizable(False, False)

# 创建一个Figure对象，用于绘制折线图

fig = Figure(figsize=(4, 4), dpi=100)
ax = fig.add_subplot(111)
ax.set_xlim(0, X_axis_points)
ax.set_ylim(auto=True)
(line,) = ax.plot([], [])


# 创建一个队列用于存储原始数据
data_queue = []

# 创建一个变量来存储最大值和最小值
max_value = None
min_value = None


# 创建一个变量来存储实时值
current_value = None

# 创建一个函数来初始化折线图
def init_line():
    line.set_data([], [])
    return (line,)

# 创建一个函数来更新折线图
def update_line(frame):
    global max_value, min_value, current_value

    new_data_point = shujuhuoqu()

    if len(data_queue) > X_axis_points:
        data_queue.pop(0)


    if max_value is None or new_data_point > max_value:
        max_value = new_data_point
    if min_value is None or new_data_point < min_value:
        min_value = new_data_point

    x_data = np.linspace(0, len(data_queue) - 1, X_axis_points)
    interp = interp1d(np.arange(len(data_queue)), data_queue, kind="linear")
    y_data = interp(x_data)
    line.set_data(x_data, y_data)

    ax.relim()
    ax.autoscale_view()

    max_min_text.set(f"最大值: {max_value:.2f}, 最小值: {min_value:.2f}")

    current_value = new_data_point
    current_value_text.set(f"当前值: {current_value:.2f}")
    return (line,)



# 创建一个Matplotlib画布并将其嵌入到Tkinter窗口中
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()

# 创建一个文本标签用于显示最大值和最小值
max_min_text = tk.StringVar()
max_min_label = ttk.Label(root, textvariable=max_min_text, anchor="se")
max_min_label.pack(side="right")


# 创建一个文本标签用于显示实时值
current_value_text = tk.StringVar()
current_value_label = ttk.Label(root, textvariable=current_value_text, anchor="se")
current_value_label.pack(side="right")

# 创建一个动画对象
ani = animation.FuncAnimation(
    fig,
    update_line,
    init_func=init_line,
    blit=True,
    interval=1,
    cache_frame_data=False,
)

# 创建一个函数，用于重新执行代码
def rester():
    global max_value, min_value, current_value, data_queue
    plc.open()
    max_value = None
    min_value = None
    current_value = None
    data_queue = []

# 创建"rester"按钮
rester_button = ttk.Button(root, text="复位", command=rester)
rester_button.pack(side="left")

# 运行Tkinter主循环
root.mainloop()

                                



