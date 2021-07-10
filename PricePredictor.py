from abc import ABC, abstractmethod


class PricePredictor(ABC):

    @abstractmethod
    def stock_price_predictor(self, data, predictors):
        pass
