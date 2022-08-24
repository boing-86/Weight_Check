from flask import Flask, request
from os import environ
import random
import pymysql
import json
import math

app = Flask(__name__)

if not environ.get('KurlyCheckDbHost') and not environ.get('KurlyCheckDbPort') and\
        not environ.get('KurlyCheckDbUser') and not environ.get('KurlyCheckDbPswd'):
    print("\033[31mBackend(app.py) : make environment variable for db server connection!\033[0m")

mysql = pymysql.connect(host=environ.get('KurlyCheckDbHost'),  # Endpoint
                        port=int(environ.get('KurlyCheckDbPort')),  # Endpoint Port
                        user=environ.get('KurlyCheckDbUser'),
                        password=environ.get('KurlyCheckDbPswd'),
                        database='kdb',  # Schema Name
                        charset="utf8mb4")


@app.route('/')
def hello_world():
    return 'Hello Backend World!'


# 물건 무게 평균, 표준편차 구하기
def get_weight_mean_std():
    data = request.get_json()
    barcode_id = data['id']
    is_picking_zone = barcode_id[0] == 'P'
    
    with mysql.cursor() as cursor:
        # 피킹/DAS 상품 json 불러오기
        if is_picking_zone:
            cursor.execute(
                f"SELECT product_list, basket_id FROM picking_product_basket WHERE picking_id='{barcode_id}'")
        else:
            cursor.execute(
                f"SELECT product_list, basket_id "
                f"FROM das_product_basket db join customer_order co on db.order_id = co.order_id "
                f"WHERE das_id='{barcode_id}'")
        
        products_string, basket_id = cursor.fetchone()
        products_json = json.loads(products_string)

        # 바구니 무게 더하기
        cursor.execute(
            f"SELECT b_weight_avg, b_weight_std FROM basket WHERE basket_id='{basket_id}'")
        mean, std = cursor.fetchone()
        std *= std
        
        # DB 에서 상품 평균, 표준 편차 구하기
        for name, count in products_json.items():
            cursor.execute(
                f"SELECT p_weight_avg, p_weight_std FROM product WHERE product_id='{name}'")
            p_avg, p_std = cursor.fetchone()
            
            mean += count * p_avg
            std += count * (p_std ** 2)
        std = math.sqrt(std)
    return mean, std


# 예상 상품 무게 불러오기
@app.route('/weight', methods=['POST'])
def get_weight_sum():
    mean, std = get_weight_mean_std()
    
    min_weight = mean - 3*std
    max_weight = mean + 3*std
    
    return json.dumps({'min': min_weight, 'max': max_weight})


# 작업을 성공적으로 마침
@app.route('/save/weight', methods=['POST'])
def save_working_data():
    data = request.get_json()
    user_id, finish_time, real_weight, barcode_id\
        = (data[s] for s in ['user_key', 'finish_time', 'weight', 'id'])
    
    zone = barcode_id[0] == 'P' and 'picking' or 'das'
    z = zone[0]
    
    with mysql.cursor() as cursor:
        cursor.execute(
            f"UPDATE {zone}_product_basket SET user_id='{user_id}', {z}_finish_time='{finish_time}',"
            f" {z}_real_weight={real_weight}, {z}_finish=true WHERE {zone}_id='{barcode_id}'")
        
    working_fail()
    return 'saved'


# 작업에 실패함
@app.route('/working_fail', methods=['POST'])
def working_fail():
    barcode_id = request.get_json()['id']
    
    zone = barcode_id[0] == 'P' and 'picking' or 'das'
    z = zone[0]
    
    with mysql.cursor() as cursor:
        cursor.execute(
            f"UPDATE {zone}_product_basket SET {z}_count={z}_count+1 WHERE {zone}_id='{barcode_id}'")
        mysql.commit()
    return "saved"


# 강제로 작업 완료를 함 (로그를 남김)
@app.route('/update/force', methods=['POST'])
def save_working_error():
    mean, std = get_weight_mean_std()
    barcode_id = request.get_json()['id']
    
    with mysql.cursor() as cursor:
        cursor.execute(
            f"INSERT INTO product_error (order_id, predict_avg, predict_std)"
            f"VALUES ('{barcode_id}', {mean}, {std})")
        mysql.commit()
    return "saved"


# error list api
@app.route('/product/error_list', methods=['GET'])
def get_error_list():
    with mysql.cursor() as cursor:
        cursor.execute("SELECT * FROM product_error")
        data = cursor.fetchall()
    return json.dumps({'column': ('id', 'order_id', 'predict_avg', 'predict_std'), 'data': data})


# Analysis Product Picking/Das Error Counts
@app.route('/analysis/time', methods=['GET'])
def get_time_analysis():
    date = request.get_json()['date']
    
    with mysql.cursor() as cursor:
        cursor.execute(
            f"SELECT DATE_FORMAT(p_finish_time, '%H') AS hour, (sum(p_count)-count(*))/sum(p_count) AS proba "
            f"FROM picking_product_basket "
            f"WHERE user_id IS NOT NULL AND DATE(p_finish_time)='{date}' "
            f"GROUP BY hour ORDER BY proba DESC")
        data = cursor.fetchall()
        
    return {'column': ['time', 'proba'], 'data': data}


@app.route('/analysis/user', methods=['GET'])
def get_user_analysis():
    date = request.get_json()['date']
    
    with mysql.cursor() as cursor:
        cursor.execute(
            f"SELECT user.user_id, user_name, (sum(p_count)-count(*))/sum(p_count) AS proba "
            f"FROM picking_product_basket join user on picking_product_basket.user_id = user.user_id "
            f"WHERE DATE(p_finish_time)='{date}' "
            f"GROUP BY user.user_id ORDER BY proba DESC")
        data = cursor.fetchall()
        
        if data is not None:
            data = data[:5]
    
    return {'column': ['id', 'name', 'proba'], 'data': data}


# SignIn, SignOut, SignUp Api
@app.route('/user/login_info', methods=['POST'])
def get_user_info():
    user_id = request.get_json()['user_id']

    with mysql.cursor() as cursor:
        cursor.execute(
            f"SELECT user_password, is_admin FROM user WHERE user_id='{user_id}'")
        data = cursor.fetchone()
        
        if data is None:
            return json.dumps({'password': '', 'is_admin': 0})
        
    return json.dumps({'password': data[0], 'is_admin': data[1]})


@app.route('/user/make_user', methods=['POST'])
def make_or_update_user():
    data = request.get_json()
    is_update, user_id, name, password\
        = (data[s] for s in ['is_update_give', 'id_give', 'name_give', 'password_give'])
    
    with mysql.cursor() as cursor:
        cursor.execute(f"SELECT * FROM user WHERE user_id='{user_id}'")
        data = cursor.fetchone()
        
        computed = False
        if is_update and len(data) == 1:
            cursor.execute(
                f"UPDATE user SET user_password='{password}' WHERE user_id='{user_id}'")
            computed = True
        elif not is_update and data is None:
            cursor.execute(
                f"INSERT INTO user "
                f"VALUES ('{user_id}', '{name}', '{password}', 0)")
            computed = True
        
        if computed: mysql.commit()
    return json.dumps({'saved': computed})


@app.route('/user/get_users', methods=['POST'])
def get_users():
    with mysql.cursor() as cursor:
        cursor.execute("SELECT user_id, user_name, is_admin FROM user")
        users = cursor.fetchall()
        
    return json.dumps({'user_list': users})


@app.errorhandler(404)
def error404():
    return "Not Found"


################# T  E  S  T ##################


@app.route('/test/database', methods=['POST'])
def get_test_product():
    barcode_id = request.get_json()['id']
    zone = barcode_id[0] == 'P' and 'picking' or 'das'
    
    with mysql.cursor() as cursor:
        cursor.execute(f"SELECT product_list FROM {zone}_product_basket WHERE {zone}_id='{barcode_id}'")
        products = cursor.fetchone()[0]
        print(products)
    
    return json.dumps({'list': products}, ensure_ascii=False)


@app.route('/test/normalize_list', methods=['GET'])
def normalize_list():
    with mysql.cursor() as cursor:
        cursor.execute(
            f"SELECT order_id, product_list FROM customer_order")
        products = cursor.fetchall()
        
        for order_id, product in products:
            product = normalize(product)
            cursor.execute(
                f"UPDATE customer_order SET product_list='{product}' WHERE order_id='{order_id}'")

        # asdasd
        cursor.execute(
            f"SELECT picking_id, product_list FROM picking_product_basket")
        products = cursor.fetchall()

        for picking_id, product in products:
            product = normalize(product)
            cursor.execute(
                f"UPDATE picking_product_basket SET product_list='{product}' WHERE picking_id='{picking_id}'")
        
        mysql.commit()
    return 'saved'
    
def normalize(lists):
    return lists.replace("\'", "\"").replace("“", "\"").replace("”", "\"")


################# GENERATOR ##################


def getQ(query):
    with mysql.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


#@app.route("/gen/test1")
def test1_generator():
    target = "picking_product_basket"
    products = [data[0] for data in getQ("SELECT product_id FROM product")]
    users = [data[0] for data in getQ("SELECT user_id FROM user")]

    with mysql.cursor() as cursor:
        for i in range(3, 13):
            h = random.randint(0, 23)
            m = random.randint(0, 59)
            s = random.randint(0, 59)
            
            product_list = '{"%s":%d}' %(products[random.randint(0, len(products)-1)], random.randint(1, 20))
            user_id = users[random.randint(0, len(users)-1)]
            finish_time = '2022/08/24 %d:%d:%d' %(h, m, s)
            real_weight = random.randrange(0, 100)
            p_count = random.randint(1, 10)
            
            print(user_id, product_list, finish_time, real_weight, p_count)
            
            cursor.execute(
                "INSERT INTO %s VALUES ('P%05d', '%s', 'PB001', '%s', '%s', %lf, %d, 1)"
                %(target, i, product_list, user_id, finish_time, real_weight, p_count))
        mysql.commit()
        
    return 'saved'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
