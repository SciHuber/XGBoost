'''
xgboost 官网
https://xgboost.readthedocs.io/en/latest/python/python_intro.html#setting-parameters
重复一下博客内容
https://blog.csdn.net/sb19931201/article/details/52577592
本文用的数据来自kaggle，相信搞机器学习的同学们都知道它，kaggle上有几个老题目一直开放，
适合给新手练级，上面还有很多老司机的方案共享以及讨论，非常方便新手入门。
这次用的数据是Classify handwritten digits using the famous MNIST data—手写数字识别，
每个样本相当于一个图片像素矩阵（28x28）
'''

import numpy as np
import pandas as pd
import xgboost as xgb
#from sklearn.cross_validation import train_test_split
#sklearn.cross_valition 已经不用了，用 sklearn.model_selection
from sklearn.model_selection import train_test_split
#记录程序运行时间
import time 
start_time = time.time()

#读入数据
train = pd.read_csv("train.csv")
tests = pd.read_csv("test.csv") 

#用sklearn.cross_validation进行训练数据集划分，这里训练集和交叉验证集比例为7：3，可以自己根据需要设置
train_xy,val = train_test_split(train, test_size = 0.3,random_state=1)

y = train_xy.label
X = train_xy.drop(['label'],axis=1)
val_y = val.label
val_X = val.drop(['label'],axis=1)

#xgb矩阵赋值
xgb_val = xgb.DMatrix(val_X,label=val_y)
xgb_train = xgb.DMatrix(X, label=y)
xgb_test = xgb.DMatrix(tests)

param = {}

param['booster']='gbtree'
param['objective']='multi:softmax'
param['num_class']=10
param['gamma']=0.1
param['max_depth']=12
param['lambda']=2
param['subsample']=0.7
param['colsample_bytree']=0.7
param['min_child_weight']=3
param['silent']=0
param['eta']=0.007
param['seed']=1000
param['nthread']=7

'''
这种参数设置方式也可以
params={
'booster':'gbtree',
'objective': 'multi:softmax', #多分类的问题
'num_class':10, # 类别数，与 multisoftmax 并用
'gamma':0.1,  # 用于控制是否后剪枝的参数,越大越保守，一般0.1、0.2这样子。
'max_depth':12, # 构建树的深度，越大越容易过拟合
'lambda':2,  # 控制模型复杂度的权重值的L2正则化项参数，参数越大，模型越不容易过拟合。
'subsample':0.7, # 随机采样训练样本
'colsample_bytree':0.7, # 生成树时进行的列采样
'min_child_weight':3, 
# 这个参数默认是 1，是每个叶子里面 h 的和至少是多少，对正负样本不均衡时的 0-1 分类而言
#，假设 h 在 0.01 附近，min_child_weight 为 1 意味着叶子节点中最少需要包含 100 个样本。
#这个参数非常影响结果，控制叶子节点中二阶导的和的最小值，该参数值越小，越容易 overfitting。 
'silent':0 ,#设置成1则没有运行信息输出，最好是设置为0.
'eta': 0.007, # 如同学习率
'seed':1000,
'nthread':7,# cpu 线程数
#'eval_metric': 'auc'
}
'''
plst = list(params.items())
num_rounds = 5000 # 迭代次数
watchlist = [(xgb_train, 'train'),(xgb_val, 'val')]

#训练模型并保存
# early_stopping_rounds 当设置的迭代次数较大时，early_stopping_rounds 可在一定的迭代次数内准确率没有提升就停止训练
model = xgb.train(plst, xgb_train, num_rounds, watchlist,early_stopping_rounds=100)
model.save_model('./model/xgb.model') # 用于存储训练出的模型
print "best best_ntree_limit",model.best_ntree_limit 


preds = model.predict(xgb_test,ntree_limit=model.best_ntree_limit)

np.savetxt('xgb_submission.csv',np.c_[range(1,len(tests)+1),preds],delimiter=',',header='ImageId,Label',comments='',fmt='%d')

#输出运行时长
cost_time = time.time()-start_time
print "xgboost success!",'\n',"cost time:",cost_time,"(s)......"
