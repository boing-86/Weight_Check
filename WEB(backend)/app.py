from flask import Flask, request, jsonify
from functools import reduce
import math

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello Backend World!'

@app.route('/weight', methods=['POST'])
def get():
    try:
        print(request.form['id'])
    except:
        print("error")
        
    product_mean = [1, 2, 3, 4]
    product_std = [1, 1, 1, 1]
    mean = sum(product_mean)
    std = math.sqrt(reduce(lambda s, x: s + x ** 2, product_std))
    
    return jsonify({'mean': mean, 'std': std})

if __name__ == '__main__':
    app.run('0.0.0.0', port=6000, debug=True)
