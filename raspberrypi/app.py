from os import P_PID
from flask import Flask, request, jsonify, render_template   # flask 모듈과 관련함수 불러옴
from flask_jsonpify import jsonpify
import RPi.GPIO as GPIO     # 라즈베리파이 GPIO 관련 모듈을 불러옴
import time
import sys
from hx711 import HX711
from flask_cors import CORS, cross_origin

app = Flask(__name__)       # Flask라는 이름의 객체 생성
# GPIO.cleanup()
CORS(app) #CORS 허용
app.config['CORS_HEADERS'] = 'Content-Type'

hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(205)
hx.reset()
hx.tare()
# global weight
# weight = 0
# global p_id
# p_id = 0

@app.route('/')                 
def home():
    return "append '/enter' after the url"
    

@app.route('/enter', methods=['GET','POST'])
def enter():
    if request.method == 'GET':
        return render_template('varcode.html', p_id = None)

    elif request.method == 'POST':
        val = hx.get_weight(5) / 1000
        hx.power_down()
        hx.power_up()
        global weight
        weight = round(val, 2)
        global p_id
        p_id = request.form['p_id']
        print("weight : ", weight)
        print("identity value : ", p_id)
        return render_template('varcode.html', p_id = p_id)

@app.route('/real_weight', methods=['GET'])
@cross_origin(allow_headers=['Content-Type'])
def real_weight():
    # json, keyvalue 로 넘겨주고 나서
    # 값 넘겨주고 바로 None 으로 바꿔버림!!!
    # 값이 None 이면 request에 이상한 거 넣어줌
    if request.method == 'GET':
        
        print(request)
        r_id, r_weight = happy()
        print(r_id, r_weight)
        return jsonpify({ 'weight' : r_weight, 'barcode' : r_id})

def happy():
    global p_id
    global weight
    id = p_id
    p_id = None
    wt = weight
    weight = 0
    return id, wt


if __name__ == "__main__":  
   app.run(host="127.0.0.1", port = "5000")
