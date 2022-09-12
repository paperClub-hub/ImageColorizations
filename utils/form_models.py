#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @ Date    : 2022/7/7 20:55
# @ Author  : DELL
# @ Site    : 
# @ Software: PyCharm


from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, TextAreaField, validators, SelectField, ValidationError
import requests

class ImageForm(FlaskForm):
    """ 上传本地图片 """
    upload = FileField(label='Upload a Picture',
                       validators=[
                           FileRequired(),
                           FileAllowed(['png', 'jpg', 'jpeg', 'bmp'], 'Images only!')
                       ])
    submit = SubmitField('点击上传图片')



def is_url_image(image_url):
    ''' 获取网络图片  '''
    image_formats = ("image/png", "image/jpeg", "image/jpg", "image/bmp")
    r = requests.head(
        image_url,
        headers={
            'user-agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        })
    if r.headers["content-type"] in image_formats:
        return True
    return False



class UrlForm(FlaskForm):
    ''' 提交网络图片 '''
    URL_str = TextAreaField(label='URL', validators=[validators.URL()], default = "http://www.infersite.com/images/cd1876de2b399.jpg")

    # Check if the url points to an image file
    def validate_URL_str(form, field):
        if not is_url_image(field.data):
            raise ValidationError('无效图片网址')

    submit = SubmitField('上传网络图片')


