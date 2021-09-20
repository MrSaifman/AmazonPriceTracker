import textwrap
from hashlib import sha1
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.use("TkAgg")
AMAZON_ORANGE = "#ff9900"


class Utils:
    def encode(self, string: str):
        hash = sha1(str.encode(string)).hexdigest()
        return hash

    def textwrapper(self, text: str, num_letters: int):
        string = '\n'.join(
            textwrap.wrap(
                text,
                num_letters,
                break_long_words=False))

        return string


class Graph:
    def graph_data(self, x_array, y_array, watch_price, frame):
        if len(x_array) != len(y_array):
            print(f"x_array's size is {len(x_array)} and y_array's size is {len(y_array)} ")

        fig = Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.axhline(y=watch_price, color='red')
        ax.plot(x_array, y_array, color=AMAZON_ORANGE, marker='o')

        labels_new = ['' for i in range(0, len(x_array))]
        labels_new[0] = x_array[0]
        labels_new[-1] = x_array[-1]
        ax.set_xticklabels(labels_new)
        ax.tick_params(axis=u'both', which=u'both', length=0)
        canvas = FigureCanvasTkAgg(fig, frame)
        return canvas.get_tk_widget()
