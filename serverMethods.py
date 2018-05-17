from switchboard import *
import json
import serverDB
from bson import json_util

messageList = {}
messageNum = 0
socketList = dict()
appSocketList = dict()


def sentBoardInfoReq(nodeid):
    Msg = {'message_type': SB_BOARD_INFO_REQ}
    Msg['node'] = nodeid
    Msg['flags'] = 0
    return Msg


def sentStateChangeReq(nodeid, sbtype, self):
    Msg = {'message_type': SB_STATE_CHANGE_REQ}
    Msg['node'] = nodeid
    if(sbtype == SB_TYPE_4X4):
        switch1 = self.get_argument('switch1', default=None)
        switch2 = self.get_argument('switch2', default=None)
        switch3 = self.get_argument('switch3', default=None)
        switch4 = self.get_argument('switch4', default=None)
        Msg['sbType'] = SB_TYPE_4X4
        Msg['switch1'] = SW_TURN_ON if (switch1 == 'on') else SW_TURN_OFF
        Msg['switch2'] = SW_TURN_ON if (switch2 == 'on') else SW_TURN_OFF
        Msg['switch3'] = SW_TURN_ON if (switch3 == 'on') else SW_TURN_OFF
        Msg['switch4'] = SW_TURN_ON if (switch4 == 'on') else SW_TURN_OFF
        Msg['switch5'] = SW_DONT_CARE
        Msg['switch6'] = SW_DONT_CARE
        Msg['switch7'] = SW_DONT_CARE
        Msg['switch8'] = SW_DONT_CARE
    return Msg


def sentStateChangeReqForApp(nodeid, sbtype, message):
    Msg = {'message_type': SB_STATE_CHANGE_REQ}
    Msg['node'] = nodeid
    if(sbtype == SB_TYPE_4X4):
        switch1 = message['switch1']
        switch2 = message['switch2']
        switch3 = message['switch3']
        switch4 = message['switch4']
        Msg['sbType'] = SB_TYPE_4X4
        Msg['switch1'] = SW_TURN_ON if (switch1 == 'on') else SW_TURN_OFF
        Msg['switch2'] = SW_TURN_ON if (switch2 == 'on') else SW_TURN_OFF
        Msg['switch3'] = SW_TURN_ON if (switch3 == 'on') else SW_TURN_OFF
        Msg['switch4'] = SW_TURN_ON if (switch4 == 'on') else SW_TURN_OFF
        Msg['switch5'] = SW_DONT_CARE
        Msg['switch6'] = SW_DONT_CARE
        Msg['switch7'] = SW_DONT_CARE
        Msg['switch8'] = SW_DONT_CARE
    return Msg


def informWebClient(message):
    #TODO : Handle App socket connections
    mid = message['mid']
    global socketList
    print("mid is %d:" %mid)
    print(messageList)
    if mid in messageList:
        nodeList = serverDB.findHub(int(messageList[mid]['addr']))
        nodeList['serverPush'] = 'stateChange'
        nodeList['appSocketID'] = '0'
        if '_id' in nodeList:
            del nodeList['_id']
        msg = json.dumps(nodeList, default=json_util.default)
        messageList[mid]['value'] = 1
        hubAddr = int(messageList[mid]['addr'])
        if hubAddr in socketList:
            print(socketList[hubAddr])
            print("sending to browsers:%d" % len(socketList[hubAddr]))
            if len(socketList[hubAddr]) != 0:
                socketList[hubAddr][0].session.broadcast(socketList[hubAddr], msg)
                del messageList[mid]
        else:
            print("Not found in socket list")
            print(hubAddr)
    else:
        print("NO ACTIVE REQUEST FOUND FOR RESPONSE")


def processMsgFromClient(connection, clientMessage):
    clientMessage = json.loads(clientMessage)
    if clientMessage['message_type'] == SB_BOARD_INFO_RSP:
        print ("Info Response received")
        serverDB.updateNode(connection, clientMessage)
        informWebClient(clientMessage)
    elif clientMessage['message_type'] == SB_STATE_CHANGE_RSP:
        print ("State change Response received")
        connection.write_message(msg)
    elif clientMessage['message_type'] == SB_DEVICE_READY_NTF:
        print ("Hub is up and running")
        print("Message received %s\n" %clientMessage)
        serverDB.addHub(connection, clientMessage)
    elif clientMessage['message_type'] == SB_DEVICE_INFO_NTF:
        print("hub addr:%s" % format(clientMessage['hubAddr'], '#010x'))
        serverDB.addHubStates(clientMessage, connection)
