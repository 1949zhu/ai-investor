from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Flask 运行正常!</h1>'

if __name__ == '__main__':
    print('Starting Flask on port 5000...')
    app.run(host='0.0.0.0', port=5000, debug=False)
