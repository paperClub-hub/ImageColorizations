#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @ Date    : 2022/7/6 5:58
# @ Author  : paperClub

import os
import time
import json
from flask import Flask, render_template
from werkzeug.utils import secure_filename
from pathlib import Path
from urllib.parse import urlparse
from utils.form_models import *
from datetime import timedelta
from color_transformer import *
import base64



app = Flask(__name__)
app.config['SECRET_KEY']='PAPERCLUBASDFASDF'
app.send_file_max_age_default = timedelta(seconds=1)
app.config['UPLOAD_FOLDER'] = './instance/uploads/'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/', methods=['POST', 'GET'])  # 添加路由
def main():
    Image_form = ImageForm()
    Url_form = UrlForm()

    def img2byte(img_path):
        with open(img_path,'rb') as f:
            img_byte = f.read()
        return img_byte

    def color_transfor_res(filename, method):

        ori_img_bytes = img2byte(filename)
        img_bytes = img_transformer(ori_img_bytes, method)

        return ori_img_bytes, img_bytes

    if Image_form.validate_on_submit():
        filename = Path(secure_filename(Image_form.upload.data.filename))
        filename = filename.stem + str(time.time()) + filename.suffix
        img_filepath = Path(app.config['UPLOAD_FOLDER'])  / filename
        Image_form.upload.data.save(str(img_filepath))

        ori_bytes, img_bytes = color_transfor_res(img_filepath, method=1)
        ori_bytes = "data:image/png;base64," + base64.b64encode(ori_bytes).decode("ascii")
        del filename, img_filepath
        return render_template('predict.html',
                               title='Prediction',
                               form = Image_form,
                               ori_bytes = ori_bytes,
                               img_bytes = img_bytes,
                              )



    elif Url_form.validate_on_submit():
        """ 网络图片 """

        filename = Path(urlparse(Url_form.URL_str.data).path)
        filename = filename.stem + str(time.time()) + filename.suffix
        img_filepath = Path(app.config['UPLOAD_FOLDER']) / filename

        headers = {
            'user-agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        }
        res = requests.get(Url_form.URL_str.data, headers)
        with open(img_filepath, 'wb') as f:
            f.write(res.content)

        ori_bytes, img_bytes = color_transfor_res(img_filepath, method=0)
        ori_bytes = "data:image/png;base64," + base64.b64encode(ori_bytes).decode("ascii")
        return render_template('predict.html',
                               title='Prediction',
                               url_form = Url_form,
                               ori_bytes = ori_bytes,
                               img_bytes = img_bytes
                              )

    return render_template('upload.html',
                           url_form=Url_form,
                           form=Image_form)



if __name__ == '__main__':
    # app.debug = True
    app.run(host='127.0.0.1', port=8001, debug=True)
