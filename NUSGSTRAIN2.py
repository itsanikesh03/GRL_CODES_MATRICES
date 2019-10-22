from keras.models import Sequential, Model, load_model
from keras.layers import Dense, Activation, GaussianNoise, Dropout, BatchNormalization
from keras import initializers
from keras.optimizers import SGD, Nadam, RMSprop
from keras.constraints import maxnorm
from keras.regularizers import l2
from keras.layers.advanced_activations import LeakyReLU, PReLU
#from keras.wrappers.scikit_learn import KerasRegressor
#from sklearn import preprocessing 
#from sklearn.preprocessing import MinMaxScaler
#from sklearn.pipeline import Pipeline
#from scipy.stats.stats import pearsonr
#from scikit_learn.model_selection import train_test_split
#from scikit_learn.metrics import mean_absolute_error
import numpy as np
import tensorflow as tf
import keras.backend as kb
import keras.backend as K
import os
import threading
import random

os.environ["CUDA_VISIBLE_DEVICES"] = '1' #use GPU with ID=0
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.5 # maximun alloc gpu50% of MEM
config.gpu_options.allow_growth = True #allocate dynamically

#from netCDF4 import Dataset

def rae(y_true, y_pred):
  return tf.reduce_sum(tf.abs(y_pred-y_true)) / tf.reduce_sum(tf.abs(y_true))

def mae(y_true, y_pred):
  return tf.reduce_mean(tf.abs(y_pred-y_true))

def mape(y_true, y_pred):
  diff = tf.abs((y_true - y_pred) / (tf.abs(y_true)))
  return 100. * tf.reduce_mean(diff)

def mean_absolute_percentage_error(y_true, y_pred):
    diff = K.abs((y_true - y_pred) / K.clip(K.abs(y_true), K.epsilon(), np.inf))
    return 100. * K.mean(diff)

def rmse(y_true, y_pred):
    return K.sqrt(K.mean(K.square(y_pred - y_true)))

# reading the input data

#SGSDATA = np.genfromtxt('NUSGS.dat')
SGSDATA = np.load('RANDOMDATA/NUSGSTRAIN.npy')
SGSDATA2 = np.load('RANDOMDATA/TESTING_DATA.npy')
#random.shuffle(SGSDATA)
print (SGSDATA.shape)
print (SGSDATA2.shape)

#np.save('NUSGS.npy',SGSDATA)

#X_train0 = SGSDATA[:,0:9]
Y_train = -SGSDATA[:,13]
Y_test  = -SGSDATA2[:,13]
SGSDATA = np.delete(SGSDATA,3,1)
SGSDATA2 = np.delete(SGSDATA2,3,1)

print (SGSDATA.shape)
print (SGSDATA2.shape)

X_train = SGSDATA[:,0:9]
X_test = SGSDATA2[:,0:9]

print (Y_train,X_train)

#X_train, X_test, Y_train, Y_test = train_test_split(X_train0,Y_train0, test_size=0.1, random_state=42)
#print (X_train.shape, X_test.shape, Y_train.shape, Y_test.shape)

XMEAN=np.max(X_train,axis=0) #np.mean(X_train,axis=0)
XSTDD=np.min(X_train,axis=0)

#print XMEAN, XSTDD
np.savetxt('xnmax.dat',XMEAN)
np.savetxt('xnmin.dat',XSTDD)

for j in range(9):
 X_train[:,j]= (X_train[:,j]-XSTDD[j])/(XMEAN[j]-XSTDD[j]) #(X_train[:,j]-XMEAN[j])/XSTDD[j]
 X_test[:,j] = (X_test[:,j]-XSTDD[j])/(XMEAN[j]-XSTDD[j])  #(X_test[:,j]-XMEAN[j])/XSTDD[j]

#print XMEAN,XSTDD

YMEAN=np.max(Y_train,axis=0) #np.mean(Y_train,axis=0)
YSTDD=np.min(Y_train,axis=0) #np.std(Y_train,axis=0)
YDATA = np.zeros((2))
YDATA[0] = YMEAN
YDATA[1] = YSTDD
print (YDATA.shape)
print (YDATA)

np.savetxt('ynmax.dat',YDATA)

Y_train[:]=(Y_train[:]-YSTDD)/(YMEAN-YSTDD) #(Y_train[:]-YMEAN)/YSTDD
Y_test[:] =(Y_test[:]-YSTDD)/(YMEAN-YSTDD)

print (YMEAN,YSTDD)

#fix random seed for reproducibility
seed = 7
np.random.seed(seed)

model = Sequential()
model.add(Dense(16, input_dim=9,       kernel_initializer='uniform', activation = 'relu'))
model.add(Dense(16,                    kernel_initializer='uniform', activation = 'relu'))
model.add(Dense(16,                    kernel_initializer='uniform', activation = 'relu'))
model.add(Dense(1,                     kernel_initializer='uniform'))
# Compile model
model.compile(loss='mean_squared_error', optimizer='rmsprop')
history = model.fit(X_train,Y_train, epochs=100, batch_size=240,validation_split=0.24822695035)

score  = model.predict(X_test)
score[:]=score[:]*(YMEAN-YSTDD)+YSTDD #score[:]*YSTDD+YMEAN

print("Larger: %.2f (%.2f) MSE" % (score.mean(), score.std()))

W_Input_Hidden0 = model.layers[0].get_weights()[0]; print (W_Input_Hidden0.shape)
biases0  = model.layers[0].get_weights()[1]; print (biases0.shape)
W_Input_Hidden1 = model.layers[1].get_weights()[0]; print (W_Input_Hidden1.shape)
biases1  = model.layers[1].get_weights()[1]; print (biases1.shape)
W_Input_Hidden2 = model.layers[2].get_weights()[0]; print (W_Input_Hidden2.shape)
biases2  = model.layers[2].get_weights()[1]; print (biases2.shape)
W_Input_Hidden3 = model.layers[3].get_weights()[0]; print (W_Input_Hidden3.shape)
biases3  = model.layers[3].get_weights()[1]; print (biases3.shape)

np.save('SWNHidden003.npy',W_Input_Hidden0)
np.save('SWNbiases003.npy',biases0)
np.save('SWNHidden013.npy',W_Input_Hidden1)
np.save('SWNbiases013.npy',biases1)
np.save('SWNHidden023.npy',W_Input_Hidden2)
np.save('SWNbiases023.npy',biases2)
np.save('SWNHidden033.npy',W_Input_Hidden3)
np.save('SWNbiases033.npy',biases3)
np.save('SWNX_test3.npy', X_test)
np.save('SWNY_test3.npy', Y_test)
np.save('SWNScore3.npy', score)

print(history.history.keys())
train_loss = history.history['loss']
val_loss   = history.history['val_loss']
np.save('train_lossN.npy',train_loss)
np.save('val_lossN.npy',val_loss)
