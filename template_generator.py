import qrcode
from fpdf import FPDF
from PIL import Image, ImageOps

def generate_a_qrcode(data_to_encode):
    image = qrcode.make(data_to_encode)
    return image

class PDF(FPDF):
    def __init__(self, template_name, author_name, author_age, image_width, image_height):
        super().__init__()
        self.qrCodeAsImage = generate_a_qrcode({'template_name': template_name, 'author_name': author_name, 'author_age': author_age, 'image_width': image_width, 'image_height': image_height})
        self.qrCodeAsImage.save('./templates/qrCodes/qrcode.png')
        self.qrCodeAsImageMirrored = ImageOps.mirror(self.qrCodeAsImage)
        self.qrCodeAsImageMirrored.save('./templates/qrCodes/qrcode-mirrored.png')
        self.qrCodeAsImageFlipped = ImageOps.flip(self.qrCodeAsImage)
        self.qrCodeAsImageFlipped.save('./templates/qrCodes/qrcode-flipped.png')
        self.qrCodeAsImageMirroredThenFlipped = ImageOps.flip(self.qrCodeAsImageMirrored)
        self.qrCodeAsImageMirroredThenFlipped.save('./templates/qrCodes/qrcode-mirrored-flipped.png')
        
    def header(self):
        self.image('./templates/qrCodes/qrcode.png', 8, 8, 33, 33)
        self.image('./templates/qrCodes/qrcode-mirrored.png', 171, 8, 33, 33)
    def body(self, template_path):
        template_image = Image.open(template_path)
        template_image_width, template_image_height = template_image.size
        ratio = template_image_width / template_image_height
        self.image(template_path, (210//2) - (177//2), (297//2) - ((177 // ratio)//2), 177, (177 // ratio))
    def footer(self):
        self.image('./templates/qrCodes/qrcode-flipped.png', 8, 256, 33, 33)
        self.image('./templates/qrCodes/qrcode-mirrored-flipped.png', 171, 256, 33, 33)
        