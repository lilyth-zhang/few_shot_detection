# 基于特征重加权(Feature Reweighting)模块的小样本检测人头算法

本代码基于  [https://github.com/bingykang/Fewshot_Detection](https://github.com/bingykang/Fewshot_Detection) 

论文全文见 [Few-shot Object Detection via Feature Reweighting](https://arxiv.org/abs/1812.01866), ICCV 2019

[Bingyi Kang](https://scholar.google.com.sg/citations?user=NmHgX-wAAAAJ)\*, [Zhuang Liu](https://liuzhuang13.github.io)\*, [Xin Wang](https://people.eecs.berkeley.edu/~xinw/), [Fisher Yu](https://www.yf.io), [Jiashi Feng](https://sites.google.com/site/jshfeng/home) and [Trevor Darrell](https://people.eecs.berkeley.edu/~trevor/) (\* equal contribution)

代码运行环境为 Python 3.5 & PyTorch 0.4.0。


## 检测样例 (20-shot)

<div align=center>
<img src="https://i.loli.net/2020/01/10/M9KIx4vB56NeAC1.jpg" width="740">
</div>

<div align=center>
采用20-shot的新类训练图片来检测新背景下的人头效果示例。
</div> 

## 论文模型框架
<div align=center>
<img src="https://user-images.githubusercontent.com/8370623/67256408-ad583e00-f43b-11e9-806e-47d79acecaed.png" width="740">
</div>

论文提出的小样本检测模型的框架接结构。它由元特征提取器和特征重加权模块组成。特征提取器遵循单阶段检测模型结构，直接对目标得分（objectness score）、检测框位置（x、y、h、w）和分类得分（classification score）进行回归。重加权模块被训练成将N个类的支持样本映射到N个重加权向量，每个重加权向量负责调整元特征以检测来自相应类的对象。最终输出采用基于softmax的分类评分标准化。


## 本实验应用场景
现有三种不同场景（A,B,C）下的人头标注数据共7007张，想要训练一个模型在D场景下也能用于人头检测的模型，但D场景的标注图片数量有限，仅有20张。

## 在自己的数据集上训练模型

- ``` $PROJ_ROOT : project root ```
- ``` $DATA_ROOT : dataset root ```

### Prepare dataset
+ 进入数据集路径，将数据存放在DATA_ROOT中
```
cd $DATA_ROOT
```

+ 为数据加上标签，需要修改sunmi_label.py内容，如类别和数据路径等。
```
python sunmi_label.py
cat chshop_train.txt mozi_train.txt office.txt > sunmi_train.txt
cat 3f_train.txt > 3f_test.txt
```

+ 产生单类别标签 (used for meta inpput)
```
python sunmi_label_1c.py
```

+ 产生小样本检测图片列表
新类的检测图片列表（分为1_shot,3_shot,5_shot等）
```
python scripts/gen_few_fewlist.py 
```


### Base Training
+ 修改cfg配置
修改文件 data/metayolo.data file 
```
metayolo = 1
metain_type = 2
data = sunmi
neg = 1
rand = 0
novel = data/sunmi_novels.txt             // file contains novel splits
novelid = 0                             // which split to use
scale = 1
meta = data/voc_traindict_full.txt
train = $DATA_ROOT/sunmi_train.txt
valid = $DATA_ROOT/3f_test.txt
backup = backup/metayolo
gpus = 0,1,2,3
```


+ 训练模型
```
python train_meta.py cfg/metayolo.data cfg/darknet_dynamic.cfg cfg/reweighting_net.cfg darknet19_448.conv.23
```

+ 模型评估
```
python valid_ensemble.py cfg/metayolo.data cfg/darknet_dynamic.cfg cfg/reweighting_net.cfg path/toweightfile
python scripts/voc_eval.py results/path/to/comp4_det_test_
```

### fine-tuning
+ 修改cfg文件
修改fine-tuning阶段的模型配置 data/metatune.data file 
```
metayolo = 1
metain_type = 2
data = sunmi
tuning = 1
neg = 0
rand = 0
novel = data/sunmi_novels.txt                 
novelid = 0
max_epoch = 2000
repeat = 200
dynamic = 0
scale = 1
train = $DATA_ROOT/sunmi_train.txt
meta = data/voc_traindict_bbox_5shot.txt
valid = $DATA_ROOT/3f_test.txt
backup = backup/metatune
gpus  = 0,1,2,3
```


+ 训练模型
```
python train_meta.py cfg/metatune.data cfg/darknet_dynamic.cfg cfg/reweighting_net.cfg path/to/base/weightfile
```

+ 模型评估
```
python valid_ensemble.py cfg/metatune.data cfg/darknet_dynamic.cfg cfg/reweighting_net.cfg path/to/tuned/weightfile
python scripts/voc_eval.py results/path/to/comp4_det_test_
```

## 与基线模型yolov2的对比

- ``` $PROJ_ROOT : yolov2/pytorch-yolo2-master ```
- ``` $DATA_ROOT : yolov2/data_root ```


### Prepare dataset
+ 进入数据集路径，将上述模型使用的数据复制到该路径下

```
cd yolov2/data_root
cp /FEW_SHOT_MODEL_ROOT/data_root/sunmi_train.txt /yolov2/data_root
cp /FEW_SHOT_MODEL_ROOT/data_root/voclist/5shot_head4_train.txt /yolov2/data_root
cat sunmi_train.txt 5shot_head4_train.txt > sunmi_train.txt
cp /FEW_SHOT_MODEL_ROOT/data_root/3f_test.txt /yolov2/data_root
```

### Model training
```
python train.py cfg/sunmi.data cfg/yolo-sunmi.cfg darknet19_448.conv.23
```

### Model evaluating
```
python valid.py cfg/sunmi.data cfg/yolo-sunmi.cfg yolo-sunmi.weights
python scripts/voc_eval.py results/comp4_det_test_
```


## 结果对比

 id      | training set       | val set | mAP@416 | epoch   | lr         | Notes
---      |---                 |---      |---      |---      |---         |---
  0      | A + B + C          | D       |  67.48  |  410    | 0.00033    | few_shot(5-shot)
  1      | A + B + C          | D       |  67.42  |  410    | 0.001      | yolov2(5-shot)
  2      | A + B + C          | D       |  78.71  |  410    | 0.00033    | few_shot(20-shot)
  3      | A + B + C          | D       |  76.78  |  410    | 0.001      | yolov2(20-shot)
