# coding:utf-8


import sys
import requests
import time
import threading
from datetime import datetime
import codecs
import urllib3

dataFileNames = ['jing.txt', 'leon.txt']
# interval in second
presetInterval = 0.5
# duration in second
presetDuration = 2
req_Times = []

reload(sys)
sys.setdefaultencoding('utf8')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = 'https://oatoarray.zritc.com:9009/wms-c/reserve/customerOrder.do'

params = {
    'method': 'add',
}

# read default config
mInputs = []
for fileName in dataFileNames:
    status = 'waiting for cookie'
    data = ''
    cookie = ''
    with codecs.open(fileName, 'r', encoding='utf-8-sig') as f:
        for line in f.readlines():
            line = line.strip('\n')
            if status == 'waiting for cookie':
                if line == 'cookie':
                    status = 'cookie next'
                continue
            if status == 'cookie next':
                cookie = line
                status = 'waiting for data'
                continue
            if status == 'waiting for data':
                if line == 'data':
                    status = 'data next'
                continue
            if status == 'data next':
                # input is already Form-Url encoded
                if '&' in line and '=' in line:
                    data = line
                    continue

                # input is key: value pairs
                splits = line.split(':')
                if len(splits) < 2 or splits[1] == '':
                    continue
                if data != '':
                    data += '&'
                data += splits[0].strip() + '=' + splits[1].strip()
    if status == 'data next':
        mInput = {
            'headers': {
                'Cookie': cookie,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            'data': data
        }
        mInputs.append(mInput)
    else:
        print('failed loading data with status' + status)

print('=======================')
print('Loading data succeeded!')
print('=======================')
print(mInputs)


def action(index = None):
    print ('User ' + str(index) + ' POST at:')
    print datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    response = requests.post(base_url, headers=mInputs[index]['headers'], params=params, data=mInputs[index]['data'], verify=False)
    print ('User ' + str(index) + ' POST end at:')
    print datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    # print(response.content.decode())


class SetInterval:
    def __init__(self, interval, action, index):
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        self.index = index
        thread = threading.Thread(target=self._setInterval)
        thread.start()
        print('=======================')
        print ('User ' + str(i) + ' started at:')
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def _setInterval(self):
        nextTime = time.time()
        while not self.stopEvent.wait(nextTime - time.time()):
            nextTime += self.interval
            thread = threading.Thread(target=self.action, args=([self.index]))
            thread.start()

    def cancel(self):
        print('Canceled: ', self.index)
        self.stopEvent.set()

for i in range(len(mInputs)):
    mInput = mInputs[i]
    inter = SetInterval(presetInterval, action, i)
    t = threading.Timer(presetDuration, inter.cancel)

    t.start()
