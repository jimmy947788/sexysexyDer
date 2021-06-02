from flask import Flask
from flask import render_template
from flask import request
import logging
import auto_poster
from dotenv import load_dotenv
import os

app = Flask(__name__)

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    msg1 = ""
    msg2  = ""
    post_linker = ""
    if request.method == 'POST':
        if request.form.get('txt_ig_linker'): 
            try:
                ig_linker = request.form.get('txt_ig_linker')
                shortcode_folder = auto_poster.ig_downloader(ig_linker)
                post_linker =auto_poster.fb_post2page(shortcode_folder, ig_linker)
                auto_poster.fb_post2group(post_linker)
                msg1 = "發送成功 !!"
            except Exception as e:
                msg1 = ""
                msg2 = f"發送失敗:{ str(e) }"  
                post_linker = ""

    return render_template('index.html', title='Welcome', message=msg1, post_linker=post_linker, error_message=msg2)

if __name__ == "__main__":

    if not os.path.exists("logs"):
            os.makedirs("logs")
    logging.basicConfig(filename='./logs/sexsexder.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
    
    auto_poster.load_env()

    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.jinja_env.auto_reload = True
    app.run(debug=True, host='0.0.0.0')