from flask import Flask, request, render_template   # flask 모듈과 관련함수 불러옴
import RPi.GPIO as GPIO     # 라즈베리파이 GPIO 관련 모듈을 불러옴
import time
import sys
from hx711 import HX711
from flask_cors import CORS, cross_origin

app = Flask(__name__)       # Flask라는 이름의 객체 생성
# GPIO.cleanup()
CORS(app) #CORS 허용

hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(205)
hx.reset()
hx.tare()

@app.route('/')
def home():
    return "HAPPY KURLY LIFE"


@app.route('/enter', methods=['GET','POST'])
def enter():
    if request.method == 'GET':
        return render_template('index.html', weight = 0, p_id = None)

    elif request.method == 'POST':
        val = hx.get_weight(5) / 1000
        hx.power_down()
        hx.power_up()
        weight = round(val, 2)
        p_id = request.form['p_id']
        print("weight : ", weight)
        print("identity value : ", p_id)
        return render_template('index.html', weight = weight, p_id = p_id)

@app.route('/happy', methods=['GET', 'POST'])
def happy():
    # json, keyvalue 로 넘겨주고 나서
    # 값 넘겨주고 바로 None 으로 바꿔버림!!!
    # 값이 None 이면 request에 이상한 거 넣어줌
    return 'PLEASE HAPPY'


if __name__ == "__main__":
   app.run(host="127.0.0.1", port = "5000")