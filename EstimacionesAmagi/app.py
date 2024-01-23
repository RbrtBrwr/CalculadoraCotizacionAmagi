from flask import Flask, jsonify, request
import dataProcessing as dp

app = Flask(__name__)

@app.route('/pullData', methods=['GET'])
def api():
    data = dp.getAllData()
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:7295')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response

@app.route('/pullVariablesDeServicio', methods=['GET'])
def api2():
    data = dp.getVariablesServicio()
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:7295')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response

@app.route('/pullCostos', methods=['GET'])
def api3():
    data = dp.getCostos()
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:7295')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response

if __name__ == '__main__':
    app.run(port=5000)
