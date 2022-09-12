import base64

from PIL import Image
import numpy as np
from skimage import color
import torch
import torch.nn.functional as F
from urllib import request
import cv2
from io import BytesIO


def load_img(img_path):
	out_np = np.asarray(Image.open(img_path))
	if(out_np.ndim==2):
		out_np = np.tile(out_np[:,:,None],3)
	return out_np

def resize_img(img, HW=(256,256), resample=3):
	return np.asarray(Image.fromarray(img).resize((HW[1],HW[0]), resample=resample))

def preprocess_img(img_rgb_orig, HW=(256,256), resample=3):
	# return original size L and resized L as torch Tensors
	img_rgb_rs = resize_img(img_rgb_orig, HW=HW, resample=resample)
	
	img_lab_orig = color.rgb2lab(img_rgb_orig)
	img_lab_rs = color.rgb2lab(img_rgb_rs)

	img_l_orig = img_lab_orig[:,:,0]
	img_l_rs = img_lab_rs[:,:,0]

	tens_orig_l = torch.Tensor(img_l_orig)[None,None,:,:]
	tens_rs_l = torch.Tensor(img_l_rs)[None,None,:,:]

	del img_rgb_orig,img_l_orig, img_l_rs
	return (tens_orig_l, tens_rs_l)


def postprocess_tens(tens_orig_l, out_ab, mode='bilinear'):
	# tens_orig_l 	1 x 1 x H_orig x W_orig
	# out_ab 		1 x 2 x H x W

	HW_orig = tens_orig_l.shape[2:]
	HW = out_ab.shape[2:]

	# call resize function if needed
	if(HW_orig[0]!=HW[0] or HW_orig[1]!=HW[1]):
		out_ab_orig = F.interpolate(out_ab, size=HW_orig, mode=mode)
	else:
		out_ab_orig = out_ab

	out_lab_orig = torch.cat((tens_orig_l, out_ab_orig), dim=1)

	del tens_orig_l, out_ab
	return color.lab2rgb(out_lab_orig.data.cpu().numpy()[0,...].transpose((1,2,0)))


def predict(model, pil_img, size = 256, resample=3):
	""" 整合图像格式，用于着色处理 """

	tens_orig_l, tens_rs_l = preprocess_img(pil_img, HW=(size, size), resample=resample)
	colorizer_img = postprocess_tens(tens_orig_l, model(tens_rs_l).cpu())
	cv2_img = pil2cv(colorizer_img)
	cv2_img = cv2.normalize(cv2_img, None, 0, 255, cv2.NORM_MINMAX)
	cv2_img = np.uint8(cv2_img)

	del pil_img,tens_orig_l, tens_rs_l,colorizer_img
	return cv2_img


def cv2pil(cv2_img):
    """ cv2 img to pil img"""
    img = cv2_img
    if len(cv2_img.shape) == 2:
        img = Image.fromarray(cv2_img)

    elif len(cv2_img.shape) == 3:
        img = Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))
    else:
        print("格式有问题")
    del cv2_img
    return img


def pil2cv(pil_img):
    return cv2.cvtColor(np.asarray(pil_img), cv2.COLOR_RGB2BGR)


def url2img(url_path):
    """ url to image """
    resp = request.urlopen(url_path)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    img = cv2.imdecode(image, 1)
    del image, resp, url_path

    return img


def pil2bytes(pil_img):
	""" pil 图像转字节流 """

	imgByteArr = BytesIO()
	pil_img.save(imgByteArr, format='png')
	img_bytes = base64.b64encode(imgByteArr.getbuffer()).decode("ascii")
	return f"data:image/png;base64,{img_bytes}"



def bytes2pil(img_bytes):
	""" 字节流转图片 """
	img_stream = BytesIO(img_bytes)
	return Image.open(img_stream).convert('RGB')

