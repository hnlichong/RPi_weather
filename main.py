#! /usr/bin/env python3
import csv
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

    # 记录环境数据
    env_path = os.path.join(root_path, 'env_data')
    env_fields = ['datetime', 'temperature(℃)', 'humidity(%)', 'pressure(mbar)']
    lightning_path = os.path.join(root_path, 'lightning_data')
    lightning_fields = ['datetime', 'events', 'distance(KM)']
    os.makedirs(env_path, exist_ok=True)
    os.makedirs(lightning_path, exist_ok=True)

    def env_monitor():
        # nonlocal env_path, env_fields
        temperatue, pressure = ms8607.get_temperature_pressure()
        humidity = ms8607.get_humidity()
        now = datetime.now()
        data = [now.strftime('%Y%m%d%H%M%S'), temperatue, humidity, pressure]
        logger.debug(data)
        # write into file
        append_data_to_file(data, env_fields, env_path, now)
        # 预测是否下雨, 是则报警
        res = clf.predict([temperatue, humidity, pressure])
        if res:
            logger.debug('下雨！')
            sos_cb()


    def lightning_monitor():
        distance = as3935.get_distance()
        events = as3935.get_INT_res()
        now = datetime.now()
        data = [now.strftime('%Y%m%d%H%M%S'), events, distance]
        logger.debug(data)
        # write into file
        append_data_to_file(data, lightning_fields, lightning_path, now)


    # 绑定事件
    # 如有闪电发生，则报警
    as3935.lightning_cbs.append(sos_cb)

    # 执行循环监控任务
    while True:
        env_monitor()
        lightning_monitor()
        sleep(5)
        pass

if __name__ == '__main__':
    main()
