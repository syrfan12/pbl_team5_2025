# Python
# ラズパイで土壌センサーのデジタル値（HIGH/LOW）を読み取るサンプル

import RPi.GPIO as GPIO
import time

# GPIO番号指定のモード設定
GPIO.setmode(GPIO.BCM)

# センサーのDOピン番号
DO_PIN = 17

# ピンを入力モードに設定
GPIO.setup(DO_PIN, GPIO.IN)

try:
    while True:
        # デジタル値を取得
        sensor_value = GPIO.input(DO_PIN)
        
        if sensor_value == 0:
            print("土壌湿潤")
        else:
            print("土壌乾燥")
        
        time.sleep(1)  # 1秒ごとに値をチェック

except KeyboardInterrupt:
    print("終了します。")
finally:
    GPIO.cleanup()