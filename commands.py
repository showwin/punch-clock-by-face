import time

import picamera
from utils import say

COMMANDS_MAP = {
    'good morning': _punch_in,
    'hello': _punch_in,
    'ohio': _punch_in,
    'bye bye': _punch_out,
    'register': _register,
}


def command_handler(message):
    for key, func in COMMANDS_MAP.items():
        if key in message:
            func()


def _punch_in():
    say('おはようございます')


def _punch_out():
    say('お疲れ様でした')


def _register():
    say('登録を始めます')
    say('正面に立ってラズベリーマークを見てください')

    with picamera.PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.start_preview()
        time.sleep(2)  # 輝度調整のために最低2秒sleepする必要がある
        camera.capture('front.jpg')
        say('次にゆっくりと左右に顔を振ってください。５秒かけて左右にふるイメージです。')
        for i in range(10):
            camera.capture(f"side_{i}.jpg")
            time.sleep(0.5)
        say('撮影が完了しました。')
        camera.stop_preview()
