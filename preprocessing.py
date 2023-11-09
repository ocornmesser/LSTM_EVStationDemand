import json
import pandas as pd
import matplotlib.pyplot as plt

#extracting connnection time from string, returns three ints (hour, minute, second)
def getConnectTime(connectionTime):
    connectionTimeNumber = connectionTime[17:25]
    hour = connectionTimeNumber[:2]
    minute = connectionTimeNumber[3:5]
    second = connectionTimeNumber[6:]
    return int(hour), int(minute), int(second)

#extracting disconnnect time from string, returns three ints (hour, minute, second)
def getDisconnectTime(disconnectTime):
    disconnectTimeNumber = disconnectTime[17:25]
    hour = disconnectTimeNumber[:2]
    minute = disconnectTimeNumber[3:5]
    second = disconnectTimeNumber[6:]
    return int(hour), int(minute), int(second)

# turning JSON data into a list for datafram
def getDataList(dataJSON):
    dataList = []
    for item in dataJSON["_items"]:
        row_data = [
            item["connectionTime"],
            item["disconnectTime"],
            item["doneChargingTime"],
            item["kWhDelivered"]
        ]
        dataList.append(row_data)
    return dataList

def updateDayMonthYear(day, month, year):
    if (day != 30) and (day != 31) and (day != 28) and (day != 29):
            day += 1
    elif (day == 30):
        if month == "Apr":
            month = "May"
            day = 1
        elif month == "Jun":
            month = "Jul"
            day = 1
        elif month == "Sep":
            month = "Oct"
            day = 1
        elif month == "Nov":
            month = "Dec"
            day = 1
        else:
            day += 1
    elif (day == 31):
        if month == "Jan":
            month = "Feb"
        elif month == "Mar":
            month = "Apr"
        elif month == "May":
            month = "Jun"
        elif month == "Jul":
            month = "Aug"
        elif month == "Aug":
            month = "Sep"
        elif month == "Oct":
            month = "Nov"
        elif month == "Dec":
            month = "Jan"
            year += 1
        day = 1
    elif (day == 28):
        if (month == "Feb") and (year != 2020):
            month = "Mar"
            day = 1
        elif (month == "Feb") and (year == 2020):
            month = "Feb"
            day += 1
        else:
            day += 1
    elif (day == 29):
        if month == "Feb":
            month = "Mar"
            day = 1
        else:
            day += 1
    return day, month, year





# Define the headers
headers = ["connectionTime", "disconnectTime", "doneChargingTime", "kWhDelivered"]

# first 4 months
with open('data4-26-18_8-26-18.json', 'r') as json_file:
    data4months1 = json.load(json_file)
    df1 = pd.DataFrame(getDataList(data4months1), columns=headers)


# next file
with open('data8-26-18_12-26-18.json', 'r') as json_file:
    data4months2 = json.load(json_file)
    df2 = pd.DataFrame(getDataList(data4months2), columns=headers)

# next file
with open('data12-26-18_4-26-19.json', 'r') as json_file:
    data4months3 = json.load(json_file)
    df3 = pd.DataFrame(getDataList(data4months3), columns=headers)

# next file
with open('data4-26-19_8-26-19.json', 'r') as json_file:
    data4months4 = json.load(json_file)
    df4 = pd.DataFrame(getDataList(data4months4), columns=headers)

# next file
with open('data8-26-19_12-26-19.json', 'r') as json_file:
    data4months5 = json.load(json_file)
    df5 = pd.DataFrame(getDataList(data4months5), columns=headers)

# next file
with open('data12-26-19_2-29-20.json', 'r') as json_file:
    data4months6 = json.load(json_file)
    df6 = pd.DataFrame(getDataList(data4months6), columns=headers)

# concatenate the dataframes
combinedDf = pd.concat([df1,df2,df3,df4,df5,df6], axis = 0).reset_index(drop=True)

#combinedDf = df1
#print(combinedDf)


# get data out of string form, with begin and end charge times
dataList = []
for i in range(len(combinedDf)):

    # find connection time
    connectionTimeString = combinedDf["connectionTime"]
    conHour, conMin, conSec = getConnectTime(connectionTimeString[i])

    # find disconnect time
    doneChargingTimeString = combinedDf["doneChargingTime"]
    if type(doneChargingTimeString[i]) != str:
        doneChargingTimeString = combinedDf["disconnectTime"]
    disHour, disMin, disSec = getDisconnectTime(doneChargingTimeString[i])

    # find kWhDelivered
    kWhDelStr = combinedDf["kWhDelivered"]
    kWhDel = kWhDelStr[i]

    # find date of connection
    connectTimeFull = combinedDf["connectionTime"]

    # find date of disconnection

    # combine into list
    dataList.append([conHour,conMin,conSec,disHour,disMin,disSec,kWhDel,connectTimeFull[i],doneChargingTimeString[i]])




#               0      1      2      3       4      5      6           7                         8
# session = [conHour,conMin,conSec,disHour,disMin,disSec,kWhDel, connectTimeFull[i], donechargingtimestring[i]]
currDateHour = [dataList[0][7][5:16], dataList[0][0]]
dataIntermSessions = []
kWhAcc = 0

for session in dataList:
    currDateHour = [session[7][5:16], session[0]]
    hour = 0
    if session[3] >= session[0]: 
        checkTimeMin = (session[0] * 60) + (session[1])
        doneTimeMin = (session[3] * 60) + (session[4])
        kWhPerMin = session[6] / (doneTimeMin - checkTimeMin)
        kWhAcc = 0
        #print(f" if - doneTime: {doneTimeMin / 60}, startTime: {checkTimeMin / 60}")
        hour = int(session[0])
        while checkTimeMin < doneTimeMin:
            if (checkTimeMin % 60) == 0:
                hour = checkTimeMin / 60
                dataIntermSessions.append([currDateHour[0], hour, kWhAcc])
                #print(f"test: startTime: {checkTimeMin / 60}, data: {dataIntermSessions[-1]}")
                kWhAcc = 0
            kWhAcc += kWhPerMin
            checkTimeMin += 1
        if (hour + 1) == 24:
            dataIntermSessions.append([currDateHour[0] + " nxtDay", 0, kWhAcc])
        else:
            dataIntermSessions.append([currDateHour[0], hour + 1, kWhAcc])
        #print(f"test: startTime: {checkTimeMin / 60}, data: {dataIntermSessions[-1]}")
        hour = 0
    else:
        checkTimeMin = (session[0] * 60) + (session[1])
        doneTimeMin = ((session[3] + 24) * 60) + (session[4])
        kWhPerMin = session[6] / (doneTimeMin - checkTimeMin)
        #print(f" else: {doneTimeMin / 60}, hour: {session[3]}, min: {session[4]}")
        hour = int(session[0])
        kWhAcc = 0
        while checkTimeMin < doneTimeMin:
            if ((checkTimeMin % 60) == 0) and ((checkTimeMin / 60) < 24):
                #print(f" else first if: {checkTimeMin / 60}")
                hour = checkTimeMin / 60
                dataIntermSessions.append([currDateHour[0], hour, kWhAcc])
                kWhAcc = 0
                #print(f"test: startTime: {checkTimeMin / 60}, data: {dataIntermSessions[-1]}")
            if ((checkTimeMin % 60) == 0) and ((checkTimeMin / 60) >= 24):
                #print(f" else 2nd if: {checkTimeMin / 60}")
                hour = (checkTimeMin / 60) - 24
                dataIntermSessions.append([currDateHour[0] + " nxtDay", hour, kWhAcc])
                kWhAcc = 0
                #print(f"test: startTime: {checkTimeMin / 60}, data: {dataIntermSessions[-1]}")
            kWhAcc += kWhPerMin
            checkTimeMin += 1
        if (checkTimeMin / 60) >= 24:
            dataIntermSessions.append([currDateHour[0] + " nxtDay", hour + 1, kWhAcc])
            #print(f"test: startTime: {checkTimeMin / 60}, data: {dataIntermSessions[-1]}")
        else:
            dataIntermSessions.append([currDateHour[0], hour + 1, kWhAcc])
            #print(f"test: startTime: {checkTimeMin / 60}, data: {dataIntermSessions[-1]}")
        hour = 0



#sortedByHourDf = pd.DataFrame(dataIntermSessions, columns=["Day", "Hour", "kWhUsed"])
#print(sortedByHourDf)
#print(sortedByHourDf["Day"].iloc[4][-6:])
#print(combinedDf)
#testDf.plot()
#plt.show()

#                       "day month yr"    
# dataIntermSessions = [currDateHour[0], hour, kWhAcc]
print("cleaning data")
date = "26 Apr 2018"
dayWithDemand = []
hour = 20
day = int(date[:2])
month = date[3:6]
year = int(date[7:11])
progressCount = 0
while date != "29 Feb 2020":
    #print(date)
    pastMonth = month
    kWhAcc = 0
    for instance in dataIntermSessions:
        currHour = instance[1]
        currTimeDay = int(instance[0][:2])
        currTimeMonth = instance[0][3:6]
        currTimeYear = int(instance[0][7:11])
        if (currTimeMonth != month) and ((currTimeDay != 30) and (currTimeDay != 31) and (currTimeDay != 28) and (currTimeDay != 29)):
            continue
        if instance[0][-6:0] == "nxtDay":
            currTimeDay, currTimeMonth, currTimeYear = updateDayMonthYear(currTimeDay, currTimeMonth, currTimeYear)
        if (currTimeYear == year) and (currTimeMonth == month) and (currTimeDay == day) and (currHour == hour):
            kWhAcc += instance[2]
    dayWithDemand.append([day, month, year, hour, kWhAcc])
    if hour >= 23:
        hour = 0
        day, month, year = updateDayMonthYear(day, month, year)
    else:
        hour += 1
    if (day == 28):
        print(f"{month}, {year}")
    
    date = str(day) + ' ' + month + ' ' + str(year)

sortedByHourDf = pd.DataFrame(dayWithDemand, columns=["Day", "Month", "Year", "Hour", "Demand (kWh)"])
#print(sortedByHourDf)
sortedByHourDf["Demand (kWh)"].plot()
plt.show()
sortedByHourDf.to_csv("DataByHour.csv")
print("done")

