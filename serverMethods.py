import switchboard
from switchboard import *
import json
import serverDB

global_devlist = []
global_num_devices = 0

class dotslash_hub:
    def __init__(self,a,b):
        self.id = a
        self.conn = b
        self.nodes = []

class switch_node:
    def __init__(self, id, type, a, b, c, d):
        self.id = id
        self.type = type
        self.switch1 = a
        self.switch2 = b
        self.switch3 = c
        self.switch4 = d

def sentBoardInfoReq(nodeid):
    Msg = {'message_type': SB_BOARD_INFO_REQ}
    Msg['node'] = nodeid
    Msg['flags'] = 0
    return Msg

def sentStateChangeReq(nodeid, sbtype, self):
    Msg = {'message_type': SB_STATE_CHANGE_REQ}
    Msg['node'] = nodeid
    if(sbtype == SB_TYPE_4X4):
        switch1 = self.get_argument('switch1')
        switch2 = self.get_argument('switch2')
        switch3 = self.get_argument('switch3')
        switch4 = self.get_argument('switch4')
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

def processMsgFromClient(connection, clientMessage):
    clientMessage = json.loads(clientMessage)
    if clientMessage['message_type'] == SB_BOARD_INFO_RSP:
        print ("Info Response received")
#TBD
        #serverDB.updateNode(connection, clientMessage)
        for device in global_devlist:
            if(device.conn == connection):
                id = clientMessage['devIndex'] - 1
                device.nodes[id].switch1 = clientMessage['switch1']
                device.nodes[id].switch2 = clientMessage['switch2']
                device.nodes[id].switch3 = clientMessage['switch3']
                device.nodes[id].switch4 = clientMessage['switch4']
    elif clientMessage['message_type'] == SB_STATE_CHANGE_RSP:
        print ("State change Response received")
        #Request updated node info as well
        msg = sentBoardInfoReq(clientMessage['devIndex'])
        connection.write_message(msg)
    elif clientMessage['message_type'] == SB_DEVICE_READY_NTF:
        print ("Hub is up and running")
        print("Message received %s\n" %clientMessage)
        global_num_devices = 1
        if global_num_devices not in [hub.id for hub in global_devlist]:
            device = dotslash_hub(global_num_devices, connection)
            global_devlist.append(device)
        print ("Total Devices %i" % len(global_devlist))
        clientMessage['hubAddr'] = 0x0102030405060708
        serverDB.addHub(connection, clientMessage)
    elif clientMessage['message_type'] == SB_DEVICE_INFO_NTF:
        print("hub addr:%s" % format(clientMessage['hubAddr'], '#010x'))
        serverDB.addHubStates(clientMessage, connection)
