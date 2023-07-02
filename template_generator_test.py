import template_generator
import os
from PIL import Image

author_name = 'Masih Tabaei'
author_age = 23

# 'C:\\Users\\masih\\Desktop\\DrawingsComeAlive\\PythonCode\\templates\\asPNG'
templates_path = './templates/asPNG'
for template in os.scandir(templates_path):
    image_opened = Image.open(template.path)
    image_opened_width, image_opened_height = image_opened.size
    pdf = template_generator.PDF(template.name.split('.')[0].split('_')[0],
                                 author_name,
                                 author_age,
                                 image_opened_width,
                                 image_opened_height)
    pdf.add_page()
    pdf.body(template.path)
    pdf.output(f'{template.name.split(".")[0]}.pdf', 'F')
  
    
    
