import numpy as np
import csv
import pandas as pd
import matplotlib.pyplot as plt
import math
from sklearn.metrics import r2_score

from tensorflow import keras
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense

def split_sequence(sequence, n_steps):
    X, y = list(), list()
    for i in range(len(sequence)):
        # find the end of this pattern
        end_ix = i + n_steps
        # check if we are beyond the sequence
        if end_ix > len(sequence)-1:
            break
        # gather input and output parts of the pattern
        seq_x, seq_y = sequence[i:(end_ix-1)], sequence[end_ix-1]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)

with open('DataByHourWithWeather.csv', 'r') as incomingData:
    readFile = csv.reader(incomingData)
    strictData = []
    dayData = []
    dayType = 0
    dayCounter = 4
    pastDay = 26
    for row in readFile:

        if row[5] == 'Demand (kWh)':
            continue

        if (row[1] != pastDay): # new day
            if (dayCounter == 6) or (dayCounter == 7):
                if (dayCounter == 7):
                    dayCounter = 1
                else:
                    dayCounter += 1
                dayType = 1
            else:
                dayType = 0
                dayCounter += 1
            
        pastDay = row[1]
        # row 5 in kwh, row 6 is temp, row 7 is humidity, row 4 is hour, day type is weekend (Y/N)
        strictData.append([float(row[5]), dayType, int(row[4]), float(row[6]), float(row[7])])
        dayData.append([row[1], row[2], row[3], row[4]])

#dataWithWeekend = pd.DataFrame(strictData, columns=["Demand (kWh)", "Weekend(Y/N)"])
#dataWithWeekend.to_csv("adjustedDataWithWeekends.csv")
dayDataStr = []
for day in dayData:
    strDay = ' '.join(day)
    dayDataStr.append(strDay)


trainData = strictData[:int((len(strictData)//1.33))]
testData = strictData[int((-len(strictData)//1.33)):]
n_steps = 36
XTrain, yTrainWithDay = split_sequence(trainData, n_steps+1)
XTest, yTestWithDay = split_sequence(testData, n_steps+1)
yTest = []
for row in yTestWithDay:
    yTest.append(row[0])
yTest = np.array(yTest)
yTrain = []
for row in yTrainWithDay:
    yTrain.append(row[0])
yTrain = np.array(yTrain)
n_features = 5

XTrain = XTrain.reshape((XTrain.shape[0], XTrain.shape[1], n_features))

# define model
model = Sequential()
model.add(LSTM(50, activation='sigmoid', input_shape=(n_steps, n_features)))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')

print("Training model...")
model.fit(XTrain, yTrain, epochs=60, verbose=1)
print("Completed training of model.")

XTest = XTest.reshape(XTest.shape[0], XTest.shape[1], n_features)
print("Testing model...")
yhat = model.predict(XTest, verbose=1)
print("Completed testing of model")


yhat = yhat.reshape(yhat.shape[0], yhat.shape[1])

predictionDF = pd.DataFrame(yhat)
actualDF = pd.DataFrame(yTest)
timesDF = pd.DataFrame(dayDataStr)

# RMSE
acc = 0
for time in range(len(predictionDF)):
    square = math.pow((float(actualDF.iloc[time].iloc[0]) - float(predictionDF.iloc[time].iloc[0])),2)
    acc += square

beforeSqr = acc / len(predictionDF)
rmse = math.sqrt(beforeSqr)
print()
print()
print(f"RMSE achieved: {rmse}")
print("RMSE from study: 5.268")
print()
print()


# MAE
acc = 0
for time in range(len(predictionDF)):
    diff = float(actualDF.iloc[time].iloc[0]) - float(predictionDF.iloc[time].iloc[0])
    acc += abs(diff)
mae = acc / len(predictionDF)
print()
print()
print(f"MAE acheived: {mae}")
print("MAE from study: 3.267")
print()
print()


# R^2
r2 = r2_score(actualDF.values, predictionDF.values)
print()
print()
print(f"R^2 acheived: {r2}")
print("R^2 from study: 0.8811")
print()
print()

# weekend in september
timesArray = np.array(dayDataStr)
startHour = 13 + (24*7)
endHour = 63 + (24*7)
lengthTrain = len(XTrain)
plt.plot(timesArray[(startHour + lengthTrain):(endHour + lengthTrain)], actualDF.iloc[startHour:endHour], label='Actual')
plt.plot(timesArray[(startHour + lengthTrain):(endHour + lengthTrain)], predictionDF.iloc[startHour:endHour], label='Predicted')
plt.xticks(rotation=80, fontsize = 5)
plt.legend()
plt.title("Weekend in September")
plt.xlabel("Day")
plt.ylabel("kWh Demand")
plt.show()

# week during september
startHour = 63 + (24*7)
endHour = 63 + (5*24) + (24*7)
lengthTrain = len(XTrain)
plt.plot(timesArray[(startHour + lengthTrain):(endHour + lengthTrain)], actualDF.iloc[startHour:endHour], label='Actual')
plt.plot(timesArray[(startHour + lengthTrain):(endHour + lengthTrain)], predictionDF.iloc[startHour:endHour], label='Predicted')
plt.xticks(rotation=80, fontsize = 5)
plt.legend()
plt.title("Week in September")
plt.xlabel("Day")
plt.ylabel("kWh Demand")
plt.show()

# weekend during January
startHour = 13 + (24*7) + (24*7*17) # would be 24*7*13 for quarter of year, but september is a little short
endHour = 63 + (24*7) + (24*7*17)
lengthTrain = len(XTrain)
plt.plot(timesArray[(startHour + lengthTrain):(endHour + lengthTrain)], actualDF.iloc[startHour:endHour], label='Actual')
plt.plot(timesArray[(startHour + lengthTrain):(endHour + lengthTrain)], predictionDF.iloc[startHour:endHour], label='Predicted')
plt.xticks(rotation=80, fontsize = 5)
plt.legend()
plt.title("Weekend in January")
plt.xlabel("Day")
plt.ylabel("kWh Demand")
plt.show()

startHour = 63 + (24*7) + (24*7*17)
endHour = 63 + (24*7) + (5*24) + (24*7*17)
lengthTrain = len(XTrain)
plt.plot(timesArray[(startHour + lengthTrain):(endHour + lengthTrain)], actualDF.iloc[startHour:endHour], label='Actual')
plt.plot(timesArray[(startHour + lengthTrain):(endHour + lengthTrain)], predictionDF.iloc[startHour:endHour], label='Predicted')
plt.xticks(rotation=80, fontsize = 5)
plt.legend()
plt.title("Week in January")
plt.xlabel("Day")
plt.ylabel("kWh Demand")
plt.show()
