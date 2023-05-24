# -*- coding: utf-8 -*-
# @Author  : LG

import base64
import io
import os
from PIL import Image
import numpy as np
from json import load, dump
from typing import List


def img_arr_to_b64(img_arr):
    img_pil = Image.fromarray(np.uint8(img_arr))
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


class Object:
    def __init__(self, category: str, group: int, segmentation, area, layer, bbox, iscrowd=0, note=''):
        self.category = category
        self.group = group
        self.segmentation = segmentation
        self.area = area
        self.layer = layer
        self.bbox = bbox
        self.iscrowd = iscrowd
        self.note = note


class Annotation:
    def __init__(self, image_path, label_path):
        img_folder, img_name = os.path.split(image_path)
        self.description = 'ISAT'
        self.img_folder = img_folder
        self.img_name = img_name
        self.label_path = label_path
        self.note = ''

        image = np.array(Image.open(image_path))
        self.image = image.copy()
        if image.ndim == 3:
            self.height, self.width, self.depth = image.shape
        elif image.ndim == 2:
            self.height, self.width = image.shape
            self.depth = 0
        else:
            self.height, self.width, self.depth = image.shape[:, :3]
            print('Warning: Except image has 2 or 3 ndim, but get {}.'.format(image.ndim))
        del image

        self.objects: List[Object, ...] = []

    def load_annotation(self):
        if os.path.exists(self.label_path):
            with open(self.label_path, 'r') as f:
                dataset = load(f)
                info = dataset.get('info', {})
                description = info.get('description', '')
                if description == 'ISAT':
                    # ISAT格式json
                    objects = dataset.get('objects', [])
                    self.img_name = info.get('name', '')
                    width = info.get('width', None)
                    if width is not None:
                        self.width = width
                    height = info.get('height', None)
                    if height is not None:
                        self.height = height
                    depth = info.get('depth', None)
                    if depth is not None:
                        self.depth = depth
                    self.note = info.get('note', '')
                    for obj in objects:
                        category = obj.get('category', 'unknow')
                        group = obj.get('group', 0)
                        if group is None: group = 0
                        segmentation = obj.get('segmentation', [])
                        iscrowd = obj.get('iscrowd', 0)
                        note = obj.get('note', '')
                        area = obj.get('area', 0)
                        layer = obj.get('layer', 2)
                        bbox = obj.get('bbox', [])
                        obj = Object(category, group, segmentation, area, layer, bbox, iscrowd, note)
                        self.objects.append(obj)
                else:
                    # labelme格式json
                    shapes = dataset.get('shapes', {})
                    for shape in shapes:
                        # 只加载多边形
                        is_polygon = shape.get('shape_type', '') == 'polygon'
                        if not is_polygon:
                            continue
                        category = shape.get('label', 'unknow')
                        group = shape.get('group_id', 0)
                        if group is None: group = 0
                        segmentation = shape.get('points', [])
                        iscrowd = shape.get('iscrowd', 0)
                        note = shape.get('note', '')
                        area = shape.get('area', 0)
                        layer = shape.get('layer', 2)
                        bbox = shape.get('bbox', [])
                        obj = Object(category, group, segmentation, area, layer, bbox, iscrowd, note)
                        self.objects.append(obj)

    def save_annotation(self):
        dataset = {}
        dataset['info'] = {}
        dataset['info']['description'] = self.description
        dataset['info']['folder'] = self.img_folder
        dataset['info']['name'] = self.img_name
        dataset['info']['width'] = self.width
        dataset['info']['height'] = self.height
        dataset['info']['depth'] = self.depth
        dataset['info']['note'] = self.note
        dataset['objects'] = []
        for obj in self.objects:
            object = {}
            object['category'] = obj.category
            object['group'] = obj.group
            object['segmentation'] = obj.segmentation
            object['area'] = obj.area
            object['layer'] = obj.layer
            object['bbox'] = obj.bbox
            object['iscrowd'] = obj.iscrowd
            object['note'] = obj.note
            dataset['objects'].append(object)
        with open(self.label_path, 'w') as f:
            dump(dataset, f, indent=4)
        return True

    def save_labelme(self):
        dataset = {}
        dataset['version'] = "5.2.0.post4"
        dataset['flags'] = {}
        dataset['shapes'] = []
        for obj in self.objects:
            object = {}
            object['label'] = obj.category
            if obj.group is None:
                object['group_id'] = 0
            object['points'] = obj.segmentation
            object['description'] = ""
            object['shape_type'] = "polygon"
            object['flags'] = {}
            dataset['shapes'].append(object)
        dataset['imageData'] = img_arr_to_b64(self.image)
        dataset['imagePath'] = self.img_name
        dataset['imageWidth'] = self.width
        dataset['imageHeight'] = self.height
        with open(self.label_path, 'w') as f:
            dump(dataset, f, indent=4)
        return True
