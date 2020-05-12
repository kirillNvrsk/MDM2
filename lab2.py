import csv
from datetime import datetime

import chardet
import matplotlib.pyplot as mplt
import matplotlib.dates as mdates

FREE_MB = 1000
K = 1
PATH = '192.168.250.59.csv'
IP = '192.168.250.59'
DICT_KEYS = ['ts', 'ibyt']

# функция определения кодировки файла
def code_detecter(filename):
    try:
        with open(filename, 'rb') as code_file:
            data = code_file.read(512)
        code_file.close()
    except:
        return "utf-8"
    return chardet.detect(data)['encoding']

# функця чтение csv в лист словарей
def read_csv_to_list_of_dict(filename):
    with open(filename, encoding=code_detecter(filename)) as file:
        reader = list(csv.reader(file))
        indexes = [reader[0].index(i) for i in reader[0] if i in DICT_KEYS]
        count_of_col = len(DICT_KEYS)
        list_ = [[] for i in range(count_of_col)]
        count_of_str = len(reader)
        for i in range(1, count_of_str):
            if reader[i][0] == 'Summary':
                break
            for k, j in enumerate(indexes):
                list_[k].append(reader[i][j])
        dict_ = {}
        for i in range(0, count_of_col):
            dict_[DICT_KEYS[i]] = list_[i]
    return dict_


a = read_csv_to_list_of_dict(PATH)

# тарификация абонента
traffic = sum([int(i) for i in a['ibyt']])
print('Объем траффика: ', traffic, ' b, ', traffic/1000, 'Kb ', '\n', sep='')
payment = (traffic/1000 - FREE_MB) * K
print('Цена:', payment)

a['ibyt'] = [ int(i) for i in a['ibyt']]
a['ts'] = [datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in a['ts']]

time_byte = []
for i in range(0, len(a['ibyt'])):
    time_byte.append((a['ts'][i], a['ibyt'][i]))
time_byte.sort(key=lambda x: x[0])

for i, (t, b) in enumerate(time_byte):
    a['ts'][i], a['ibyt'][i] = t, b

traffic = {'time': [], 'byte': [] }

for i in range(0, len(a['ibyt'])):
    traffic['time'].append(a['ts'][i])
    traffic['byte'].append(a['ibyt'][i] / 1000)


time_byte = []
for i in range(0, len(traffic['time'])):
    time_byte.append((traffic['time'][i], traffic['byte'][i]))
time_byte.sort(key=lambda x: x[0])
for i, (t, b) in enumerate(time_byte):
    traffic['time'][i] = t
    traffic['byte'][i] = b

lst_time = []
lst_byte = []
i = 1
while i < len(traffic['time']):
    byte = traffic['byte'][i-1]
    time = traffic['time'][i-1]
    while i < len(traffic['time']) and traffic['time'][i-1] == traffic['time'][i]:
        byte += traffic['byte'][i]
        i += 1
    lst_byte.append(byte)
    lst_time.append(time)
    i += 1
traffic['time'] = lst_time
traffic['byte'] = lst_byte


fig = mplt.figure(figsize=(8,3))
ax = fig.add_subplot(111)
ax.set_ylim([0, 1400])
x = ax.xaxis
y = ax.yaxis
date_formatter = mdates.DateFormatter('%H:%M:%S')
date_locator = mdates.AutoDateLocator()
x.set_major_formatter(date_formatter)
x.set_major_locator(date_locator)
ax.set_xlabel('время')
ax.set_ylabel('трафик (кб)')
mplt.plot(traffic['time'], traffic['byte'])
mplt.show()