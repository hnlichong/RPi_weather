#! /usr/bin/env python3
"""
main的压力测试，连续环境监控、发送SOS
"""
import csv
import numpy as np
import pickle
from datetime import datetime

from sx1278 import sx1278
from ms8607 import ms8607
from as3935 import as3935
from up501 import up501
from time import sleep
from led import led
from utils import my_logger
import os

logger = my_logger(__name__, level="DEBUG")
root_path = os.path.dirname(os.path.abspath(__file__))


def read_environment():
    while 1:
        temperatue, pressure = ms8607.get_temperature_pressure()
        humidity = ms8607.get_humidity()
        print(
            'temperature: {} degrees Celsius, pressure: {} mbar, relative humidity: {} %RH'.format(temperatue, pressure,
                                                                                                   humidity))
        sleep(1)

def append_data_to_file(data, row_fields, path, now = datetime.now()):
    f_name = now.strftime('%Y%m%d') + '.csv'
    f_path = os.path.join(path, f_name)
    if not os.path.exists(f_path):
        with open(f_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row_fields)
            writer.writerow(data)
    else:
        with open(f_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(data)

def send_SOS():
    """报警，红灯闪烁，发送位置信息"""
    led.on('RED')
    gps = up501.read()
    sx1278.send_str(gps)
    logger.debug('send_SOS ok!')
    led.off('RED')

def send_SOS_repeat(times):
    return [send_SOS() for i in range(times)]

def send_SOS_repeat_gen(times):
    def wrapper():
        send_SOS_repeat(times)
    return wrapper

def import_model():
    """
    example:
        res = clf.predict([22.2, 92.2, 1000.1])
    """
    clf = None
    with open('knn.pickle', 'rb') as fr:
        clf = pickle.load(fr)
    return clf

def main():
    # 系统启动后黄灯亮
    led.on('YELLOW')

    # 导入预测模型
    clf = import_model()
    if clf is None:
        raise Exception('模型导入失败！')

    # 报警函数, 重复5次
    sos_cb = send_SOS_repeat_gen(5)

    # 日志配置
    env_path = os.path.join(root_path, 'env_data')
    env_fields = ['datetime', 'temperature(℃)', 'humidity(%)', 'pressure(mbar)', 'hazardous']
    lightning_path = os.path.join(root_path, 'lightning_data')
    lightning_fields = ['datetime', 'events', 'distance(KM)', 'hazardous']
    os.makedirs(env_path, exist_ok=True)
    os.makedirs(lightning_path, exist_ok=True)

    def env_monitor():
        # 读取测量数据
        temperatue, pressure = ms8607.get_temperature_pressure()
        humidity = ms8607.get_humidity()
        # 预测是否下雨, 是则报警
        mx = np.array([temperatue, humidity, pressure]).reshape(1, -1)
        res = clf.predict(mx)[0]
        # 写入日志
        now = datetime.now()
        data = [now.strftime('%Y%m%d%H%M%S'), temperatue, humidity, pressure, res]
        append_data_to_file(data, env_fields, env_path, now)
        logger.debug(data)
        # 报警
        if res:
            sos_cb()

    def lightning_monitor():
        # 读取数据
        distance = as3935.get_distance()
        events = as3935.get_INT_res()
        res = False
        # 闪电事件为8
        if events == 0x08:
            res = True
        # 写入日志
        now = datetime.now()
        data = [now.strftime('%Y%m%d%H%M%S'), events, distance, res]
        append_data_to_file(data, lightning_fields, lightning_path, now)
        logger.debug(data)


    # 绑定事件, 事件回调的实时性比定时监控更强
    # 如有闪电发生，则报警
    as3935.lightning_cbs.append(sos_cb)

    # 执行定时监控任务
    while True:
        env_monitor()
        lightning_monitor()
        sos_cb()
        # sleep(5)
        pass

if __name__ == '__main__':
    main()
