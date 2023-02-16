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
appPausedTimeDict = {}
gameEndDict = {}
turnCountDict = {}
userGoneHandlerDict = {}
appPauseFlag = {}
stuckGames = {}

switchtime = ""


basetime = "00:00:08,500"
timeDelta =  datetime.strptime(basetime, "%H:%M:%S,%f") - datetime.strptime("00:00:00,100", "%H:%M:%S,%f")
for turnCount in range(1, 3): 
    turnCount = str(turnCount)
    switchtime = ""
    turnCountFlag = {}
    prev_line = None
    for line in lines:
        line = line.decode()
        roomName = ""
        if "SFS_PlayerId: 1" in line and "Request Message: ready" in line:
            roomName = line.split("Room_name: ", 1)[1].split(";")[0]
            if roomName not in roomNamesList:
                roomNamesList.append(roomName)
            appPauseFlag[roomName] = False
            if turnCount == '1':
                turnCountFlag[roomName] = True

        if ("SFS_PlayerId: 1" in line or "SFS_PlayerId: 2" in line) and "Response Message: switch_turn" in line and "Turn_count: " + turnCount + ";" in line:
            roomName = line.split("Room_name: ", 1)[1].split(";")[0]
            switchtime = line.split(" | ")[1]
            switchTurnTimeDict[roomName] = switchtime
            
            turnCountFlag[roomName] = True
        
        if ("SFS_PlayerId: 1" in line or "SFS_PlayerId: 2" in line) and "Response Message: striker_response" in line and "Turn_count: " + turnCount + ";" in line:
            roomName = line.split("Room_name: ", 1)[1].split(";")[0]
            time = line.split(" | ")[1]
            strikerResponseTimeDict[roomName] = time
            turnCountFlag[roomName] = True

        if ("SFS_PlayerId: 1" in line or "SFS_PlayerId: 2" in line) and "Response Message: keeper_response" in line and "Turn_count: " + turnCount + ";" in line:
            roomName = line.split("Room_name: ", 1)[1].split(";")[0]
            time = line.split(" | ")[1]
            keeperResponseTimeDict[roomName] = time
            turnCountFlag[roomName] = True


        if ("SFS_PlayerId: 1" in line or "SFS_PlayerId: 2" in line) and "Response Message: switch_turn" in line and "Turn_count: " + str(int(turnCount) + 1) + ";" in line:
            roomName = line.split("Room_name: ", 1)[1].split(";")[0]
            time = line.split(" | ")[1]
            nextSwitchTurnTimeDict[roomName] = time
            turnCountFlag[roomName] = True

        if ("SFS_PlayerId: 1" in line or "SFS_PlayerId: 2" in line)  and "Response Message: timeout" in line and "Turn_count: " + turnCount + ";" in line:
            roomName = line.split("Room_name: ", 1)[1].split(";")[0]
            time = line.split(" | ")[1]
            timeoutTimeDict[roomName] = time
            turnCountFlag[roomName] = True

        if "Request Message: app_paused" in line and "Turn_count: " + turnCount + ";" in line:
            roomName = line.split("Room_name: ", 1)[1].split(";")[0]
            time = line.split(" | ")[1]
            appPauseFlag[roomName] = True
            turnCountFlag[roomName] = True

    
        if "Response Message: sync_time" in line and "Turn_count: " + turnCount + ";" in line:
            roomName = line.split("Room_name: ", 1)[1].split(";")[0]
            time = line.split(" | ")[1]
            appPauseFlag[roomName] = False
            turnCountFlag[roomName] = True
        

        if "Winner_player_ID" in line: 
            roomName = line.split("Room_name: ", 1)[1].split(";")[0]
            # time = line.split(" | ")[1]

            # time = datetime.strptime(time, "%H:%M:%S,%f")
            # if switchtime != "" and type(switchtime) == str:
            #     switchtime = datetime.strptime(switchtime, "%H:%M:%S,%f")

            
            # if switchtime != "" and time - switchtime < timeDelta:
            gameEndDict[roomName] = True
            # else:
            #     gameEndDict[roomName] = False

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

                # print(line, "prev line: ", prev_line)
                # print(time, " prevTime: ",  prevTime)
                if time - prevTime > timeDelta :
                    stuckGames[roomName] = True


        if roomName in appPauseFlag:
            appPausedTimeDict[roomName] = appPauseFlag[roomName]
        
        

    timeDelayDict = {}


    for roomName in roomNamesList:

        if roomName in switchTurnTimeDict:
            switchTime = datetime.strptime(switchTurnTimeDict[roomName], "%H:%M:%S,%f")
        else:
            switchTime = -1
        
        if roomName in strikerResponseTimeDict:
            strikerTime = datetime.strptime(strikerResponseTimeDict[roomName], "%H:%M:%S,%f")
        else:
            strikerTime = -1

        if roomName in keeperResponseTimeDict:
            keeperTime = datetime.strptime(keeperResponseTimeDict[roomName], "%H:%M:%S,%f")
        else:
            keeperTime = -1

        if roomName in nextSwitchTurnTimeDict:
            nextSwitchTime = datetime.strptime(nextSwitchTurnTimeDict[roomName], "%H:%M:%S,%f")
        else:
            nextSwitchTime = -1

        if roomName in timeoutTimeDict:
            timeoutTime = datetime.strptime(timeoutTimeDict[roomName], "%H:%M:%S,%f")
        else:
            timeoutTime = -1
        
        # print("FOR ROOM " + roomName)
        if strikerTime != -1 and switchTime != -1: 
            # print("Delay in striker respone and switch turn: ", strikerTime - switchTime)
            timeDelayDict[roomName] = {"strikerDelay" : strikerTime - switchTime}

        else:
            timeDelayDict[roomName] = {"strikerDelay" : "--"}
        
        if strikerTime != -1 and keeperTime != -1: 
            # print("Delay in keeper response and striker response: ", keeperTime - strikerTime)
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

        if roomName in appPausedTimeDict:
            timeDelayDict[roomName].update({"appPaused" : appPausedTimeDict[roomName]})
        else:
            timeDelayDict[roomName].update({"appPaused" : False})
        
        if roomName in gameEndDict:
            timeDelayDict[roomName].update({"gameEnd" : gameEndDict[roomName]})
        else:
            timeDelayDict[roomName].update({"gameEnd" : False})

        if roomName in turnCountFlag:
            timeDelayDict[roomName].update({"turnCount" : True})
        else:
            timeDelayDict[roomName].update({"turnCount" : False})

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

# print(timeDelayDict)
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
    timeoutIndex = len(df[(df["strikerDelay"] == "--") & (df["timeOutDelay"] == "--") & df["turnCount"] == True])
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


    timeDelta = pd.Timedelta(seconds=8, microseconds=500)
    strikerIndex = len(m1[m1["strikerDelay"] > timeDelta])
    strikerIndexList.append(strikerIndex)
    checkIndexStriker = strikerIndex +  len(m1[m1["strikerDelay"] > timeDelta])
    totalIndexStiker = len(m1["strikerDelay"])

    switchIndex = len(m3[m3["switchTurnDelay"] > timeDelta])
    switchTurnList.append(switchIndex)
    checkIndexSwitchTurn = checkIndexSwitchTurn + switchIndex
    totalIndexSwitchTurn = len(m3["switchTurnDelay"])


# turnCountList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
turnCountList = [1, 2]



serverHealthPercent = 100 - ((checkIndexStriker + checkIndexSwitchTurn + checkIndexTimeout)/(totalIndexStiker + totalIndexSwitchTurn + totalIndexTimeout) *  100)

st.title("Server Health: " + str(serverHealthPercent) + "%")

st.write("Percentage of games with no striker and keeper response and no timeout: " , timeoutIndexList[0]/totalGames * 100)

turnCountdf = pd.DataFrame(timeoutIndexList, index = turnCountList)
st.line_chart(turnCountdf)

# print(len(roomNamesList))
# print(len(userGoneHandlerDict))
st.write(" User gone handler event ")

userGonePercent = len(userGoneHandlerDict)/len(roomNamesList) *  100
st.write("Percentage of games ended by user gone : " , userGonePercent)


turnCount = st.text_input("Enter Turn Count: ", value="1")

if turnCount in turnCountDict: 
    df = pd.DataFrame.from_dict(turnCountDict[turnCount]).transpose()
        # df = pd.to_timedelta(df["strikerDelay"])
    st.table(df[(df["strikerDelay"] == "--") & (df["timeOutDelay"] == "--") & df["turnCount"] == True])
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
    st.dataframe(df)
else:
    st.write("Displaying data only for turn count <= 10")