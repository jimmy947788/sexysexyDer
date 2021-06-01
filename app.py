from flask import Flask
from flask import render_template
from flask import request
import logging
from logging.handlers import RotatingFileHandler
import auto_poster

app = Flask(__name__)

logging.basicConfig(filename='sexsexder.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    fdffffff = ""
    if request.method == 'POST':
        if request.form.get('txt_ig_linker'): 
            ig_linker = request.form.get('txt_ig_linker')
            (post, shortcode_folder) = auto_poster.igDownloader(ig_linker)
            post_url =  auto_poster.fpPostToPage(post, shortcode_folder, ig_linker)
            auto_poster.fpPostToGroup(post_url)

    return render_template('index.html', title='Welcome', message="", error_message="")

if __name__ == "__main__":

    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.jinja_env.auto_reload = True
    app.run(debug=True, host='0.0.0.0')