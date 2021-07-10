from sklearn import linear_model
from PricePredictor import PricePredictor


class LinearRegressionPredictor(PricePredictor):

    def stock_price_predictor(self, data, predictors):

        X = data[predictors]
        y = data.iloc[:, 0]

        model = linear_model.LinearRegression(fit_intercept=True, normalize=True, copy_X=True)
        model.fit(X, y)

        return model.predict([data.loc[data.index.max()][1:]])[0]
