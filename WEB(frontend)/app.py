from flask import Flask, render_template   # flask 모듈과 관련함수 불러옴

app = Flask(__name__)       # Flask라는 이름의 객체 생성
# GPIO.cleanup()

@app.route('/')                       # 기본 주소
def index():
    return render_template('index.html')
    #index2.html에 스위치의 눌림 여부 현황을 전달

if __name__ == "__main__":  # 웹사이트를 호스팅하여 접속자에게 보여주기 위한 부분
   app.run(host="0.0.0.0", port = "5000")
   # host는 현재 라즈베리파이의 내부 IP, port는 임의로 설정
   # 해당 내부 IP와 port를 포트포워딩 해두면 외부에서도 접속가능