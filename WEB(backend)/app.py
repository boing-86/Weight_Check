from flask import Flask, request, jsonify
import pymysql
import math

app = Flask(__name__)
# mysql 연결 설정 하기
mysql = pymysql.connect(host='',  # Auroua Endpoint
                        port=3306,  # Auroua Endpoint Port
                        user='',
                        password='',
                        database='kdb')  # Schema Name

@app.route('/')
def hello_world():
    return 'Hello Backend World!'

@app.route('/weight', methods=['POST'])
def get_weight_sum():
    data = request.get_json()
    barcode_id = data['id']
    is_picking_zone = barcode_id[0] == 'P'

    with mysql.cursor() as cursor:
        # 피킹/DAS 별 상품 리스트 만들기
        if is_picking_zone:
            cursor.execute(
                "SELECT product_id, p_product_count, basket_id FROM picking_product_basket WHERE picking_id = %s" %barcode_id)
            id, count, basket_id = cursor.fetchone()
        
            product_ids = [id]
            product_counts = [count]
        else:
            cursor.execute(
                "SELECT order_id, basket_id FROM das_product_basket WHERE das_id = %s" %barcode_id)
            order_id, basket_id = cursor.fetchone()
            
            cursor.execute(
                "SELECT product_id_list, product_count_list FROM customer_order WHERE order_id = %s" % order_id)
            ids, counts = cursor.fetchone()
        
            product_ids = ids.split(',')
            product_counts = counts.split(',')
    
        # 바구니 무게 더하기
        cursor.execute(
            "SELECT b_weight_avg, b_weight_std FROM basket WHERE basket_id = %s" % basket_id)
        mean, std = cursor.fetchone()
    
        # DB 에서 상품 평균, 표준 편차 구하기
        for name, count in zip(product_ids, product_counts):
            cursor.execute(
                "SELECT p_weight_avg, p_weight_std FROM product WHERE product_id == %s" %name)
            p_avg, p_std = cursor.fetchone()
        
            mean += count *  p_avg
            std  += count * (p_std**2)
        std = math.sqrt(std)
    
    # 기대 중량 최대, 최소 구하기
    min_weight = mean - 3*std
    max_weight = mean + 3*std

    return jsonify({'min': min_weight, 'max': max_weight})

@app.route('/save/weight', methods=['POST'])
def save_working_data():
    data = request.get_json()
    user_key = data['user_key']
    finish_time = data['finish_time']
    real_weight = data['weight']
    barcode_id = data['id']
    is_picking_zone = barcode_id[0] == 'P'
    
    with mysql.cursor() as cursor:
        cursor.execute(
            "SELECT user_id FROM login WHERE user_key == %s" %user_key)
        user_id = cursor.fetchone()
        
        if is_picking_zone:
            cursor.execute(
                "UPDATE picking_product_basket SET user_id=%s, p_finish_time=%s, p_real_weight=%lf, p_finish=true WHERE picking_id=%s"
                %(user_id, finish_time, real_weight, barcode_id))
        else:
            cursor.execute(
                "UPDATE das_product_basket SET  user_id=%s, p_finish_time=%s, p_real_weight=%lf, p_finish=true WHERE das_id=%s"
                %(user_id, finish_time, real_weight, barcode_id))
    
    return 'saved'

@app.route('/test/database', methods=['POST'])
def get_product():
    with mysql.cursor() as cursor:
        cursor.execute("SELECT * FROM product")
        print(cursor.fetchall())

    return 'test'

@app.errorhandler(404)
def error404():
    return "Not Found"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)
    