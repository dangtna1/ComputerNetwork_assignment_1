import base64
import json


with open("test.png", 'rb') as f:
    img_data = f.read()


img_base64 = base64.b64encode(img_data).decode('ascii')

with open("test.json", "rt", encoding='utf-8') as f:
    new_img_64data = json.load(f)

new_img_data = base64.b64decode(new_img_64data)

with open('gg.png', 'wt') as f:
    f.write(new_img_data)
