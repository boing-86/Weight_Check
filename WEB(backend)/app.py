from flask import Flask, request
from os import environ
import pymysql
import json
import math

app = Flask(__name__)
# mysql 연결 하기
mysql = pymysql.connect(host=environ.get('KurlyCheckDbHost'),  # Endpoint
                        port=int(environ.get('KurlyCheckDbPort')),  # Endpoint Port
                        user=environ.get('KurlyCheckDbUser'),
                        password=environ.get('KurlyCheckDbPswd'),
                        database='kdb',  # Schema Name
                        charset="utf8mb4")

@app.route('/')
def hello_world():
    return 'Hello Backend World!'

@app.route('/weight', methods=['POST'])
def get_weight_sum():
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
        products_json = json.loads(products_string.replace("'", "\""))
    
        # 바구니 무게 더하기
        cursor.execute(
            f"SELECT b_weight_avg, b_weight_std FROM basket WHERE basket_id='{basket_id}'")
        mean, std = cursor.fetchone()
    
        # DB 에서 상품 평균, 표준 편차 구하기
        for name, count in products_json.items():
            cursor.execute(
                f"SELECT p_weight_avg, p_weight_std FROM product WHERE product_id='{name}'")
            p_avg, p_std = cursor.fetchone()
        
            mean += count *  p_avg
            std  += count * (p_std**2)
        std = math.sqrt(std)
    
    # 기대 중량 최대, 최소 구하기
    min_weight = mean - 3*std
    max_weight = mean + 3*std

    return json.dumps({'min': min_weight, 'max': max_weight})

@app.route('/save/weight', methods=['POST'])
def save_working_data():
    data = request.get_json()
    user_key = data['user_key']
    finish_time = data['finish_time']
    real_weight = data['weight']
    barcode_id = data['id']
    is_picking_zone = barcode_id[0] == 'P'
    
    with mysql.cursor() as cursor:
        # cursor.execute(
        #     f"SELECT user_id FROM login WHERE user_key='{user_key}'")
        # user_id = cursor.fetchone()
        user_id = user_key
        
        if is_picking_zone:
            cursor.execute(
                f"UPDATE picking_product_basket SET user_id='{user_id}', p_finish_time='{finish_time}', p_real_weight={real_weight}, p_finish=true WHERE picking_id='{barcode_id}'")
        else:
            cursor.execute(
                f"UPDATE das_product_basket SET user_id='{user_id}', p_finish_time='{finish_time}', p_real_weight={real_weight}, p_finish=true WHERE das_id='{barcode_id}'")
    
    return 'saved'

@app.route('/test/database', methods=['POST'])
def get_test_product():
    with mysql.cursor() as cursor:
        cursor.execute("SELECT * FROM product")
        id, name, avg, std = cursor.fetchone()
        print(id, name, avg, std)
        
    return json.dumps({'id':id, 'name':name, 'avg':avg, 'std':std}, ensure_ascii=False)

@app.route('/get/password', methods=['POST'])
def get_user_password():
    user_id = request.get_json()['user_id']
    
    with mysql.cursor() as cursor:
        cursor.execute(
            f"SELECT user_password FROM user WHERE user_id='{user_id}'")
        password = cursor.fetchone()[0]
    
    return json.dumps({'password': password})

@app.errorhandler(404)
def error404():
    return "Not Found"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)
