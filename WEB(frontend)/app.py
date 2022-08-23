from flask import Flask, request, render_template, redirect, session
from flask_jsonpify import jsonpify
from datetime import datetime
import requests
import bcrypt
import re


BACKEND_ADDRESS = "http://127.0.0.1:5000"

app = Flask(__name__)
app.secret_key = "123456129efl32089df@#$fd"


@app.route('/', methods=['GET'])
def index():
    if 'user_id' in session:
        return redirect('/main')
    return redirect('login')

@app.route('/main', methods=['GET'])
def page_main():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def page_login():
    form = {'id': '', 'pw': ''}
    
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect('/main')
        return render_template('login.html', form=form)
    else:
        form['id'] = request.form['username']
        form['pw'] = request.form['password']
        
        if try_login(form):
            return redirect('/main')
    
    return render_template('login.html', form=form)

def try_login(form):
    print(form['id'], form['pw'])
    
    # 아이디: 영문, 숫자조합 5~19글자
    # 비밀번: 영문, 숫자, 특수문자 조합 8~16글자
    #정규식이 잘 안되네요 ㅎㅎ
    id_re = re.compile('/^[A-Za-z]+[A-Za-z0-9]{5,19}$/g')
    pw_re = re.compile('/^(?=.*[a-zA-z])(?=.*[0-9])(?=.*[$`~!@$!%*#^?&\\(\\)\-_=+]).{8,16}$/')

    print(id_re.match(form['id']), pw_re.match(form['pw']))
    if id_re.match(form['id']) == None or pw_re.match(form['pw']) == None:
        return False
    
    password = requests.post(BACKEND_ADDRESS + "/get/password", json={'user_id': form['id']}).text
    bcrypt_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    if form['pw'] == bcrypt_pw:
        session['user_id'] = form['id']
        return True
    
    return False

###################### APIs ########################

@app.route('/api/logout', methods=['POST'])
def log_out():
    session.pop('user_id')
    return redirect('/login')


@app.route('/api/main/exp_weight')
def get_exp_weight():
    return requests.post(BACKEND_ADDRESS + "/weight").json()

@app.route('/api/main/result')
def get_result():
    data = request.get_json()
    data['user_key'] = session['user_id']
    data['finish_time'] = datetime.now().strftime('%Y %m %d %H %M %S')

    requests.post(BACKEND_ADDRESS + "/save/weight", json=data)
    
    return 'saved'

################# T  E  S  T ##################

@app.route('/api/bi')
def get_bcrypt_str():
    password = request.args.get('pw')
    bcrypt_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    return bcrypt_pw

@app.route('/api/test1')
def test():
    path = request.path
    host = request.host_url
    
    return {"path":path, "host": host}

@app.route('/api/test2')
def test2():
    return requests.post(BACKEND_ADDRESS + "/get/password", json={'user_id': "A00004689"}).text

@app.route('/real_weight2')
def test3():
    weight = 456789
    p_id = None
    return jsonpify({'weight': weight, 'barcode': p_id})

if __name__ == "__main__":
   app.run()
   