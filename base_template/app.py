#!flask/bin/python
from flask import Flask, render_template
app = Flask(__name__)
@app.route('/index', methods=('GET', 'POST'))
def index():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(host="localhost",port="8000",debug=True)