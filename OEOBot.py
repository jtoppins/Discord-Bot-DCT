#!/bin/env python3

import time
import datetime
import json
import threading
import enum
import socket
import configparser
import asyncio
import discord
from discord.ext import commands

class DCSMsgType(enum.Enum):
    HEARTBEAT       = 1
    MISSIONINFO     = 2
    PLAYERINFOSTART = 3
    PLAYERINFOCONT  = 4
    SLOTINFOSTART   = 5
    SLOTINFOCONT    = 6
    STATE           = 7

class DCSServerState(enum.Enum):
    UNKNOWN = 0
    STARTED = 1
    STOPPED = 2
    PAUSED  = 3

class MissionInfo:
    def __init__(self, msninfo):
        self.theater        = msninfo['theater']
        self.name           = msninfo['mission']
        self.filename       = msninfo['filename']
        self.description    = msninfo['description']
        self.restart_period = msninfo['restart_period']
        self.local_time     = None
        self.time_left      = None
        self.slots          = dict()

    def updateTimes(self, times):
        self.local_time = (
            times['time']['year'],
            times['time']['month'],
            times['time']['day'],
            times['time']['hour'],
            times['time']['min'],
            times['time']['sec'],
            times['time']['wday'],
            times['time']['yday'],
            0)
        self.time_left = times['time_left']

    def addSlot(self, slot):
        self.slots[str(slot['unitId'])] = slot

def seq_iter(obj):
    return obj if isinstance(obj, dict) else range(len(obj))

class Players:
    def __init__(self, players):
        self.players = dict()
        for i in seq_iter(players):
            self.players[players[i]['ucid']] = players[i]

    def __len__(self):
        return len(self.players)

    def update(self, player):
        self.players[player['ucid']] = player

class DCSServer:
    def __init__(self, uid):
        self.uid       = uid
        self.status    = DCSServerState.UNKNOWN
        self.players   = None
        self.mission   = None
        self.last_hb   = None

    def rcvMsg(self, msg):
        if DCSMsgType.HEARTBEAT.value == msg['type']:
            self.last_hb = time.time()
            if self.mission is None:
                return
            self.mission.updateTimes(msg['data'])
        elif DCSMsgType.MISSIONINFO.value == msg['type']:
            self.mission = MissionInfo(msg['data'])
        elif DCSMsgType.PLAYERINFOSTART.value == msg['type']:
            if not bool(msg['data']['eom']):
                return
            self.players = Players(msg['data']['players'])
        elif DCSMsgType.PLAYERINFOCONT.value == msg['type']:
            pass
            # not supported, look at changing the protocol to
            # where each slot and player are sent in individual
            # messages
        elif DCSMsgType.SLOTINFOSTART.value == msg['type']:
            if not bool(msg['data']['eom']) or self.mission is None:
                return
            for key, slot in msg['data']['slots'].items():
                self.mission.addSlot(slot)
        elif DCSMsgType.SLOTINFOCONT.value == msg['type']:
            pass
        elif DCSMsgType.STATE.value == msg['type']:
            if msg['data'] == DCSServerState.STARTED.value:
                self.status = DCSServerState.STARTED
            elif msg['data'] == DCSServerState.STOPPED.value:
                self.status = DCSServerState.STOPPED
            elif msg['data'] == DCSServerState.PAUSED.value:
                self.status = DCSServerState.PAUSED
        else:
            pass

class DCSServerDB:
    def __init__(self):
        self.default = None
        self.servers = dict()
    def __getitem__(self, key):
        return self.servers[key]
    def __contains__(self, key):
        return (key in self.servers)
    def keys(self):
        return self.servers.keys()
    def rcvMsg(self, msg):
        data = json.loads(msg)
        if data['id'] in self.servers:
            server = self.servers[data['id']]
        else:
            server = DCSServer(data['id'])
            self.servers[data['id']] = server
        if self.default is None:
            self.default = server.uid
        server.rcvMsg(data)

def receive_messages(connectinfo, db):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(connectinfo)
    with sock:
        while True:
            data, addr = sock.recvfrom(2**16)
            db.rcvMsg(data)

def build_server_info(server):
    if server is None:
        return "no data for server"
    msg = "server: {}\n".format(server.uid) + \
          "status: {}\n".format(server.status.name)
    if server.mission is not None and \
       server.mission.local_time is not None:
        tleft = datetime.timedelta(seconds=int(server.mission.time_left))
        period = datetime.timedelta(seconds=server.mission.restart_period)
        msg += "mission: {}\n".format(server.mission.name)
        msg += "theater: {}\n".format(server.mission.theater)
        msg += time.strftime("local time: %Y-%m-%d %H:%M \n",
                    server.mission.local_time)
        msg += "restarts in: {}\n".format(tleft)
        msg += "restart period: {}\n".format(period)
    if server.players is not None:
        msg += "players: {}/{}\n".format(len(server.players), 60)
    return msg

def build_server_list(ids):
    if ids is None:
        return "no known servers"
    return '\nKnown Servers\n-------------\n' + '\n'.join(ids)

def bot_setup(dcsserverdb):
    description = '''DCT Discord Bot

Pulls information from DCT enabled servers to report things such as server status and in the future stats.'''

    bot = commands.Bot(command_prefix='!',
            description=description,
            case_insensitive=True)

    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Game("starting"))
        print("discord bot ready")

    @bot.group(
        brief="Get information about a DCS server")
    async def server(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid command see usage...')

    @server.command(name='list',
        brief=" - list IDs of known servers",
        usage="server list")
    async def server_list(ctx):
        await ctx.send(build_server_list(dcsserverdb.keys()))

    @server.command(name='info',
        brief=" - get info about a specific server",
        usage="[id]")
    async def server_info(ctx, server_id=None):
        if server_id is None:
            server_id = dcsserverdb.default
        if server_id not in dcsserverdb:
            await ctx.send("no info for server '{}'".format(server_id
                or 'default'))
            return
        await ctx.send(build_server_info(dcsserverdb[server_id]))

    return bot


def main():
    config = configparser.ConfigParser()
    config.read_string(
"""
[DCS]
address = localhost
port = 8095
heartbeat_timeout = 4
"""
    )
    config.read('bot.cfg')
    dcsserverdb = DCSServerDB()
    bot = bot_setup(dcsserverdb)
    server = threading.Thread(target=receive_messages,
            args=((config['DCS']['address'], config.getint('DCS','port')),
                    dcsserverdb))
    server.start()
    async def status_update(bot, db):
        await bot.wait_until_ready()
        while True:
            if db.default is not None:
                server = db[db.default]
                msg = "{};".format(server.status.name)
                if server.players is None or server.mission is None or \
                    server.mission.time_left is None:
                    msg += " P: 0/0; R: ??:??"
                else:
                    msg += " P: {}/{}; R: {}".format(
                            len(server.players),
                            60,
                            datetime.timedelta(
                                seconds=int(server.mission.time_left)))
                await bot.change_presence(activity=discord.Game(msg))
            await asyncio.sleep(10)
    bot.loop.create_task(status_update(bot, dcsserverdb))
    bot.run(config['discord']['token'])

if __name__ == "__main__":
    main()
