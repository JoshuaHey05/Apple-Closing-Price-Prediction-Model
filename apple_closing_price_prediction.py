# -*- coding: utf-8 -*-
"""Apple Closing Price Prediction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HMyZSI-8hwA0VdjAwooIXxuLa73sem86
"""

#Program uses an artificial neural network called Long Short Term Memory (LSTM), will use this program to predict the closing stock price of a corporation (Apple Inc.)
# using the past 60 days of stock price - apparently

import math
import yfinance as yf
import pandas as pd
import pandas_datareader as web
import datetime
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

df = yf.download('AAPL', start='2016-01-01', end=datetime.datetime.now().date())

#show the trends of the AAPL stock closing price in USD
plt.figure(figsize=(16,8))
plt.title('Close Price History')
plt.plot(df['Close'])
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.show()

#create a new dataframe and specify the length of the training data
df_close = df.filter(['Close'])
close_dataset = df_close.values

training_close_dataset_len = math.ceil(len(close_dataset) * .8)

#scale the values from 0 to 1
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(df_close)

#seperate the data to be used for training
train_close_data = scaled_data[0:training_close_dataset_len, :]

x_train = []
y_train = []

for i in range(60, len(train_close_data)):
  x_train.append(train_close_data[i-60:i, 0])
  y_train.append(train_close_data[i, 0])

#convert dataset to numpy arrays
x_train, y_train = np.array(x_train), np.array(y_train)

x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

#train the Sequential model with the dataset
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
model.add(LSTM(50, return_sequences=False,))
model.add(Dense(25))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mean_squared_error')

model.fit(x_train, y_train, batch_size=1, epochs=1)

#seperate recent data excluded from training to test the accuracy
test_data = scaled_data[training_close_dataset_len - 60:, :]

x_test = []
y_test = close_dataset[training_close_dataset_len:, :]

for i in range(60, len(test_data)):
  x_test.append(test_data[i-60:i, 0])

#convert to a numpy array
x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

# Generate predictions
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

#get the Root Mean Squared Error (RMSE) - square root of residuals
rmse = np.sqrt(np.mean(((predictions- y_test)**2)))
print('RMSE: ' + str(rmse))

# Prepare data for plotting
train = df_close[:training_close_dataset_len]
valid = df_close[training_close_dataset_len:]
valid['Predictions'] = predictions

# Plotting
plt.figure(figsize=(16,8))
plt.title('Model')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)

plt.plot(train['Close'])
plt.plot(valid[['Close', 'Predictions']])
plt.legend(['Train', 'Val', 'Predictions'], loc='upper right')

plt.show()

new_df = df.filter(['Close'])
last_60_days = new_df[-60:].values

last_60_days_scaled = scaler.transform(last_60_days)

X_test = []
X_test.append(last_60_days_scaled)

X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

#create a new dataframe with the saved prediction values
pred_price = model.predict(X_test)

pred_price = scaler.inverse_transform(pred_price)
print('Predicted Price for Jun 8: ' + str(pred_price))
#predicted for Jun 8: 192.336