import os
import copy
import random
import argparse
import xml.etree.ElementTree as ET
import numpy as np
from fsdet.utils.file_io import PathManager

PTower_CLASSES = ['broken', 'laughcrack', 'damage', 'corroison', 'rust', 'endjump', 'bondlinebroken', 'straightpipebend']


def rename_img_file():
    src_datadir = "powertower"
    dst_dir = src_datadir + "new"
    index = 0
    os.makedirs(dst_dir, exist_ok=True)
    rename_txt = "powertower_rename.txt"
    with open(rename_txt, "w") as fw:
        for sub_folder in os.listdir(src_datadir):
            sub_dir = os.path.join(src_datadir, sub_folder)
            for cur_f in os.listdir(sub_dir):
                cur_img = os.path.join(sub_dir, cur_f)
                cur_img_new_name = "%04d.jpg" % index
                cur_img_new = os.path.join(dst_dir, cur_img_new_name)
                os.system("mv %s %s" % (cur_img, cur_img_new))
                index += 1
                fw.write("%s ==> %s" % (os.path.join(sub_folder, cur_f), cur_img_new_name) + "\n")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--seeds", type=int, nargs="+", default=[1, 20], help="Range of seeds"
    )
    args = parser.parse_args()
    return args


def analysis_xml_create_trainval():
    anno_dir = "powertower/Annotations"
    txt_dir = "powertower/ImageSets"
    allimg_list = []
    data_per_cat = {c: [] for c in PTower_CLASSES}
    for cur_f in os.listdir(anno_dir):
        allimg_list.append(cur_f.replace(".xml", ""))
        anno_file = os.path.join(anno_dir, cur_f)
        tree = ET.parse(anno_file)
        clses = []
        for obj in tree.findall("object"):
            cls = obj.find("name").text
            clses.append(cls)
        for cls in set(clses):
            data_per_cat[cls].append(cur_f.replace(".xml", ""))

    test_img_list = []
    for c in data_per_cat.keys():
        print(c, "has images: ", len(data_per_cat[c]))
        cur_test = random.sample(data_per_cat[c], 3)
        test_img_list += cur_test
    test_img_list = list(set(test_img_list))
    trainval_img_list = list(set(allimg_list) - set(test_img_list))
    traintxt_f = "powertower_all1_trainval.txt"
    with open(os.path.join(txt_dir, traintxt_f), "w") as fp:
        fp.write("\n".join(trainval_img_list) + "\n")

    test_f = "powertower_all1_test.txt"
    with open(os.path.join(txt_dir, test_f), "w") as fp:
        fp.write("\n".join(test_img_list) + "\n")


def generate_seeds(args):
    dirname = "datasets/powertower"
    data = []
    data_per_cat = {c: [] for c in PTower_CLASSES}
    data_file = "datasets/powertower/ImageSets/Main/trainval.txt"
    with PathManager.open(data_file) as f:
        fileids = np.loadtxt(f, dtype=np.str).tolist()
    data.extend(fileids)
    for fileid in data:
        anno_file = os.path.join(dirname, "Annotations", fileid + ".xml")
        tree = ET.parse(anno_file)
        clses = []
        for obj in tree.findall("object"):
            cls = obj.find("name").text
            clses.append(cls)
        for cls in set(clses):
            data_per_cat[cls].append(anno_file)

    result = {cls: {} for cls in data_per_cat.keys()}
    shots = [1, 5, 10]
    for i in range(args.seeds[0], args.seeds[1]):
        random.seed(i)
        for c in data_per_cat.keys():
            c_data = []
            for j, shot in enumerate(shots):
                diff_shot = shots[j] - shots[j - 1] if j != 0 else 1
                shots_c = random.sample(data_per_cat[c], diff_shot)
                num_objs = 0
                for s in shots_c:
                    if s not in c_data:
                        tree = ET.parse(s)
                        file = tree.find("filename").text
                        name = os.path.join(dirname, "JPEGImages/{}".format(file))
                        c_data.append(name)
                        for obj in tree.findall("object"):
                            if obj.find("name").text == c:
                                num_objs += 1
                        if num_objs >= diff_shot:
                            break
                result[c][shot] = copy.deepcopy(c_data)
        save_path = "datasets/powertowersplit/seed{}".format(i)
        os.makedirs(save_path, exist_ok=True)
        for c in result.keys():
            for shot in result[c].keys():
                filename = "box_{}shot_{}_train.txt".format(shot, c)
                with open(os.path.join(save_path, filename), "w") as fp:
                    fp.write("\n".join(result[c][shot]) + "\n")


if __name__ == "__main__":
    args = parse_args()
    # rename_img_file()
    # analysis_xml_create_trainval()
    generate_seeds(args)

'''
#------v1_11_25---------
broken has images:  61
laughcrack has images:  159
damage has images:  13
corroison has images:  37
rust has images:  313
endjump has images:  26
bondlinebroken has images:  21
straightpipebend has images:  25
'''