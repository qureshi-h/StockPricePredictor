from abc import ABC, abstractmethod


class StockPriceFinder(ABC):

    @abstractmethod
    def find_stock_prices(self, target_code, predictor_codes, duration):
        pass
