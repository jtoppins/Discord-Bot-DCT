#!/bin/python3

import time
import socket
import json

UDP_HOST = "localhost"
UDP_PORT = 8095

server = {
    "start": {
        "ver":1,
        "type":7,
        "header":"DCSEXPORT",
        "id":"78cce7cff12ed21baa6d159d6d9629bf",
        "data":1
    },
    "stop": {
        "ver":1,
        "type":7,
        "header":"DCSEXPORT",
        "id":"78cce7cff12ed21baa6d159d6d9629bf",
        "data":2
    },
    "heartbeat1": {
        "ver":1,
        "type":1,
        "header":"DCSEXPORT",
        "id":"78cce7cff12ed21baa6d159d6d9629bf",
        "data": {
            "time": {
                "hour":20,
                "min":37,
                "wday":4,
                "day":1,
                "month":6,
                "year":2011,
                "sec":0,
                "yday":152,
                "isdst":False
            },
            "time_left":119.32699999999999818
        }
    },
    "mission": {
        "ver":1,
        "type":2,
        "header":"DCSEXPORT",
        "id":"78cce7cff12ed21baa6d159d6d9629bf",
        "data": {
            "filename": "C:\\Users\\Ryan\\Saved Games\\DCS\\Missions\\VMFA169Checkride.miz",
            "restart_period":120,
            "theater":"Caucasus",
            "description":"",
            "mission":"VMFA169Checkride"
        }
    },
    "slots": {
        "ver":1,
        "type":5,
        "header":"DCSEXPORT",
        "id":"78cce7cff12ed21baa6d159d6d9629bf",
        "data": {
            "eom":True,
            "seqnum":7721,
            "slots": {
                "1": {
                    "type":"FA-18C_hornet",
                    "unitId":"1",
                    "countryName":"USA",
                    "onboard_num":"010",
                    "groupSize":4,
                    "role":"pilot",
                    "groupName":"VMFA-169",
                    "callsign":[1,1,1],
                    "task":"CAP",
                    "airdromeId":25
                },
                "12": {
                    "type":"FA-18C_hornet",
                    "unitId":"12",
                    "countryName":"USA",
                    "onboard_num":"014",
                    "groupSize":4,
                    "role":"pilot",
                    "groupName":"VMFA-169",
                    "callsign":[1,1,4],
                    "task":"CAP",
                    "airdromeId":25
                },
                "11": {
                    "type":"FA-18C_hornet",
                    "unitId":"11",
                    "countryName":"USA",
                    "onboard_num":"013",
                    "groupSize":4,
                    "role":"pilot",
                    "groupName":"VMFA-169",
                    "callsign":[1,1,3],
                    "task":"CAP",
                    "airdromeId":25
                },
                "2": {
                    "type":"FA-18C_hornet",
                    "unitId":"2",
                    "countryName":"USA",
                    "onboard_num":"011",
                    "groupSize":4,
                    "role":"pilot",
                    "groupName":"VMFA-169",
                    "callsign":[1,1,2],
                    "task":"CAP",
                    "airdromeId":25
                }
            }
        }
    },
    "players": {
        "ver":1,
        "type":3,
        "header":"DCSEXPORT",
        "id":"78cce7cff12ed21baa6d159d6d9629bf",
        "data": {
            "eom":True,
            "seqnum":24015,
            "players": {
                "1": {
                    "ping":0,
                    "side":0,
                    "id":1,
                    "name":"VMFA-169 | Terrificfool",
                    "pilotid":2117067,
                    "ucid":"78cce7cff12ed21baa6d159d6d9629bf",
                    "started":False,
                    "lang":"en",
                    "ipaddr":"97.102.255.236:10308"
                }
            }
        }
    },
    "players2": {
        "ver":1,
        "type":3,
        "header":"DCSEXPORT",
        "id":"78cce7cff12ed21baa6d159d6d9629bf",
        "data": {
            "eom":True,
            "seqnum":24015,
            "players": [
                {
                    "ping":0,
                    "side":0,
                    "id":1,
                    "name":"VMFA-169 | Terrificfool",
                    "pilotid":2117067,
                    "ucid":"78cce7cff12ed21baa6d159d6d9629bf",
                    "started":False,
                    "lang":"en",
                    "ipaddr":"97.102.255.236:10308"
                }
            ]
        }
    },
    "heartbeat2": {
        "ver":1,
        "type":1,
        "header":"DCSEXPORT",
        "id":"78cce7cff12ed21baa6d159d6d9629bf",
        "data": {
            "time": {
                "hour":20,
                "min":38,
                "wday":4,
                "day":1,
                "month":6,
                "year":2011,
                "sec":0,
                "yday":152,
                "isdst":False
            },
            "time_left": 59.320000000000000284
        },
    },
    "heartbeat3": {
        "ver":1,
        "type":1,
        "header":"DCSEXPORT",
        "id":"78cce7cff12ed21baa6d159d6d9629bf",
        "data": {
            "time": {
                "hour":20,
                "min":39,
                "wday":4,
                "day":1,
                "month":6,
                "year":2011,
                "sec":0,
                "yday":152,
                "isdst":False
            },
            "time_left": -0.68399999999999749889
        },
    },
}

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (UDP_HOST, UDP_PORT)
    sendorder = [
            ("start", 5),
            ("heartbeat1",5),
            ("mission", 2),
            ("slots", 2),
            ("players", 2),
            ("heartbeat2", 180),
            ("players2", 2),
            ("heartbeat3", 60),
            ("stop", 0),
    ]
    try:
        for item in sendorder:
            print("sending: " + item[0])
            sock.sendto(bytes(json.dumps(server[item[0]]), 'ascii'),
                    server_address)
            time.sleep(item[1])
    finally:
        sock.close()
