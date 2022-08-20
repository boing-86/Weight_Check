from flask import Flask, request, jsonify
import pymysql
import math

# mysql = MySQL()
app = Flask(__name__)
# todo: mysql 연결 설정 하기
mysql = pymysql.connect(host = '',
                        user='',
                        password='',
                        database='',
                        cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def hello_world():
    return 'Hello Backend World!'

@app.route('/weight', methods=['POST'])
def get_weight_sum():
    mean = std = 0
    barcode_id = request.form['id']

    # 바코드가 피킹/DAS 에서 쓰이는지 확인
    # todo: 바코드 임의로 정하면, 문자열 파싱해서 알 수 있음
    is_picking_zone = True # 임의 값

    # DB 에서 상품 리스트 찾기
    with mysql.cursor() as cursor:
        if is_picking_zone:
            cursor.execute("sql: picking_id == %s" %barcode_id)
            data = cursor.fatchone()
            
            product_names = [ data['product_id'] ]
            product_counts= [ data['p_product_count'] ]
        else:
            cursor.execute("sql: das_id == %s" %barcode_id)
            data = cursor.fatchone()
            
            # todo: 쿼리 문자열 파싱 (string -> List)
            product_names = data['']
            product_counts= data['']
    
    # DB 에서 상품 평균, 표준 편차 구하기
    with mysql.cursor() as cursor:
        for name, count in zip(product_names, product_counts):
            cursor.execute("sql: product_id == %s" %name)
            product = cursor.fatchone()
            
            mean += count * product['p_weight_avg']
            std  += count *(product['p_weight_std']**2)
    std = math.sqrt(std)

    return jsonify({'mean': mean, 'std': std})

@app.errorhandler(404)
def error404():
    return "Not Found"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)
