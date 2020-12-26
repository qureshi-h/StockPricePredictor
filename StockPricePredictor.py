from sklearn import linear_model


def stock_price_predictor(data, predictors):

    X = data[predictors]
    y = data.iloc[:, 0]

    model = linear_model.LinearRegression()
    model.fit(X, y)

    print(data[predictors])
    print(model.score(X, y))
    print(model.predict([X.iloc[0]]))
