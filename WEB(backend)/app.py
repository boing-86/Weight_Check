from flask import Flask, request
from os import environ
import pymysql
import json
import math

app = Flask(__name__)

if not environ.get('KurlyCheckDbHost') and not environ.get('KurlyCheckDbPort') and\
        not environ.get('KurlyCheckDbUser') and not environ.get('KurlyCheckDbPswd'):
    print("make environment variable for db server connection!")

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
            products_string, basket_id = cursor.fetchone()
        else:
            cursor.execute(
                f"SELECT order_id, basket_id FROM das_product_basket WHERE das_id='{barcode_id}'")
            order_id, basket_id = cursor.fetchone()
            
            cursor.execute(
                f"SELECT product_list FROM customer_order WHERE order_id='{order_id}'")
            products_string = cursor.fetchone()[0]
 
        products_json = json.loads(products_string)

        # 바구니 무게 더하기
        cursor.execute(
            f"SELECT b_weight_avg, b_weight_std FROM basket WHERE basket_id='{basket_id}'")
        mean, std = cursor.fetchone()
        
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
        
    counting_count()
    return 'saved'


# 작업에 실패함
@app.route('/counting', methods=['POST'])
def counting_count():
    barcode_id = request.get_json()['id']
    
    zone = barcode_id[0] == 'P' and 'picking' or 'das'
    z = barcode_id[0] == 'P' and 'p' or 'd'
    
    with mysql.cursor() as cursor:
        cursor.execute(
            f"SELECT {z}_count FROM {zone}_product_basket WHERE {zone}_id='{barcode_id}'")
        count = cursor.fetchone()[0] + 1
        
        cursor.execute(
            f"UPDATE {zone}_product_basket SET {z}_count={count} WHERE {zone}_id='{barcode_id}'")
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
@app.route('/product/error_list')
def get_error_list():
    with mysql.cursor() as cursor:
        cursor.execute(
            f"SELECT * FROM product_error")
        data = cursor.fetchall()
    return data


@app.route('/analysis/time')
def get_time_analysis():
    with mysql.cursor() as cursor:
        cursor.execute(
            f"SELECT * FROM product_error")
        data = cursor.fetchall()
    return data


# Login Api
@app.route('/user/login_info', methods=['POST'])
def get_user_info():
    user_id = request.get_json()['user_id']
    
    with mysql.cursor() as cursor:
        cursor.execute(
            f"SELECT user_password, is_admin FROM user WHERE user_id='{user_id}'")
        data = cursor.fetchone()
        
        if data is None:
            return json.dumps({'password': '', 'is_admin': 0})
        password, is_admin = data
        
    return json.dumps({'password': password, 'is_admin': is_admin})


# User Api
@app.route('/user/make_user', methods=['POST'])
def make_or_update_user():
    data = request.get_json()
    is_update, user_id, name, password, admin\
        = (data[s] for s in ['is_update', 'id', 'name', 'password', 'is_admin'])
    
    with mysql.cursor() as cursor:
        cursor.execute(f"SELECT * FROM user WHERE user_id='{user_id}'")
        data = cursor.fetchone()
        
        computed = False
        if is_update and len(data) == 1:
            cursor.execute(
                f"UPDATE user SET user_password='{password}' WHERE user_id='{user_id}'")
            computed = True
        elif not is_update and len(data) == 0:
            cursor.execute(
                f"INSERT INTO user "
                f"VALUES ('{user_id}', '{name}', '{password}', {admin})")
            computed = True
        
        if computed: mysql.commit()
    return json.dumps({'committed': computed})


@app.route('/user/get_users', methods=['POST'])
def get_users():
    with mysql.cursor() as cursor:
        cursor.execute("SELECT user_id, user_name, is_admin FROM user")
        users = cursor.fetchall()
    return users


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


@app.errorhandler(404)
def error404():
    return "Not Found"


if __name__ == '__main__':
    app.run()
