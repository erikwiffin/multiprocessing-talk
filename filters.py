import math

from PIL import Image, ImageOps, ImageFont, ImageDraw


def split(l, n):
    step = math.ceil(len(l) / n)
    for i in range(n):
        yield l[i * step : (i + 1) * step]


CHARS = list('@#*+=:-. ')
RANGES = list(split(range(0, 256), len(CHARS)))
COURIER_NEW = r'/Library/Fonts/Courier New.ttf'


def ascii(img):

    orig_x, orig_y = img.size

    new_x = math.floor(orig_x / 8)
    new_y = math.floor(new_x * orig_y / orig_x * 0.51)

    img = img.resize((new_x, new_y))
    img = ImageOps.grayscale(img)

    text = ''
    for img_y in range(0, new_y - 1):
        for img_x in range(0, new_x - 1):
            color = img.getpixel((img_x, img_y))
            for ix, color_range in enumerate(RANGES):
                if color in color_range:
                    text += CHARS[ix]
        text += '\n'

    img = Image.new('L', (orig_x, orig_y), 255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(COURIER_NEW, 14)

    draw.text((0, 0), text, 0, font=font)

    return img
