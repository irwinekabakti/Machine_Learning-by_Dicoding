# -*- coding: utf-8 -*-
"""satellite.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Xql5p9V36gB612vcbQ_Hy8JoLBbSQOjp
"""

!chmod 600 /content/kaggle.json

! KAGGLE_CONFIG_DIR=/content/ kaggle datasets download -d mahmoudreda55/satellite-image-classification

import zipfile
zip_file = zipfile.ZipFile('/content/satellite-image-classification.zip')
zip_file.extractall('/tmp/')

import tensorflow as tf
device_name = tf.test.gpu_device_name()
if device_name != '/device:GPU:0':
  raise SystemError('GPU device not found')
print('Found GPU at: {}'.format(device_name))

import tensorflow as tf
tf.device('/device:GPU:0')

import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator 

from PIL import Image
total = 0

import os

satellite_full_file = os.path.join('/tmp/data')

print(os.listdir(satellite_full_file))

list_sattelite = os.listdir(satellite_full_file)
print(list_sattelite)

for x in list_sattelite:
  dir = os.path.join(satellite_full_file, x)
  y = len(os.listdir(dir))
  print(x+':', y)
  total = total + y
  
  img_name = os.listdir(dir)
  for z in range(4):
    img_path = os.path.join(dir, img_name[z])
    img = Image.open(img_path)
    print('-',img.size)
  print('---------------')

print('\nTotal :', total)

fig, ax = plt.subplots(2, 2, figsize=(15,15))
fig.suptitle("Pick random images : ", fontsize=24)
satellite_sorted = sorted(list_sattelite)
satellite_id = 0
for i in range(2):
  for j in range(2):
    try:
      satellite_selected = satellite_sorted[satellite_id] 
      satellite_id += 1
    except:
      break
    if satellite_selected == '.TEMP':
        continue
    satellite_selected_images = os.listdir(os.path.join(satellite_full_file, satellite_selected))
    satellite_selected_random = np.random.choice(satellite_selected_images)
    img = plt.imread(os.path.join(satellite_full_file, satellite_selected, satellite_selected_random))
    ax[i][j].imshow(img)
    ax[i][j].set_title(satellite_selected, pad=10, fontsize=22)
    
plt.setp(ax, xticks=[],yticks=[])
plt.show

train_datagen_satellite = ImageDataGenerator(
    validation_split=0.2,   
    rescale=1./255,
    horizontal_flip=True,
    fill_mode='nearest',
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
)

batch_size = 128

data_train = train_datagen_satellite.flow_from_directory(
    satellite_full_file,
    target_size=(150, 150),
    batch_size = batch_size,
    class_mode='categorical',
    subset='training')

data_val = train_datagen_satellite.flow_from_directory(
    satellite_full_file, 
    target_size =(150, 150),
    batch_size = batch_size,
    class_mode = 'categorical',
    subset='validation')

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(64, (3,3), activation='relu', input_shape=(150, 150, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),
    
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    
    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    
    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dropout(0.5), 
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(4, activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics = ['accuracy'])

model.summary()

class historyCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy') > 0.95 and logs.get('val_accuracy') > 0.95):
      print("\n The Accuracy is up to > 95%, and forced to stop!")
      self.model.stop_training = True

callbacks = historyCallback()

history = model.fit(data_train, 
                    epochs = 200, 
                    steps_per_epoch = data_train.samples // batch_size,
                    validation_data = data_val, 
                    validation_steps = data_val.samples // batch_size,
                    verbose = 1,
                    callbacks = [callbacks])

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Graphic Accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Grapchic Loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with tf.io.gfile.GFile('model.tflite', 'wb') as f:
  f.write(tflite_model)