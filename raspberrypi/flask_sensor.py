from flask import Flask, render_template   # flask 모듈과 관련함수 불러옴
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
weight = 0


@app.route('/')                       # 기본 주소
def home():
    return "HAPPY KURLY LIFE"


@app.route('/enter', methods=['POST'])
def enter_value():
    val = hx.get_weight(5) / 1000
    hx.power_down()
    hx.power_up()
    weight = round(val, 2)

    if request.method == 'POST':
        temp = request.form['nm']

    return render_template('index.html', weight = weight, p_id = temp)
    # 바코드 번호를 enter하면 html에서 값 상태를 보여줌.


if __name__ == "__main__":  # 웹사이트를 호스팅하여 접속자에게 보여주기 위한 부분
   app.run(host="0.0.0.0", port = "5000")
   # host는 현재 라즈베리파이의 내부 IP, port는 임의로 설정
   # 해당 내부 IP와 port를 포트포워딩 해두면 외부에서도 접속가능