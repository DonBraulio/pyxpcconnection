# xpcconnection: OS X XPC Bindings for Python
#
# Copyright (c) 2015 Matthew Else
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from xpcconnection import XpcConnection
from threading import Event

import time

from uuid import UUID

class Connection(XpcConnection):
    def __init__(self, target, event):
        super(Connection, self).__init__(target)
        self.event = event

    def onEvent(self, data):
        msg_id = data['kCBMsgId']
        args = data['kCBMsgArgs']

        if msg_id == 6:
            # state changed
            STATE_TYPES = ['unknown', 'resetting', 'unsupported', 'unauthorized', 'poweredOff', 'poweredOn']
            print('State Changed: %s' % STATE_TYPES[args['kCBMsgArgState']])
        elif msg_id == 37:
            # discovered a device
            args.setdefault(None)

            rssi = args['kCBMsgArgRssi']
            uuid = UUID(bytes=args['kCBMsgArgDeviceUUID'])
            ad_data = args['kCBMsgArgAdvertisementData']

            print(rssi)
            print(uuid)
            print(ad_data)

    def onError(self, data):
        pass

    def handler(self, event):
        e_type, data = event

        if e_type == 'event':
            self.onEvent(data)
        elif e_type == 'error':
            self.onError(data)
        else:
            # que?
            pass

        self.event.set()

e = Event()

conn = Connection('com.apple.blued', e)

def init():
    # init
    init_data = {
        'kCBMsgArgName': 'py-' + str(time.time()),
        'kCBMsgArgOptions': {
            'kCBInitOptionShowPowerAlert': 0
        },
        'kCBMsgArgType': 0
    }

    conn.sendMessage({
        'kCBMsgId': 1,
        'kCBMsgArgs': init_data
    })

    e.wait()
    e.clear()

def startScanning():
    scan_data = {
        'kCBMsgArgOptions': {},
        'kCBMsgArgUUIDs': []
    }

    conn.sendMessage({
        'kCBMsgId': 29,
        'kCBMsgArgs': scan_data
    })

    e.wait()
    e.clear()

def stopScanning():
    conn.sendMessage({
        'kCBMsgId': 30,
        'kCBMsgArgs': None
    })

    e.wait()
    e.clear()



init()
startScanning()
e.stopScanning()
