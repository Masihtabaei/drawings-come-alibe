from fastapi.responses import Response, FileResponse
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import cv2
import aiofiles
import shutil
import requests
import template_generator
from pyzbar.pyzbar import decode, ZBarSymbol
from PIL import Image, ImageFilter, ImageOps
from kraken import binarization
import ast
import numpy as np
import io
from threading import Thread
import time

""" Drawings Come Alive """
cap = None
frame = None



def read_frame():
    global cap
    global temp_frame
    while(True):
        ret, frame = cap.read()
        if(ret):
            temp_frame = frame
        
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    global cap
    cap = cv2.VideoCapture("https://10.199.30.64:8080/video")
    print("Ready to capture!")
    t = Thread(target=read_frame)
    t.start()
    yield
    
    
app = FastAPI(lifespan=lifespan)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # You can restrict this to specific origins
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['*'],
)

# GET-Method about_us
@app.get("/about-us")
async def about_us():
    return {'Team Members': ['Gia Huy Vo', 'Kolya Keller', 'Luca Haas', 'Seyedmasih Tabaei'], 'Organization Name': 'University of applied sciences Coburg', 'Project Name': 'Drawings come Alive', 'Supervisor': 'Prof. Dr. Grubert', 'Release Date': 'July 2023'}

# GET-Method template_names
@app.get("/template-names")
async def templates_names():
    templates_path = './templates/asPNG'
    return [template.name.split('.')[0].split('_')[0] for template in os.scandir(templates_path)]

# GET-Method specific_template
@app.get("/customized-template/")
async def get_customized_template(name: str = "-", age: int = 0, template_name: str="-"):
    # 'C:\\Users\\masih\\Desktop\\DrawingsComeAlive\\PythonCode\\templates\\asPNG'
    templates_path = './templates/asPNG'
    for template in os.scandir(templates_path):
        print(template.name)
        if(template.name == template_name + "_template.png"):
            print("Found the image!")
            image_opened = Image.open(template.path)
            image_opened_width, image_opened_height = image_opened.size
            pdf = template_generator.PDF(template.name.split('.')[0].split('_')[0],
                                         name,
                                         age,
                                         image_opened_width,
                                         image_opened_height)
            pdf.add_page()
            pdf.body(template.path)
            file_path = f'./templates/customized/{template.name.split(".")[0]}.pdf'
            pdf.output(file_path, 'F')
    headers = {
        'Content-Disposition': f'attachment; filename={template.name.split(".")[0]}.pdf'
    }            
    return FileResponse(file_path, headers=headers)


# GET-Method extract_texture
@app.get("/extract-texture-cam/",
    responses = {
        200: {
            "content": {"image/jpg": {}}
        }
    },

    # Prevent FastAPI from adding "application/json" as an additional
    # response media type in the autogenerated OpenAPI specification.
    # https://github.com/tiangolo/fastapi/issues/3258
    response_class=Response)
async def extract_texture(url: str = 0):
    #url = 'http://10.199.21.68:8080'
    #if(url == 0):
    #    return "Oops, something is wrong with url."
    #response = requests.get('http://' + url + '/photo.jpg', stream=True)
    #with open('frame_captured.jpg', 'wb') as out_file:
    #    shutil.copyfileobj(response.raw, out_file)
    #del response
    #while temp_frame is None:
    #    pass
    imgx = cv2.cvtColor(temp_frame, cv2.COLOR_BGR2RGB)
    frame_captured_original = Image.fromarray(imgx)
    #cv2.imwrite('frame_captured.jpg',frame)    
    #frame_captured_original = Image.open('frame_captured.jpg')
    #frame_captured_original.show()
    frame_captured_rotated = frame_captured_original.rotate(270, expand=True)
    #frame_captured_rotated.show()
    bin_im  = binarization.nlbin(frame_captured_rotated)
    decoded_list = decode(bin_im, symbols=[ZBarSymbol.QRCODE])
    headers = ast.literal_eval(decoded_list[0].data.decode('utf-8'))
    #print(headers)
    #print(type(headers))
    print(len(decoded_list))
    lefts = [decoded.rect[0] for decoded in decoded_list]
    tops = [decoded.rect[1] for decoded in decoded_list]
    widths = [decoded.rect[2] for decoded in decoded_list]
    heights = [decoded.rect[3] for decoded in decoded_list]
    #width_var, height_var = 7, 7
    width = max(widths)
    height = max(heights)
    lefts.sort()
    tops.sort()
    #print(lefts)
    #print(tops)
    #print(width)
    #print(height)
    #original_width, original_height = new_img.size
    #print(width_whole, height_whole)
    frame_cropped_after_qr_code_detection = frame_captured_rotated.crop((lefts[0], tops[0] + height, lefts[2] + width, tops[2]))
    #frame_cropped_after_qr_code_detection.show()
    frame_cropped_after_qr_code_detection.save('frame_cropped_after_qr_code_detection.jpg')
    #end_frame = frame_cropped_after_qr_code_detection.crop((144, 312, 144 + 744, 312 + 564)) -> Elephant
    end_frame = frame_cropped_after_qr_code_detection.crop((36, 314, 36 + 963, 314 + 554))
    end_frame_resized = ImageOps.fit(end_frame, (1024, 606))
    #end_frame_resized.show()
    #end_frame_resized.save('end_frame.jpg')
    #end_frame.save('end_frame.jpeg')
    #crop.save("img_after_qrcode.bmp")
    #cropped_width, cropped_height = crop.size
    #print(cropped_width, cropped_height, original_width, original_height)
    #new_left = (((((lefts[0] + lefts[1]) / 2) * cropped_width) / original_width) * 12) / 8
    #new_top = (((((tops[0] + tops[1]) / 2) * cropped_height) / original_height) * 20) / 44
    #new_width = (((((lefts[0] + lefts[1]) / 2) * cropped_width) / original_width) * 177) / 8
    #new_height = (((((tops[0] + tops[1]) / 2) * cropped_height) / original_height) * 177) / 44
    #print(new_left, new_top, new_width, new_height)
    #print(crop.size)
    #crop.show()
    #crop2 = crop.crop((50, 100, 50 + 930, 100 + 930))
    #crop2 = crop.crop((new_left - 20, new_top + 50, new_left - 20 + new_width, new_top + 50 + new_height))
    #new_qr_width = 33 * cropped_width / width;
    #new_qr_height = 33 * cropped_height / height;
    #crop2 = crop.crop(((7 * new_qr_width) / 33, (16 * new_qr_height) / 33, (7 * new_qr_width) / 33 + (177 * new_qr_width) / 33, (16 * new_qr_height) / 33 + (177 * new_qr_height) / 33))
    #crop3 = crop.crop((46, 104, 46 + 926, 104 + 936))
    #crop3.show()
    header = {"template_name": headers["template_name"]}
    image_bytes = cv2.imencode('.jpg', np.array(end_frame_resized))[1].tobytes()
    # media_type here sets the media type of the actual response sent to the client.
    return Response(content=image_bytes, headers=header, media_type="image/jpg")
    #return FileResponse('end_frame.jpg', headers=header)


