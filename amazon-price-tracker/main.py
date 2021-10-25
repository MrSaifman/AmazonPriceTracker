import tkinter as tk
from tkinter import font, ttk
import utils
from data_manager import DataManager
from price_search import PriceSearch
import price_tracker

from urllib.request import urlopen
import io
from PIL import Image, ImageTk

BACKGROUND_COLOR = "#FFFFFF"
SECONDARY_COLOR = "#F0F0F0"
AMAZON_ORANGE = "#FF9900"


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("Amazon Price Tracker")
        self.parent.iconbitmap("images/logo_icon.ico")
        self.parent.config(bg=BACKGROUND_COLOR)
        self.parent.minsize(height=560, width=700)
        self.parent.columnconfigure([1, 3], weight=1)
        self.parent.columnconfigure(2, weight=2)
        self.parent.option_add("*TCombobox*selectBackground", AMAZON_ORANGE)
        self.parent.option_add("*TCombobox*font", ('calibre', 12, 'bold'))

        self.data_manager = DataManager()
        self.utils = utils.Utils()
        self.price_search = PriceSearch()
        template = Templates()

        self.watchlist_btn = template.create_button(
            None,
            'WATCHLIST',
            self.btn_pressed,
            activebackground=BACKGROUND_COLOR,
            bg=BACKGROUND_COLOR,
            btn_index=0)

        self.history_btn = template.create_button(
            None,
            'PRICE HISTORY',
            self.btn_pressed,
            activebackground=BACKGROUND_COLOR,
            bg=BACKGROUND_COLOR,
            btn_index=1)

        self.watcher_btn = template.create_button(
            None,
            'WATCHER',
            self.btn_pressed,
            activebackground=BACKGROUND_COLOR,
            bg=BACKGROUND_COLOR,
            btn_index=2)

        self.buttons = (self.watchlist_btn, self.history_btn, self.watcher_btn)

        self.watchlist_btn.grid(column=1, row=0, sticky="se")
        self.history_btn.grid(column=2, row=0, sticky="sew")
        self.watcher_btn.grid(column=3, row=0, sticky="sw")
        self.bind_on()

        self.parent.rowconfigure(1, weight=1)
        self.parent.columnconfigure(1, weight=1)

        self.history = HistoryPage(self, template)
        self.watchlist = WatchlistPage(self, template, self.history)
        self.watcher = WatcherPage(self, template)

        self.frames = (
            self.watchlist.frame,
            self.history.frame,
            self.watcher.frame
        )

        for frame in self.frames:
            frame.grid(column=1, row=1, sticky="nsew", columnspan=3)
        self.show_frame(self.history.frame)
        self.buttons[1].config(foreground=AMAZON_ORANGE)
        self.buttons[1].unbind('<Leave>')

    def btn_pressed(self, btn_index):
        curr_btn = self.buttons[btn_index]
        self.bind_on()
        curr_btn.unbind('<Leave>')
        for button in self.buttons:
            button.config(foreground='black')
        curr_btn.config(foreground=AMAZON_ORANGE)
        self.show_frame(self.frames[btn_index])

    def bind_on(self):
        """Enables all the buttons cursor binds when called."""
        for button in self.buttons:
            button.bind(
                '<Enter>',
                lambda event,
                btn=button: self.cursor_enter(btn))
            button.bind(
                '<Leave>',
                lambda event,
                btn=button: self.cursor_leave(btn))

    def cursor_enter(self, button):
        """Sets the button (first parameter) to the highlight color"""
        button.config(foreground=AMAZON_ORANGE)

    def cursor_leave(self, button):
        """Removes the button (first parameter) highlight color"""
        button.config(foreground='black')

    def show_frame(self, frame):
        frame.tkraise()


class Templates:
    """Class used to create a custom tkinter button, canvas, entry, and label with loaded values."""
    def create_button(self, frame, text, command,
                      activebackground=SECONDARY_COLOR,
                      bg=AMAZON_ORANGE, txt_size=15, **kwargs):
        """Creates a custom tkinter button with default values."""
        return tk.Button(
            frame,
            text=text,
            relief="sunken",
            padx=30,
            highlightthickness=0,
            bd=0,
            activebackground=activebackground,
            bg=bg,
            font=font.Font(size=txt_size, weight="bold"),
            command=lambda: command(**kwargs)
        )

    def create_label(self, frame, text, size=15, bg=SECONDARY_COLOR):
        """Creates a custom tkinter label with default values."""
        return tk.Label(
            frame,
            bg=bg,
            text=text,
            font=('calibre', size, 'bold')
        )

    def create_entry(self, frame, size=15, bg=SECONDARY_COLOR):
        """Creates a custom tkinter entry with default values."""
        return tk.Entry(
            frame,
            font=('calibre', size, 'normal'),
            width=30,
            relief="flat",
            bg=bg
        )

    def create_canvas(self, frame, height=36, width=300, background=SECONDARY_COLOR):
        """Creates a custom tkinter canvas with default values."""
        return tk.Canvas(
            frame,
            height=height,
            width=width,
            background=background,
            highlightthickness=0
        )


class HistoryPage:
    def __init__(self, gui, template):
        self.gui = gui
        self.range = 7
        self.frame = tk.Frame(self.gui.parent, bg=BACKGROUND_COLOR)
        self.graph = utils.Graph()

        self.frame.columnconfigure([1, 3], weight=1)
        self.frame.columnconfigure(2, weight=2)

        self.watchlist_combo = ttk.Combobox(
            self.frame,
            state="readonly",
            values=self.gui.data_manager.get_items())

        self.watchlist_combo.bind("<<ComboboxSelected>>", 
            self.combobox_selected)

        self.week_btn = template.create_button(
            self.frame,
            '7d',
            lambda range=7: self.update_range(range),
            txt_size=7)

        self.month_btn = template.create_button(
            self.frame,
            '1m',
            lambda range=30: self.update_range(range),
            txt_size=7)

        self.all_btn = template.create_button(
            self.frame,
            'all',
            lambda range=0: self.update_range(range),
            txt_size=7)

        self.stat_canvas = template.create_canvas(
            self.frame,
            height=125,
            width=800,
            background=AMAZON_ORANGE)

        self.watch_price_text = self.stat_canvas.create_text(
            100,
            46,
            font=('calibre', 17, "bold"),
            text="Watch Price:\n$00.00")

        self.price_text = self.stat_canvas.create_text(
            285,
            60,
            font=('calibre', 17, "bold"),
            text="Current Price:\n$00.00\n00-00-00")

        self.low_price_text = self.stat_canvas.create_text(
            500,
            60,
            font=('calibre', 17, "bold"),
            text="Lowest Price:\n$00.00\n00-00-00")

        self.high_price_text = self.stat_canvas.create_text(
            700,
            60,
            font=('calibre', 17, "bold"),
            text="Highest Price:\n$00.00\n00-00-00")

        self.update_background = template.create_canvas(
            self.frame
        )

        self.update_ent = template.create_entry(
            self.frame)

        self.update_lbl = template.create_label(
            self.frame,
            "Update Price:",
            size=15)

        self.update_btn = template.create_button(
            self.frame,
            'Update',
            self.update_price)

        self.remove_btn = template.create_button(
            self.frame,
            'Remove',
            self.remove_product,
            bg='red')

        self.buttons = [
            self.week_btn,
            self.month_btn,
            self.all_btn,
            self.update_btn,
            self.remove_btn]
        self.history_graph = self.graph.graph_data([0], [0], 0, self.frame)

        self.watchlist_combo.grid(column=2, row=1, sticky="new", pady=(25, 0))
        self.history_graph.grid(column=2, row=2, sticky="new")
        self.week_btn.grid(column=2, row=3, padx=(0, 150))
        self.month_btn.grid(column=2, row=3)
        self.all_btn.grid(column=2, row=3, padx=(150, 0))
        self.stat_canvas.grid(column=2, row=4, pady=(20, 20))
        self.remove_btn.grid(column=1, row=5, sticky="sew", pady=(25, 0))
        self.update_background.grid(column=1, row=5, columnspan=2, sticky="nsew", pady=(25, 0))
        self.update_ent.grid(column=2, row=5, sticky="sew", padx=(145, 5), pady=(29, 0))
        self.update_btn.grid(column=3, row=5, sticky="sew", pady=(25, 0))
        self.update_lbl.grid(column=2, row=5, sticky="sw", pady=(28, 0))
        self.disable_btns()

    def remove_product(self):
        name = self.watchlist_combo.get()
        MsgBox = tk.messagebox.askquestion(
            'Remove Product',
            f'Are you sure you want to remove {name}?',
            icon='warning')

        if MsgBox == 'yes':
            self.disable_btns()
            self.gui.data_manager.remove_item(name)
            self.watchlist_combo.set('')
            self.watchlist_combo.configure(
                values=self.gui.data_manager.get_items())
            product_data = {
                'desired_price': '0.00',
                'current_price': '0.00',
                'current_date': '00-00-00',
                'lowest_price': '0.00',
                'lowest_date': '00-00-00',
                'highest_price': '0.00',
                'highest_date': '00-00-00'
            }
            self.update_data(product_data)

    def disable_btns(self):
        for button in self.buttons:
            button['state'] = 'disabled'

    def enable_btns(self):
        for button in self.buttons:
            button['state'] = 'normal'

    def combobox_selected(self, event):
        """Enables any disabled buttons on the history page and
        updates the graph When a product is called"""
        self.enable_btns()
        self.update_graph()

    def update_data(self, product_data):
        """Updates the canvas stats based on the product data dictionary (first parameter)"""
        self.stat_canvas.itemconfig(
            self.watch_price_text,
            text=f"Watch Price:\n${product_data['desired_price']}")

        self.stat_canvas.itemconfig(
            self.price_text,
            text="Current Price:\n" +
            f"${product_data['current_price']}\n" +
            f"{product_data['current_date']}")

        self.stat_canvas.itemconfig(
            self.low_price_text,
            text="Lowest Price:\n" +
            f"${product_data['lowest_price']}\n" +
            f"{product_data['lowest_date']}")

        self.stat_canvas.itemconfig(
            self.high_price_text,
            text=f"Highest Price:\n" +
            f"${product_data['highest_price']}\n" +
            f"{product_data['highest_date']}")

    def update_graph(self):
        """Updates the visual graph based on range and product."""
        range = self.range
        name = self.watchlist_combo.get()
        price_data = self.gui.data_manager.get_price_data(name)
        product_data = self.gui.data_manager.get_product_data(name)

        self.update_data(price_data)

        if range == 0 or range > len(product_data[0]):
            dates = product_data[0]
            prices = product_data[1]
        else:
            dates = product_data[0][len(product_data[0])-range:]
            prices = product_data[1][len(product_data[0])-range:]

        self.history_graph.destroy()
        self.history_graph = self.graph.graph_data(
            dates,
            prices,
            product_data[2],
            self.frame)

        self.history_graph.grid(column=2, row=2, sticky="ewn", pady=(25, 0))

    def update_range(self, range: int):
        """Updates the graphs range (first parameter)"""
        self.range = range
        self.update_graph()

    def update_price(self):
        """Updates the database watch price of the given item selected"""
        name = self.watchlist_combo.get()
        updated_price = self.update_ent.get()
        try:
            updated_price = float(updated_price)
        except ValueError:
            self.update_ent.delete(0, len(updated_price))
        else:
            self.gui.data_manager.update_watchprice(name, updated_price)
            self.update_graph()


class WatchlistPage:
    def __init__(self, gui, template, history_pg):
        self.gui = gui
        self.history_pg = history_pg
        self.frame = tk.Frame(self.gui.parent, bg=BACKGROUND_COLOR)

        self.frame.columnconfigure([1, 3], weight=1)
        self.frame.columnconfigure(2, weight=2)
        self.frame.rowconfigure([1, 2], weight=1)
        self.frame.rowconfigure(3, weight=2)

        self.url_background = template.create_canvas(self.frame)
        self.search_background = template.create_canvas(self.frame)
        self.product_canvas = template.create_canvas(
            self.frame,
            height=500,
            width=800,
            background=BACKGROUND_COLOR)

        self.product_image = self.product_canvas.create_image(
            0,
            0,
            anchor='nw')

        self.product_text = self.product_canvas.create_text(
            600,
            90,
            font=('calibre', 15, "bold"))

        self.price_text = self.product_canvas.create_text(
            600,
            250,
            font=('calibre', 17, "bold"))

        self.err_msg_rectangle = self.product_canvas.create_rectangle(
            0,
            50,
            800,
            150,
            outline='red',
            fill='red')

        self.err_msg = self.product_canvas.create_text(
            400,
            100,
            font=('calibre', 15, "bold"),
            justify="center",
            fill='white')

        self.error_msg()
        self.product_canvas.itemconfig(self.err_msg, state='hidden')

        self.product_image = self.product_canvas.create_image(
            0,
            0,
            anchor='nw')

        self.product_text = self.product_canvas.create_text(
            600,
            90,
            font=('calibre', 15, "bold"))

        self.price_text = self.product_canvas.create_text(
            600,
            250,
            font=('calibre', 17, "bold"))

        self.url_ent = template.create_entry(self.frame)
        self.url_lbl = template.create_label(self.frame, "URL:")
        self.search_btn = template.create_button(
            self.frame,
            'Search',
            self.search_pressed)

        self.search_valid = False
        self.product_data = None
        self.url = None

        self.add_ent = template.create_entry(self.frame)
        self.add_lbl = template.create_label(
            self.frame,
            "Desired Price:")

        self.add_btn = template.create_button(
            self.frame,
            'Add',
            self.add_product)

        self.add_confirm = False

        self.url_background.grid(
            column=1,
            row=1,
            columnspan=2,
            sticky="ewn",
            pady=(25, 0))

        self.url_ent.grid(
            column=1,
            row=1,
            sticky="nwe",
            pady=(29, 0),
            padx=(60, 5),
            columnspan=2)

        self.url_lbl.grid(
            column=1,
            row=1,
            sticky="wn",
            pady=(28, 0))

        self.search_btn.grid(column=3, row=1, sticky="enw", pady=(25, 0))
        self.product_canvas.grid(
            column=1,
            row=3,
            columnspan=3,
            pady=(25, 25),
            padx=15, sticky="n")

        self.search_background.grid(
            column=1,
            row=4,
            columnspan=2,
            sticky="ewn",
            pady=(25, 0))

        self.add_ent.grid(
            column=1,
            row=4,
            sticky="nwe",
            pady=(29, 0),
            padx=(150, 5),
            columnspan=2)

        self.add_btn.grid(column=3, row=4, sticky="enw", pady=(25, 0))
        self.add_lbl.grid(column=1, row=4, sticky="wn", pady=(28, 0))

    def error_msg(self, msg=None):
        if msg:
            hidden = [self.product_image, self.product_text, self.price_text]
            normal = [self.err_msg, self.err_msg_rectangle]
            self.product_canvas.itemconfig(
                self.err_msg,
                text=self.gui.utils.textwrapper(msg, 82))
        else:
            hidden = [self.err_msg, self.err_msg_rectangle]
            normal = [self.product_image, self.product_text, self.price_text]

        for i in hidden:
            self.product_canvas.itemconfig(i, state='hidden')

        for i in normal:
            self.product_canvas.itemconfig(i, state='normal')

    def search_pressed(self):
        self.search_valid = False
        self.url = self.url_ent.get()
        self.product_data = self.gui.price_search.lookup_product(self.url)

        if not self.product_data[0]:
            self.error_msg(self.product_data[1])
            self.url_ent.delete(0, len(self.url_ent.get()))
        else:
            self.error_msg()
            try:
                product_name = self.gui.utils.textwrapper(
                    self.product_data[2],
                    30
                )
                self.product_canvas.itemconfig(
                    self.price_text, 
                    text="Price: $" + self.product_data[1]
                )
                self.product_canvas.itemconfig(
                    self.product_text,
                    text=product_name
                )

                my_page = urlopen(self.product_data[3])
                my_picture = io.BytesIO(my_page.read())
                pil_img = Image.open(my_picture)
                width, height = pil_img.size

                if width < 150 or height < 150:
                    pil_img = pil_img.resize(
                        (width*2, height*2),
                        resample=Image.BILINEAR)

                self.tk_img = ImageTk.PhotoImage(pil_img)
                self.product_canvas.itemconfig(
                    self.product_image,
                    image=self.tk_img)
                self.search_valid = True
            except:
                self.url_ent.delete(0, len(self.url_ent.get()))

    def add_product(self):
        price = self.add_ent.get()
        print(self.search_valid)
        if self.add_confirm:
            self.add_confirm = False
            self.add_btn.config(text="Add", bg=AMAZON_ORANGE)
            self.gui.data_manager.add_item(
                self.product_data[2],
                self.product_data[1],
                self.add_ent.get(),
                self.url
            )
            self.history_pg.watchlist_combo.configure(
                values=self.gui.data_manager.get_items())
            self.add_ent.delete(0, len(self.add_ent.get()))
        else:
            if not self.search_valid:
                self.error_msg("INVALID: Must search product before adding item to watchlist!")
            else:
                try:
                    price = float(price)
                    if price <= 0:
                        raise ValueError
                    format_price = "{:.2f}".format(price)
                    self.add_ent.delete(0, len(self.add_ent.get()))
                    self.add_ent.insert(0, format_price)
                    self.add_btn.config(text="Confirm", bg='green3')
                    self.add_confirm = True
                    print(format_price)
                except ValueError:
                    self.add_ent.delete(0, len(self.add_ent.get()))
                    self.error_msg("INVALID: Must provide a valid watch price!")


class WatcherPage:
    def __init__(self, gui, template):
        super().__init__()
        self.gui = gui
        self.frame = tk.Frame(self.gui.parent, bg=BACKGROUND_COLOR)

        self.frame.columnconfigure([1, 3], weight=1)
        self.frame.columnconfigure(2, weight=2)

        self.tracker_canvas = template.create_canvas(
            self.frame,
            height=100,
            width=500,
            background='red')

        self.status_txt = self.tracker_canvas.create_text(
            250,
            50,
            font=('calibre', 15, "bold"),
            justify="center",
            fill='white',
            text='Watcher Off')

        self.on_btn = template.create_button(
                    self.frame,
                    'ON',
                    self.on)

        self.off_btn = template.create_button(
            self.frame,
            'OFF',
            self.off)

        self.check_btn = template.create_button(
            self.frame,
            'Check Prices',
            self.check)

        self.tracker_lbl = tk.Label(
            self.frame,
            text=f"Last Check Status:\n{price_tracker.read_check_date()}",
            font=('calibre', 25, 'bold'),
            bg=BACKGROUND_COLOR)

        self.tracker_lbl.grid(column=2, row=1, pady=(85, 0))
        self.check_btn.grid(column=2, row=2, pady=(28, 0))
        self.tracker_canvas.grid(column=2, row=3, pady=(28, 0))
        self.off_btn.grid(column=2, row=4, pady=(28, 0), padx=(110, 0))
        self.on_btn.grid(column=2, row=4, pady=(28, 0), padx=(0, 110))

    def on(self):
        self.tracker_canvas.itemconfig(
            self.status_txt,
            text='Watcher On'
        )
        self.tracker_canvas.configure(bg='green')
        self.on_btn['state'] = 'disabled'
        self.off_btn['state'] = 'normal'

    def off(self):
        self.tracker_canvas.itemconfig(
            self.status_txt,
            text='Watcher Off')
        self.tracker_canvas.configure(bg='red')
        self.off_btn['state'] = 'disabled'
        self.on_btn['state'] = 'normal'

    def check(self):
        if price_tracker.check_price():
            time = price_tracker.update_check_date()
            self.tracker_lbl['text'] = f"Last Check Status:\n{time}"


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).grid(column=0, row=0)
    root.mainloop()
