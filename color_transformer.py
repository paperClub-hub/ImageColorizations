#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @ Date    : 2022/7/6 5:58
# @ Author  : DELL
# @ Site    : 
# @ Software: PyCharm


from colorizers import *
from typing import Union
import matplotlib.pyplot as plt


# colorizer_eccv16 = None
# if colorizer_eccv16 is None:
#     colorizer_eccv16 = load_eccvmodel()

colorizer_siggraph17 = None
if colorizer_siggraph17  is None:
    colorizer_siggraph17 = load_siggraphmodel()


def img_colorizeation(pil_img, method: Union[int]=0):

    """
    图片着色：需要 rgb 三通道的 灰色 pil image
    :param pil_img:
    :return:
    """

    if not isinstance(pil_img, np.ndarray):
        pil_img = np.asarray(pil_img)

    if (pil_img.ndim == 2):
        pil_img = np.tile(pil_img[:, :, None], 3)


    # MODEL = colorizer_eccv16 if method == 0 else colorizer_siggraph17
    MODEL = colorizer_siggraph17

    colorizer_img = predict(MODEL, pil_img, size=256, resample=3)

    return cv2pil(colorizer_img)


def img_grey(pil_img):

    """ 转为灰白图片 """

    if len(np.array(pil_img).shape) >=3:
        return Image.fromarray(np.array(pil_img)[:, :, :3])

    elif len(np.array(pil_img).shape) == 2:
        return pil_img
    else:
        print("数据类型有误 ")
        return np.array([])


def img_transformer(img_bytes, method: int = 0, is_stream=True):
    """" 转换图片 """
    pil_img = bytes2pil(img_bytes)

    img_res = pil_img
    if method == 0 or method == 1:
        img_res = img_colorizeation(pil_img, method)

    elif method == 2:
        img_res = img_grey(pil_img)
    else:
        print(f"非法指令 ： {method} !")

    del pil_img

    if is_stream:
        return pil2bytes(img_res)
    else:
        return img_res


import re
if __name__ == '__main__':
    img_path = "./imgs/1.jpg"
    # img_bytes = open(img_path, 'rb').read()
    #
    # res_bytes = img_transformer(img_bytes, method=0, is_stream=False)
    # img = Image.open(BytesIO(img_bytes))
    # plt.imshow(res_bytes)
    # plt.show()

