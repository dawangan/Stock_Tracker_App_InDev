import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import yfinance as yf
import robin_stocks as rh
import pandas as pd 
import time
import RecModule
def get_recommendations(): 
    dict_of_rec = RecModule.prep_data()
    df= pd.DataFrame(dict_of_rec)
    return df

#TODO:
def download_data(): 
    rh.robinhood.login('YOUREMAIL', 'YOURPASSWORD')

    my_stocks = rh.robinhood.account.build_holdings()
    stock_symbols = list(my_stocks.keys())
    data_frame = pd.DataFrame() 
    for symbol in stock_symbols:
        data = yf.download(symbol, period="1y", interval="1d")
        data_frame[symbol] = data['Close']
    data_frame.index = pd.to_datetime(data_frame.index)
    return stock_symbols

symbols =  download_data()


class DataFetcher(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)

    def run(self):
        data = RecModule.update_stock_info()
        for i in range(101):
            self.progress.emit(i)
            time.sleep(0.05)
        self.finished.emit(data)

class AssetGraph(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AssetGraph, self).__init__(parent)
        self.stock_data = pd.DataFrame(pd.read_csv('out.csv', index_col=0, parse_dates=True))
        self.recommendations = get_recommendations()
        self.overlay_mode = False
        self.symbols = download_data()
        self.setupUI()
        self.update_plot(0)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.update_plot_delayed)
        

    def setupUI(self):
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.combobox1 = QtWidgets.QComboBox()
        self.combobox2 = QtWidgets.QComboBox()
        self.combobox1.addItems(self.symbols)
        self.combobox1.currentIndexChanged.connect(self.update_combo2)
        layout.addWidget(self.combobox1)
        layout.addWidget(self.combobox2)

        self.slider = QSlider(QtCore.Qt.Horizontal)
        self.slider.valueChanged.connect(self.on_slider_value_changed)
        self.slider.setMinimum(0)
        layout.addWidget(self.slider)

        self.value_label = QLabel()
        layout.addWidget(self.value_label)

        self.update_data_btn = QPushButton("Update Data", self)
        self.update_data_btn.clicked.connect(self.update_data)
        layout.addWidget(self.update_data_btn)

        self.plot_overlay_btn = QPushButton("Plot Overlay", self)
        self.plot_overlay_btn.clicked.connect(self.toggle_overlay)
        layout.addWidget(self.plot_overlay_btn)

        self.progressBar = QtWidgets.QProgressBar(self)
        layout.addWidget(self.progressBar)

        self.update_stock_button = QtWidgets.QPushButton("Update Stock Data", self)
        self.update_stock_button.clicked.connect(self.update_stock_info)
        layout.addWidget(self.update_stock_button)

    def on_slider_value_changed(self, value):
        self.timer.start(100)

    def update_plot_delayed(self):
        self.update_plot(self.slider.value())

    def update_combo2(self):
        current_selection = self.combobox1.currentText()
        self.combobox2.clear()
        if current_selection in self.recommendations.columns:
            self.combobox2.addItems(self.recommendations[current_selection].dropna().tolist())

    def update_plot(self, value=None):
        if value is None:
            value = self.slider.value()
        
        ticker1 = self.combobox1.currentText()
        data1 = self.stock_data[ticker1]
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        line1, = ax.plot(data1.index, data1.values, label=ticker1)
        
        if self.overlay_mode:
            ticker2 = self.combobox2.currentText()
            data2 = self.stock_data[ticker2]
            line2, = ax.plot(data2.index, data2.values, label=ticker2)
        
        value = min(value, len(data1) - 1)
        ax.axvline(data1.index[value], color='r', linestyle='--')
        
        ax.legend()
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        
        self.canvas.draw()
        self.slider.setMaximum(len(data1) - 1)
        date = data1.index[value].strftime('%Y-%m-%d')
        value1 = data1.iloc[value]
        if self.overlay_mode:
            value2 = data2.iloc[value]
            self.value_label.setText(f'{date}: {ticker1} = {value1:.2f}, {ticker2} = {value2:.2f}')
        else:
            self.value_label.setText(f'{date}: {ticker1} = {value1:.2f}')

    def toggle_overlay(self):
        self.overlay_mode = not self.overlay_mode
        self.plot_overlay_btn.setText("Remove Overlay" if self.overlay_mode else "Plot Overlay")
        self.update_plot()

    def update_data(self):
        self.update_plot(self.slider.value())

    def update_stock_info(self):
        self.fetcher = DataFetcher()
        self.fetcher.progress.connect(self.progressBar.setValue)
        self.fetcher.finished.connect(self.on_data_update_finished)
        self.fetcher.start()
        self.update_stock_button.setEnabled(False)

    def on_data_update_finished(self, data):
        self.stock_data = data
        self.update_plot()
        self.update_stock_button.setEnabled(True)

class App(QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setWindowTitle("Stock Analyzer")
        self.setGeometry(100, 100, 800, 600)
        self.widget = AssetGraph(self)
        self.setCentralWidget(self.widget)

def main():
    app = QApplication(sys.argv)
    main_window = App()
    main_window.show()
    print("Press Enter to exit...")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    