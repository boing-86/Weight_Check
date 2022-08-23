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
 
        products_string = products_string.replace("\'", "\"")
        products_string = products_string.replace("“", "\"")
        products_string = products_string.replace("”", "\"")
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
    user_id = data['user_key']
    finish_time = data['finish_time']
    real_weight = data['weight']
    barcode_id = data['id']
    
    zone = barcode_id[0] == 'P' and 'picking' or 'das'
    z = barcode_id[0] == 'P' and 'p' or 'd'
    
    with mysql.cursor() as cursor:
        cursor.execute(
            f"UPDATE {zone}_product_basket SET user_id='{user_id}', {z}_finish_time='{finish_time}',"
            f" {z}_real_weight={real_weight}, {z}_finish=true WHERE {zone}_id='{barcode_id}'")
        
    counting_count()
    return 'saved'

# 작업에 실패함
@app.route('/counting', methods=['POST'])
def counting_count():
    data = request.get_json()
    barcode_id = data['id']
    
    zone = barcode_id[0] == 'P' and 'picking' or 'das'
    z = barcode_id[0] == 'P' and 'p' or 'd'
    
    with mysql.cursor() as cursor:
        cursor.execute(
            f"SELECT {z}_count FROM {zone}_product_basket WHERE {zone}_id='{barcode_id}'")
        count = cursor.fetchone()[0] + 1
        print(count)
        cursor.execute(
            f"UPDATE {zone}_product_basket SET {z}_count={count} WHERE {zone}_id='{barcode_id}'")
        mysql.commit()
    return "saved"

# 강제로 작업 완료를 함 (로그를 남김)
# INSERT 구문이 오류가 납니다.
@app.route('/update/force', methods=['POST'])
def save_working_error():
    mean, std = get_weight_mean_std()
    data = request.get_json()
    barcode_id = data['id']
    zone = barcode_id[0] == 'P' and 'picking' or 'das'
    
    with mysql.cursor() as cursor:
        cursor.execute(
            f"INSERT INTO product_error (where , order_id, predict_avg, predict_std )"
            f"VALUES ('{zone}', '{barcode_id}', {mean}, {std} )")
        mysql.commit()
    return "saved"


@app.route('/get/password', methods=['POST'])
def get_user_password():
    user_id = request.get_json()['user_id']
    
    with mysql.cursor() as cursor:
        cursor.execute(
            f"SELECT user_password FROM user WHERE user_id='{user_id}'")
        password = cursor.fetchone()[0]
    
    return json.dumps({'password': password})


################# T  E  S  T ##################

@app.route('/test/database', methods=['POST'])
def get_test_product():
    data = request.get_json()
    barcode_id = data['id']
    
    zone = barcode_id[0] == 'P' and 'picking' or 'das'
    
    with mysql.cursor() as cursor:
        cursor.execute(f"SELECT product_list FROM {zone}_product_basket WHERE {zone}_id='{barcode_id}'")
        list = cursor.fetchone()[0]
        print(list)
    
    return json.dumps({'list': list}, ensure_ascii=False)

@app.errorhandler(404)
def error404():
    return "Not Found"

if __name__ == '__main__':
    app.run()
