import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

import matplotlib.ticker as mticker
from matplotlib import colormaps
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import pyplot as plt
import matplotlib as mplot

import os
import sys

from dat_to_tempMatrix import *

import datetime

class Application(tk.Frame):
    def __init__(self, master=None):
        # Windowの初期設定を行う。
        super().__init__(master)

        self.data1 = np.zeros((480, 640))

        self.fig ,\
        self.ax, \
        self.cax, \
        self.cmap = self.figure_init()
        
        #開いているファイル名
        self.fileName = tk.StringVar()

        #保存フォルダ
        self.saveFolder = tk.StringVar()
        self.saveFolder.set(os.path.dirname(sys.executable))

        #実行ファイルの場所
        self.initFolder = tk.StringVar()
        self.initFolder.set(os.path.dirname(sys.executable))

        #フレーム作成
        headerFrame = tk.Frame(self.master)
        canvasFrame = tk.Frame(self.master)
        controlFrame = tk.Frame(self.master)
        fileFrame = tk.Frame(self.master)

        # ラベルを作成
        label1 = tk.Label(controlFrame, text="最大温度")
        label2 = tk.Label(controlFrame, text="最小温度")

        # ボタン作成
        button1 = tk.Button(controlFrame, text="描画", command=self.draw_plot)
        button2 = tk.Button(controlFrame, text="保存", command=self.save_fig)
        fileOpenButton = tk.Button(headerFrame, text='ファイルを開く')
        multiFileOpenButton = tk.Button(fileFrame, text='複数ファイルを指定して変換')
        saveFolderButton = tk.Button(fileFrame, text='保存フォルダ指定')
        
        # 初期値
        strvar1 = tk.StringVar(value='60')
        strvar2 = tk.StringVar(value='-20')

        # 値入力ボックス
        self.vmax_value = tk.Entry(controlFrame, textvariable=strvar1)
        self.vmin_value = tk.Entry(controlFrame, textvariable=strvar2)
        self.curentfilePath = tk.Entry(headerFrame,width=80, textvariable=self.fileName)
        self.savefilePath = tk.Entry(fileFrame,width=60, textvariable=self.saveFolder)

        # 配置
        headerFrame.pack(side=tk.TOP)
        canvasFrame.pack(side=tk.TOP)
        controlFrame.pack(expand=True, side=tk.LEFT,fill=tk.BOTH, padx=20, pady=10)
        fileFrame.pack(expand=True, side=tk.RIGHT, fill=tk.BOTH, padx=20, pady=10)

        self.canvas = FigureCanvasTkAgg(self.fig, canvasFrame)
        tmp = self.canvas.get_tk_widget()
        tmp.pack(side=tk.TOP, expand=True)

        self.curentfilePath.grid(row=0, column=0, columnspan=4)
        fileOpenButton.grid(row=0, column=15)

        label1.grid(row=0, column=0)
        self.vmax_value.grid(row=0, column=1)

        label2.grid(row=1, column=0,sticky="e")
        self.vmin_value.grid(row=1, column=1,sticky="e")

        button1.grid(row=2, column=0,sticky="e")
        button2.grid(row=2, column=1,sticky="e")

        self.savefilePath.grid(row=1,column=0)
        saveFolderButton.grid(row=1,column=1)

        multiFileOpenButton.grid(row=3,column=0)

        # ボタン動作
        fileOpenButton.bind('<ButtonPress>', self.on_click_file_dialog)
        multiFileOpenButton.bind('<ButtonPress>', self.on_click_multi_file_convert)
        saveFolderButton.bind('<ButtonPress>', self.on_click_dir_dialog)
        self.vmax_value.bind("<Return>", self.draw_plot)
        self.vmin_value.bind("<Return>", self.draw_plot)

        self.draw_plot()

    def on_click_file_dialog(self, event):
        fTyp = [("*SIXファイル", "*.SIX")]
        file_name = tk.filedialog.askopenfilename(filetypes=fTyp, initialdir=self.initFolder.get())
        if file_name:
            self.data1 = dat_six_to_ndarray(file_name)
            self.fileName.set(file_name)
            self.initFolder.set(os.path.dirname(file_name))
            self.draw_plot()

        return "break"
    
    def on_click_multi_file_dialog(self, event):
        fTyp = [("*SIXファイル", "*.SIX")]
        file_names = tk.filedialog.askopenfilenames(filetypes=fTyp, initialdir=self.initFolder.get())

        return file_names
    
    def on_click_dir_dialog(self, event):
        iDirPath = tk.filedialog.askdirectory(initialdir = self.saveFolder.get())
        if iDirPath:
            self.saveFolder.set(iDirPath)

        return "break"

    def multi_file_convert(self, event):
        filePaths = self.multi_file_dialog(event)
        if filePaths:
            self.convert_to_png(filePaths)

        return "break"
    
    def figure_init(self):
        fig = Figure(figsize=(8,6))
        ax = fig.add_subplot()

        #画像の向き上下反転
        ax.invert_yaxis()

        #文字サイズ調整
        plt.rcParams['font.size'] = 12

        #カラーバー調整
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="6%", pad=0)

        #カラーマップ調整
        cmap = colormaps.get_cmap("jet")
        cmap.set_under("black")
        cmap.set_over("white") 

        #グラフのラベル無効
        ax.tick_params(labelbottom=False, \
                        labelleft=False, \
                        labelright=False, \
                        labeltop=False, \
                        bottom=False, \
                        left=False,\
                        right=False, \
                        top=False
                        )
        
        return fig,ax,cax,cmap

    def convert_to_png(self, filePaths):
        vmin = float(self.vmin_value.get())
        vmax = float(self.vmax_value.get())

        fig,ax,cax,cmap = self.figure_init()
        
        for filePath in filePaths:
            data = dat_six_to_ndarray(filePath)
            heatmap = ax.imshow(data, cmap=cmap,vmin=vmin, vmax=vmax, interpolation="nearest")
            self.fig.colorbar(heatmap, cax=cax, ticks=mticker.LinearLocator(numticks=5))
            filename = os.path.splitext(os.path.basename(filePath))[0]
            fig.savefig(f"{self.saveFolder.get()}/{filename}_{self.vmin_value.get()}_{self.vmax_value.get()}.png", bbox_inches="tight")

        messagebox.showinfo("Info", "Complete")

        fig.clear()
        plt.close(fig)

    # Matplotlibライブラリで作成したグラフをTkinter内で描画する。
    # リサジュー図形について : https://kagakunojikan.net/math/lissajous_figure_and_irrational_number/
    def draw_plot(self, event=None):

        vmin = float(self.vmin_value.get())
        vmax = float(self.vmax_value.get())

        heatmap = self.ax.imshow(self.data1, cmap=self.cmap,vmin=vmin, vmax=vmax, interpolation="nearest")
        self.fig.colorbar(heatmap, cax=self.cax, ticks=mticker.LinearLocator(numticks=5))

        # グラフを描画する。
        self.canvas.draw()

    def save_fig(self,event=None):

        self.draw_plot()
        filename = os.path.splitext(os.path.basename(self.fileName.get()))[0]
        self.fig.savefig(f"{self.saveFolder.get()}/{filename}_{self.vmin_value.get()}_{self.vmax_value.get()}.png", bbox_inches="tight")
        

# Tkinter初学者参考 : https://docs.python.org/ja/3/library/tkinter.html#a-simple-hello-world-program
if __name__ == "__main__":

    # Windowを作成する。
    # Windowについて : https://kuroro.blog/python/116yLvTkzH2AUJj8FHLx/
    root = tk.Tk()
    app = Application(master=root)

    # Windowをループさせて、継続的にWindow表示させる。
    # mainloopについて : https://kuroro.blog/python/DmJdUb50oAhmBteRa4fi/
    app.mainloop()