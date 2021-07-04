from Scrapper import WebScrapper
from YFinanceFinder import YFinanceFinder
from StockPricePredictor import stock_price_predictor

import matplotlib.pyplot as plt
import tkinter as tk
from PIL import ImageTk, Image


class GUI:

    NUM_FRAMES_BUY = 28
    NUM_FRAMES_SELL = 13
    FRAME_RATE = 50

    def __init__(self):
        self.target_stock = ""
        self.predictor_stocks = []
        self.stock_buttons = []
        self.chk_states = []
        self.time = [3, 6, 12, 60, 120]

        self.root = tk.Tk(className="Stock Price Predictor")
        self.root.geometry("800x800")
        self.root.maxsize(800, 800)

        self.canvas = tk.Canvas(self.root, height=800, width=800)
        image = ImageTk.PhotoImage(Image.open("E:\\Programming\\Python\\DerivativeSecurities"
                                              "\\res\\bg3.jpg"))
        self.canvas.create_image(0, 0, image=image, anchor="nw")
        self.canvas.create_text(400, 50, text="Stock Price Predictor",
                                font=("Helvetica", 16, "bold"), fill="white", width=500)

        self.duration = self.create_buttons()

        self.canvas.place(x=0, y=0)
        self.root.mainloop()

    def create_buttons(self):

        entry = tk.Entry(self.root, bg="#141412", fg="white", justify=tk.CENTER, relief=tk.RAISED)
        self.entry_reset(entry)
        entry.place(x=25, y=145, height=30, width=200)

        tk.Button(self.root, text="Enter", command=lambda: self.get_data(entry)) \
            .place(x=250, y=145, height=30, width=55)

        tk.Button(self.root, text="Calculate", command=self.calculate) \
            .place(x=330, y=145, height=30, width=70)

        tk.Button(self.root, text="Clear", command=self.root.destroy, bg="#DC5575", cursor="X_cursor") \
            .place(x=180, y=600, width=100, height=40)

        tk.Button(self.root, text="Restart", command=self.restart, bg="#23AD60", cursor="pirate") \
            .place(x=60, y=600, width=100, height=40)

        duration_var = tk.StringVar()
        durations = {"3 Months": "3_M", "6 Months": "6_M", "Year To Date": "YTD",
                     "1 Year": "1_Y", "5 Years": "5_Y", "MAX": "MAX"}
        for i, (text, value) in enumerate(durations.items()):
            tk.Radiobutton(self.root, text=text, variable=duration_var,
                           value=value).place(x=425, y=145 + i * 25)

        return duration_var

    def get_data(self, entry):

        stock_code = entry.get().split(" ")[-1].upper()
        if not stock_code or stock_code == self.target_stock or stock_code in self.predictor_stocks:
            pass
        elif not self.target_stock:
            self.target_stock = stock_code
            self.canvas.create_text(80, 200, text="Target Code",
                                    font=("Helvetica", 10, "bold"), fill="white")
            tk.Button(self.root, text=stock_code, default=tk.DISABLED).place(x=50, y=225, width=50)
        else:
            self.predictor_stocks.append(stock_code)
            self.canvas.create_text(180, 200, text="Predictor Stocks",
                                    font=("Helvetica", 10, "bold"), fill="white")

            var = tk.IntVar()
            self.stock_buttons.append(tk.Checkbutton(self.root, text=stock_code, state=tk.DISABLED, variable=var))
            self.chk_states.append(var)
            self.stock_buttons[-1].place(x=150, y=225 + (len(self.stock_buttons) - 1) * 35, width=50)

        self.entry_reset(entry)

    def calculate(self):

        if not self.target_stock or not self.predictor_stocks:
            return

        data = YFinanceFinder().find_stock_prices(self.target_stock, self.predictor_stocks, self.duration.get())
        plt.ion()
        plt.show()
        for column in self.predictor_stocks:
            data.plot(x=self.target_stock, y=column, kind="scatter")

        self.select_predictor_stocks(data)

    def entry_reset(self, entry):

        entry.delete(0, tk.END)
        if not self.target_stock:
            entry.insert(0, "Enter Target Stock Code: ")
        else:
            entry.insert(0, "Enter Predictor Stock Code: ")

    def select_predictor_stocks(self, data):
        self.predictor_stocks.clear()
        for checkbox in self.stock_buttons:
            checkbox['state'] = tk.NORMAL

        self.canvas.create_text(120, 225 + (len(self.stock_buttons) + 0.4) * 35, text="Select Predictor stocks",
                                font=("Helvetica", 10, "bold"), fill="white")

        tk.Button(self.root, text="Predict", command=lambda: self.predict(data)) \
            .place(x=225, y=225 + (len(self.stock_buttons)) * 35, width=50)

    def predict(self, data):

        for i in range(len(self.chk_states)):
            if self.chk_states[i].get():
                self.predictor_stocks.append(self.stock_buttons[i]["text"])

        if not self.predictor_stocks:
            return

        data = data.sort_index(ascending=False)
        try:
            result = stock_price_predictor(data, self.predictor_stocks)
        except ValueError:
            result = stock_price_predictor(data, self.predictor_stocks)

        self.display_results(result, data.iloc[0, 0])

    def clear(self):

        self.predictor_stocks.clear()
        self.stock_buttons = [x.destroy() for x in self.stock_buttons]
        self.stock_buttons.clear()
        self.chk_states.clear()
        self.target_stock = ""

    def update(self, frames, label, ind):

        ind += 1
        if ind == len(frames):
            ind = 0
        label.configure(image=frames[ind - 1])
        self.root.after(self.FRAME_RATE, self.update, frames, label, ind)

    def get_frames(self, predicted, current):

        if current > predicted:
            return [tk.PhotoImage(file='E:\\Programming\\Python\\DerivativeSecurities\\res\\sell.gif',
                                  format='gif -index %i' % i) for i in range(self.NUM_FRAMES_SELL)]
        return [tk.PhotoImage(file='E:\\Programming\\Python\\DerivativeSecurities\\res\\buy.gif',
                              format='gif -index %i' % i) for i in range(self.NUM_FRAMES_BUY)]

    def display_results(self, result, current):

        self.canvas.create_text(130, 240 + (len(self.stock_buttons) + 1) * 35,
                                text="The predicted value of " + self.target_stock + " is",
                                font=("Helvetica", 10, "bold"), fill="white")
        tk.Label(self.root, text=str(round(result, 2)), font="Verdana 10 underline") \
            .place(x=250, y=228 + (len(self.stock_buttons) + 1) * 35)

        self.canvas.create_text(150, 240 + (len(self.stock_buttons) + 2) * 35,
                                text=self.target_stock + " is",
                                font=("Helvetica", 10, "bold"), fill="white")
        tk.Label(self.root, font="Verdana 10 underline",
                 text=(lambda pred, curr: "UNDERVALUED" if curr < pred else "OVERVALUED")
                 (result, current)).place(x=210, y=228 + (len(self.stock_buttons) + 2) * 35)

        label = tk.Label(self.root)
        label.place(x=500, y=300)
        frames = self.get_frames(result, current)
        self.root.after(0, lambda: self.update(frames, label, 0))

    def restart(self):

        self.root.destroy()
        GUI()


if __name__ == '__main__':
    GUI()
