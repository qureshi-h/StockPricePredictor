from sklearn import linear_model


def stock_price_predictor(data, predictors):

    X = data[predictors]
    y = data.iloc[:, 0]

    model = linear_model.LinearRegression(fit_intercept=True, normalize=True, copy_X=True)
    model.fit(X, y)

    return model.predict([X.iloc[0]])[0]
