from flask import Flask
from flask import render_template
from flask import request
import logging
import auto_poster
from dotenv import load_dotenv
import os

app = Flask(__name__)

logging.basicConfig(filename='sexsexder.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    fdffffff = ""
    if request.method == 'POST':
        if request.form.get('txt_ig_linker'): 
            ig_linker = request.form.get('txt_ig_linker')
            shortcode_folder = auto_poster.ig_downloader(ig_linker)
            post_url =auto_poster.fb_post2page(shortcode_folder, ig_linker)
            auto_poster.fb_post2group(post_url)

    return render_template('index.html', title='Welcome', message="", error_message="")

if __name__ == "__main__":
    load_dotenv() 

    global  id_username
    global  ig_session_file
    global  fb_page_id
    global  fb_group_id
    global  fb_access_token
    global  fb_access_token_hide

    id_username= os.getenv('IG_USERNAME')
    ig_session_file=  os.getenv('IG_SESSION_FILE')
    fb_page_id = os.getenv('FB_PAGE_ID')
    fb_group_id = os.getenv('FB_GROUP_ID')
    fb_access_token=  os.getenv('FB_ACCESS_TOKEN')
    fb_access_token_hide = fb_access_token[0:4] + "*****" +  fb_access_token[4:0]

    environment_mesg = "read environment :"
    environment_mesg += f"id_username={id_username}, "
    environment_mesg += f"ig_session_file={ig_session_file}, "
    environment_mesg += f"fb_page_id={fb_page_id}, "
    environment_mesg += f"fb_group_id={fb_group_id}, "
    environment_mesg += f"fb_access_token={fb_access_token_hide} "
    logging.info(environment_mesg)

    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.jinja_env.auto_reload = True
    app.run(debug=True, host='0.0.0.0')