import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO 
import json
from datetime import datetime


st.set_page_config(layout="wide")

st.title("Server Log Analysis")



log_file = st.file_uploader("Upload a file", accept_multiple_files=False)

if log_file is None:
    file = "./Logs/smartfox.log"
    log_file = open(file, "rb")
    st.write(file)
userName = st.text_input("Enter user name: ")



lines = []

if log_file is not None:
    # To read file as bytes:
    for line in log_file:
        lines.append(line)

    # # To convert to a string based IO:
    # stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    # st.write(stringio)

    # To read file as string:
    
    # st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
    # dataframe = pd.read_(uploaded_file)
    # st.write(dataframe)
    # data = json.loads(bytes_data)
    # st.write(data)

    # st.table(data)

roomdetailsDict = {}
userNameRoomList = []
for line in lines:
    line = line.decode()
    if "Room_name: " in line:
        roomName = line.split("Room_name: ", 1)[1].split(";")[0]
        if roomName not in roomdetailsDict:
            roomdetailsDict[roomName] = []
        roomdetailsDict[roomName].append(line)
    
    if userName and "Username: " + userName + ";" in line:
        roomName = line.split("Room_name: ", 1)[1].split(";")[0]
        userRating = line.split("user_rating: ")[1].split(" ")[0]
        if roomName not in userNameRoomList:
            userNameRoomList.append(roomName + " | userRating: " + userRating)


select = st.selectbox("Select room name: ", userNameRoomList)
if select: 
    select = select.split(" | ")[0]
room_name = st.text_input("Enter room name: ", select)


if room_name in roomdetailsDict:
    st.write(roomdetailsDict[room_name])
else: 
    st.write("No room found ")





printbuglist = st.text_input("do you want to see bug list: ", value="n")

if printbuglist == "y":
    buglist = []
    i = 0
    j = -1
    count = 0
    for line in lines:
        lineD = line.decode()
        if ("WARN" in lineD or "ERROR" in lineD) and "Session Reconnection failure" not in lineD and "com.smartfoxserver.v2.exceptions.SFSExtensionException:" not in lineD: 
            i = lines.index(line)
            j = 0
        if "INFO" in lineD and j == 0:
            j = lines.index(line)    
            buglist.extend(lines[i:j])
            j = -1
            count = count + 1

    st.write(buglist)
    st.write(("Total Number of bugs: ", count))


roomNamesList = []
switchTurnTimeDict = {}
strikerResponseTimeDict = {}
keeperResponseTimeDict = {}
nextSwitchTurnTimeDict = {}
timeoutTimeDict = {}
gameEndDict = {}
turnCountDict = {}
userGoneHandlerDict = {}
appPauseFlag = {}
stuckGames = {}



basetime = "00:00:08,500"
timeDelta =  datetime.strptime(basetime, "%H:%M:%S,%f") - datetime.strptime("00:00:00,100", "%H:%M:%S,%f")
prev_line = None
for line in lines:
    line = line.decode()
    roomName = ""
    if "SFS_PlayerId: 1" in line and "Request Message: ready" in line:
        roomName = line.split("Room_name: ", 1)[1].split(";")[0]
        if roomName not in roomNamesList:
            roomNamesList.append(roomName)

    if ("SFS_PlayerId: 1" in line or "SFS_PlayerId: 2" in line) and "Response Message: switch_turn" in line:
        roomName = line.split("Room_name: ", 1)[1].split(";")[0]
        time = line.split(" | ")[1]
        turnCount = line.split("Turn_count: ", 1)[1].split(";")[0]
        if roomName not in switchTurnTimeDict:
            switchTurnTimeDict[roomName] = {}
        switchTurnTimeDict[roomName].update({turnCount: time})
        
    
    if ("SFS_PlayerId: 1" in line or "SFS_PlayerId: 2" in line) and "Response Message: striker_response" in line:
        roomName = line.split("Room_name: ", 1)[1].split(";")[0]
        time = line.split(" | ")[1]
        turnCount = line.split("Turn_count: ", 1)[1].split(";")[0]
        if roomName not in strikerResponseTimeDict:
            strikerResponseTimeDict[roomName] = {}
        strikerResponseTimeDict[roomName].update({turnCount: time})

    if ("SFS_PlayerId: 1" in line or "SFS_PlayerId: 2" in line) and "Response Message: keeper_response" in line:
        roomName = line.split("Room_name: ", 1)[1].split(";")[0]
        time = line.split(" | ")[1]
        turnCount = line.split("Turn_count: ", 1)[1].split(";")[0]
        # print(turnCount)
        if roomName not in keeperResponseTimeDict:
            keeperResponseTimeDict[roomName] = {}
        keeperResponseTimeDict[roomName].update({turnCount : time})


    if ("SFS_PlayerId: 1" in line or "SFS_PlayerId: 2" in line) and "Response Message: switch_turn" in line:
        roomName = line.split("Room_name: ", 1)[1].split(";")[0]
        time = line.split(" | ")[1]
        turnCount = line.split("Turn_count: ", 1)[1].split(";")[0]
        turnCount = str(int(turnCount) - 1)
        if roomName not in nextSwitchTurnTimeDict:
            nextSwitchTurnTimeDict[roomName] = {}
        nextSwitchTurnTimeDict[roomName].update({turnCount: time})


    if ("SFS_PlayerId: 1" in line or "SFS_PlayerId: 2" in line)  and "Response Message: timeout" in line:
        roomName = line.split("Room_name: ", 1)[1].split(";")[0]
        time = line.split(" | ")[1]
        turnCount = line.split("Turn_count: ", 1)[1].split(";")[0]
        if roomName not in timeoutTimeDict:
            timeoutTimeDict[roomName] = {}
        timeoutTimeDict[roomName].update({turnCount : time})


    if "Request Message: app_paused" in line:
        roomName = line.split("Room_name: ", 1)[1].split(";")[0]
        time = line.split(" | ")[1]
        turnCount = line.split("Turn_count: ", 1)[1].split(";")[0]
        if roomName not in appPauseFlag:
            appPauseFlag[roomName] = {}
        appPauseFlag[roomName].update({turnCount: True})


    if "Response Message: sync_time" in line:
        roomName = line.split("Room_name: ", 1)[1].split(";")[0]
        time = line.split(" | ")[1]
        turnCount = line.split("Turn_count: ", 1)[1].split(";")[0]
        if roomName not in appPauseFlag:
            appPauseFlag[roomName] = {}
        appPauseFlag[roomName].update({turnCount: False})
    

    if "Winner_player_ID" in line: 
        roomName = line.split("Room_name: ", 1)[1].split(";")[0]
        gameEndDict[roomName] = True

    if "Turn_count: -1; Request Message: On User gone" in line:
        roomName = line.split("Room_name: ", 1)[1].split(";")[0]
        userGoneHandlerDict[roomName] = True
        time = line.split(" | ")[1]
        time = datetime.strptime(time, "%H:%M:%S,%f")

        prev_line = None
        for i in range(1, len(roomdetailsDict[roomName])):
            if "bot " in roomdetailsDict[roomName][i]:
                break
            if "Turn_count: -1; Request Message: On User gone" in roomdetailsDict[roomName][i]:
                prev_line = roomdetailsDict[roomName][i-1]

        if prev_line:
            prevTime = prev_line.split(" | ")[1]
            prevTime = datetime.strptime(prevTime, "%H:%M:%S,%f")
            if time - prevTime > timeDelta :
                stuckGames[roomName] = True
    
    


for turnCount in range(1, 11):
    turnCount = str(turnCount)
    timeDelayDict = {}  
    for roomName in roomNamesList:
        if roomName in switchTurnTimeDict and turnCount in switchTurnTimeDict[roomName]:
            switchTime = datetime.strptime(switchTurnTimeDict[roomName][turnCount], "%H:%M:%S,%f")
        else:
            switchTime = -1
        
        if roomName in strikerResponseTimeDict and turnCount in strikerResponseTimeDict[roomName]:
            strikerTime = datetime.strptime(strikerResponseTimeDict[roomName][turnCount], "%H:%M:%S,%f")
        else:
            strikerTime = -1

        if roomName in keeperResponseTimeDict and turnCount in keeperResponseTimeDict[roomName]:
            keeperTime = datetime.strptime(keeperResponseTimeDict[roomName][turnCount], "%H:%M:%S,%f")
        else:
            keeperTime = -1

        if roomName in nextSwitchTurnTimeDict and turnCount in nextSwitchTurnTimeDict[roomName]:
            nextSwitchTime = datetime.strptime(nextSwitchTurnTimeDict[roomName][turnCount], "%H:%M:%S,%f")
        else:
            nextSwitchTime = -1

        if roomName in timeoutTimeDict and turnCount in timeoutTimeDict[roomName]:
            timeoutTime = datetime.strptime(timeoutTimeDict[roomName][turnCount], "%H:%M:%S,%f")
        else:
            timeoutTime = -1

        if strikerTime != -1 and switchTime != -1: 
            timeDelayDict[roomName] = {"strikerDelay" : strikerTime - switchTime}
        else:
            timeDelayDict[roomName] = {"strikerDelay" : "--"}
        
        if strikerTime != -1 and keeperTime != -1: 
            timeDelayDict[roomName].update({"keeperDelay" : keeperTime - strikerTime})
        else: 
            timeDelayDict[roomName].update({"keeperDelay" : "--"})

        if keeperTime != -1 and nextSwitchTime != -1: 
            timeDelayDict[roomName].update({"switchTurnDelay" : nextSwitchTime - keeperTime})
        else: 
            timeDelayDict[roomName].update({"switchTurnDelay" : "--"})

        if timeoutTime != -1 and switchTime != -1:
            timeDelayDict[roomName].update({"timeOutDelay" : timeoutTime - switchTime})
        else:
            timeDelayDict[roomName].update({"timeOutDelay" : "--"})

        if roomName in appPauseFlag and turnCount in appPauseFlag[roomName]:
            timeDelayDict[roomName].update({"appPaused" : appPauseFlag[roomName][turnCount]})
        else:
            timeDelayDict[roomName].update({"appPaused" : False})
        
        if switchTime == -1 and strikerTime == -1 and keeperTime == -1 and nextSwitchTime == -1 and timeoutTime == -1:
            timeDelayDict[roomName].update({"turnCount" : False})
        else:
            timeDelayDict[roomName].update({"turnCount" : True})

        if roomName in gameEndDict:
            timeDelayDict[roomName].update({"gameEnd" : gameEndDict[roomName]})
        else:
            timeDelayDict[roomName].update({"gameEnd" : False})

        if roomName in userGoneHandlerDict:
            timeDelayDict[roomName].update({"userGone" : True})
        else:
            timeDelayDict[roomName].update({"userGone" : False})

        if roomName in stuckGames:
            timeDelayDict[roomName].update({"stuckGame" : True})
        else:
            timeDelayDict[roomName].update({"stuckGame" : False})


    turnCountDict[turnCount] = timeDelayDict

    # print("==========================")


checkIndexStriker = 0
totalIndexStiker = 0
checkIndexSwitchTurn = 0
totalIndexSwitchTurn = 0
checkIndexTimeout = 0
totalIndexTimeout = 0



timeoutIndexList = []
strikerIndexList = []
switchTurnList = []

totalGames = 0

for turnCount in turnCountDict: 
    df = pd.DataFrame.from_dict(turnCountDict[turnCount]).transpose()
    timeoutIndex = len(df[(df["strikerDelay"] == "--") & (df["timeOutDelay"] == "--") & (df["switchTurnDelay"] == "--") & (df["turnCount"] == True) & (df["userGone"] == False)])
    totalGames = len(df)
    timeoutIndexList.append(timeoutIndex)
    checkIndexTimeout = checkIndexTimeout + timeoutIndex
    totalIndexTimeout = len(df)
    # df = pd.to_timedelta(df["strikerDelay"])
    m1 = df[df["strikerDelay"] != "--"]
    m2 = df[df["keeperDelay"] != "--" ]
    m3 = df[df["switchTurnDelay"] != "--"]
    m1 = pd.DataFrame(pd.to_timedelta(m1["strikerDelay"]))
    m2 = pd.DataFrame(pd.to_timedelta(m2["keeperDelay"]))
    m3 = pd.DataFrame(pd.to_timedelta(m3["switchTurnDelay"]))


    timeDelta = pd.Timedelta(seconds=10, microseconds=500)
    strikerIndex = len(m1[m1["strikerDelay"] > timeDelta])
    strikerIndexList.append(strikerIndex)
    checkIndexStriker = strikerIndex +  len(m1[m1["strikerDelay"] > timeDelta])
    totalIndexStiker = len(m1["strikerDelay"])

    switchIndex = len(m3[m3["switchTurnDelay"] > timeDelta])
    switchTurnList.append(switchIndex)
    checkIndexSwitchTurn = checkIndexSwitchTurn + switchIndex
    totalIndexSwitchTurn = len(m3["switchTurnDelay"])


turnCountList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# turnCountList = [1]
serverHealthPercent = 100 - ((checkIndexStriker + checkIndexSwitchTurn + checkIndexTimeout)/(totalIndexStiker + totalIndexSwitchTurn + totalIndexTimeout) *  100)

st.title("Server Health: " + str(serverHealthPercent) + "%")




st.write(" Possible Events ")

# userGonePercent = len(userGoneHandlerDict)/len(roomNamesList) *  100
# st.write("Percentage of games ended by user gone : " , userGonePercent)

df = pd.DataFrame.from_dict(turnCountDict['1']).transpose()
TotalGames = len(df)
userGoneGames = len(df[df["userGone"] == True])
stuckGames = len(df[df["stuckGame"] == True])
notEndGames = len(df[df["gameEnd"] == False])

columnName = ["User Gone Games", "Stuck Games", "Not Ended Games"]
value = [userGoneGames, stuckGames, notEndGames]

chart_data = pd.DataFrame({'index' : columnName, 'number of games' : value}).set_index('index')
st.bar_chart(chart_data)

st.write(chart_data)

st.write("User gone games")
st.write(df[df["userGone"] == True])

st.write("stuck games")
st.write(df[df["stuckGame"] == True])


st.write("Percentage of games with no striker and keeper response and no timeout: " , checkIndexTimeout/totalIndexTimeout * 100)

turnCountdf = pd.DataFrame(timeoutIndexList, index = turnCountList)
st.line_chart(turnCountdf)

turnCount = st.text_input("Enter Turn Count: ", value="1")

if turnCount in turnCountDict: 
    df = pd.DataFrame.from_dict(turnCountDict[turnCount]).transpose()
        # df = pd.to_timedelta(df["strikerDelay"])
    st.write(df[(df["strikerDelay"] == "--") & (df["timeOutDelay"] == "--") & (df["switchTurnDelay"] == "--") & (df["turnCount"] == True) & (df["userGone"] == False)])
    m1 = df[df["strikerDelay"] != "--"]
    m2 = df[df["keeperDelay"] != "--" ]
    m3 = df[df["switchTurnDelay"] != "--"]
    m1 = pd.DataFrame(pd.to_timedelta(m1["strikerDelay"]))
    m2 = pd.DataFrame(pd.to_timedelta(m2["keeperDelay"]))
    m3 = pd.DataFrame(pd.to_timedelta(m3["switchTurnDelay"]))

    st.write("Striker Delay === |  Mean: " , m1["strikerDelay"].mean(), " | Max : " , m1["strikerDelay"].max(), " | Min : " , m1["strikerDelay"].min())
    st.write("Keeper Delay ==  | Mean: "  , m2["keeperDelay"].mean(), " | Max: ", m2["keeperDelay"].max(), " | Min: " , m2["keeperDelay"].min())
    st.write("Switch Turn Delay Mean: "  , m3["switchTurnDelay"].mean(), " | Max: ", m3["switchTurnDelay"].max(),  " | Min: ", m3["switchTurnDelay"].min())

    st.write("Number of games not ended: " , len(df[df["gameEnd"] == False]))
    st.write("Number of games where user gone handler called after 8.5 seconds: " , len(df[df["stuckGame"] == True]))
    st.write("Total games: ", len(df))

    st.write("Percentage of stuck games: " , len(df[df["stuckGame"] == True]) / len(df) * 100)

    st.write("Full Data for this turn Count")
    st.dataframe(df)
else:
    st.write("Displaying data only for turn count <= 10")