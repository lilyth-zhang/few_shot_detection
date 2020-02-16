import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join
import argparse


# parser = argparse.ArgumentParser()
# parser.add_argument('--type', type=str, choices=['1c', 'all'], required=True)
# args = parser.parse_args()


# sets=[('2012', 'train'), ('2012', 'val'), ('2007', 'train'), ('2007', 'val'), ('2007', 'test')]
sets=['office', 'chshop', 'mozi', '3f']

set2cls = {'office':"head1", 'chshop':"head2", 'mozi':"head3", '3f':"head4"}

classes = ["head1", "head2", "head3", "head4"]

def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def convert_annotation(name, class_name, image_id):
    in_file = open('merge/%s/annotation/%s.xml'%(name, image_id), encoding = 'utf8')
    print(in_file)
    out_file = open('merge/%s/labels_1c/%s/%s.txt'%(name, class_name, image_id), 'w')
    tree=ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = set2cls[name]
        if cls != class_name or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
#         cls_id = 0
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')


wd = getcwd()

if not os.path.exists('voclist'):
    os.mkdir('voclist')

for name in sets:    # sets=['office', 'chshop', 'mozi', '3f']
    image_ids = []
    for ids in os.listdir('merge/%s/annotation'%(name)):
        if not ids.startswith('.'):
            image_ids.append(ids[:-4])

    # File to save the image path list
    class_name = set2cls[name]
    list_file = open('voclist/%s_train.txt'%(class_name), 'w')

    # File to save the image labels
    label_dir = 'labels_1c/' + class_name
    if not os.path.exists('merge/%s/%s/'%(name, label_dir)):
        os.makedirs('merge/%s/%s/'%(name, label_dir))

    # Traverse all images
    for image_id in image_ids:
        list_file.write('%s/merge/%s/jpegimgs/%s.jpg\n'%(wd, name, image_id))
        convert_annotation(name, class_name, image_id)
    list_file.close()

#     files = [
#         'voclist/2007_{}_train.txt'.format(class_name),
#         'voclist/2007_{}_val.txt'.format(class_name),
# #         'voclist/2012_{}_*.txt'.format(class_name)
#     ]
#     files = ' '.join(files)
#     cmd = 'cat ' + files + '> voclist/{}_train.txt'.format(class_name)
#     os.system(cmd)