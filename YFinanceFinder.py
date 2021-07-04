from StockPriceFinder import StockPriceFinder
import yfinance


class YFinanceFinder(StockPriceFinder):

    def find_stock_prices(self, target_code, predictor_codes, duration):
        print(target_code + " " + " ".join(predictor_codes))
        data = yfinance.download(target_code + " " + " ".join(predictor_codes), period="1y")
        return data["Adj Close"]
