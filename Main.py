import StockPriceFinder
import matplotlib.pyplot as plt


def main():

    data = StockPriceFinder.find_stock_prices(["AAPL", "GSPC", "DJI"])

    for column in data.columns[1:]:
        data.plot(x="AAPL", y=column, kind="scatter")

    plt.show()


if __name__ == '__main__':
    main()
