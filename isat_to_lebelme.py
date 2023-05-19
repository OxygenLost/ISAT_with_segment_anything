import json
import base64
import PIL.Image as Image
import io
import numpy
def img_arr_to_b64(img_arr):
    img_pil = Image.fromarray(img_arr)
    f = io.BytesIO()
    img_pil.save(f, format="JPEG")
    img_bin = f.getvalue()
    if hasattr(base64, "encodebytes"):
        img_b64 = base64.encodebytes(img_bin)
    else:
        img_b64 = base64.encodestring(img_bin)
    img_b64 = str(img_b64).replace(r'\n', '')
    img_b64 = str(img_b64).replace(r"b'", '')
    img_b64 = str(img_b64).replace(r"'", '')
    return img_b64

def isat_to_lebelme(json_path):
    imgpath = json_path.replace('.json', '.jpg')
    img = Image.open(imgpath)
    img_pil = numpy.array(img)

    
    with open(json_path, 'r') as f:
        jsondata = json.load(f)
    data = {
        "version": "5.2.0.post4",
        "flags": {},
        "shapes": [
            {
                "label": jsondata['objects'][0]['category'],
                "points": jsondata['objects'][0]['segmentation'],
                "group_id": None,
                "description": "",
                "shape_type": "polygon",
                "flags": {}
            }
        ],
        "imagePath": json_path,
        "imageData": img_arr_to_b64(img_pil),
        "imageHeight": jsondata['info']['height'],
        "imageWidth": jsondata['info']['width']
    }
    # print(data)
    
    # 写入json文件
    with open(json_path.replace('.json', 'labelme.json'), 'w') as f:
        json.dump(data, f, indent=4)
if __name__ == '__main__':
    isat_to_lebelme("Image10.json")
