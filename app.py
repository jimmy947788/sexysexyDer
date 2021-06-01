from flask import Flask
from flask import render_template
from flask import request
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

logging.basicConfig(filename='sexsexder.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():

    return render_template('index.html', title='Welcome')

if __name__ == "__main__":

    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.jinja_env.auto_reload = True
    app.run(debug=True, host='0.0.0.0')