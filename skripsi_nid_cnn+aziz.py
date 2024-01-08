# -*- coding: utf-8 -*-
"""skripsi-NID-CNN+Aziz.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14NXD3rkM9ckmbR-Y-Q5c7jky-vlM6mNB

Dataset: https://www.kaggle.com/datasets/sampadab17/network-intrusion-detection
"""

from google.colab import drive
drive.mount('/content/drive')

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, GlobalAveragePooling1D, Dense, Embedding, Flatten, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from tensorflow.keras.callbacks import ModelCheckpoint
from keras.models import load_model

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import GradientBoostingClassifier

import matplotlib.pyplot as plt

classifiers = {
    'CNN': (0, 0, 0),
    'SVM': (0, 0, 0),
    'DTree': (0, 0, 0),
    'KNN': (0, 0, 0),
    'GNB': (0, 0, 0),
    'GBoost': (0, 0, 0)
}

path_data = '/content/drive/MyDrive/NID_dataset/NID_dataset.csv'
path_model = '/content/drive/MyDrive/NID_dataset/nid_model.h5'

# Load dataset
data = pd.read_csv(path_data)
data

# Menghitung jumlah data berdasarkan nilai di kolom "class"
jumlah_data_class = data['class'].value_counts()

print("Jumlah data berdasarkan nilai 'class':")
print(jumlah_data_class)

labels = ['No', 'Network Intrusi']

data.info()

# Menghitung jumlah data tiap kategori pada kolom "protocol_type"
protocol_type_counts = data['protocol_type'].value_counts()

# Membuat DataFrame dengan hasil perhitungan
result_df = pd.DataFrame({'Count': protocol_type_counts})

print("Data Protocol")
print(result_df)

# Menghitung jumlah data tiap kategori pada kolom "service"
service_counts = data['service'].value_counts()

# Membuat DataFrame dengan hasil perhitungan
result_df = pd.DataFrame({'Count': service_counts})

print("Data Service")
print(result_df)

# Menghitung jumlah data tiap kategori pada kolom "flag"
flag_counts = data['flag'].value_counts()

# Membuat DataFrame dengan hasil perhitungan
result_df = pd.DataFrame({'Count': flag_counts})

print("Data Flag")
print(result_df)

# Menghitung jumlah data tiap kategori pada kolom "class"
class_counts = data['class'].value_counts()

# Membuat DataFrame dengan hasil perhitungan
result_df = pd.DataFrame({'Count': class_counts})

print("Data Class")
print(result_df)

data.describe().transpose()

kolom_text = ['protocol_type', 'service', 'flag', 'class']
data[kolom_text] = data[kolom_text].apply(lambda x: pd.factorize(x)[0])

data[['protocol_type', 'service', 'flag', 'class']]

def normalisasi(df):
  df_norm = (df-df.min())/(df.max()-df.min())
  return df_norm

kolom_skala = ['duration', 'src_bytes',	'dst_bytes', 'hot', 'num_compromised', 'num_root', 'num_file_creations', 'count','srv_count','dst_host_count','dst_host_srv_count']
data[kolom_skala] = normalisasi(data[kolom_skala])

data[['duration', 'src_bytes',	'dst_bytes', 'hot', 'num_compromised', 'num_root', 'num_file_creations', 'count','srv_count','dst_host_count','dst_host_srv_count']]

# Shuffle dataset
data = data.sample(frac=1).reset_index(drop=True)

data.info()

num_output = data['class'].unique().size
num_output

X = data.iloc[:, :-1].values  # Features :column selain class
y = data.iloc[:, -1].values   # Target : class

# Split dataset
X_trains, X_tests, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=21)

# menghitung jumlah data normal dan anomali pada data training
jumlah_normal_train = sum(y_train == 0)
jumlah_anomali_train = sum(y_train == 1)

print("Jumlah data dengan label 'normal' pada data training:", jumlah_normal_train)
print("Jumlah data dengan label 'anomali' pada data training:", jumlah_anomali_train)

# menghitung jumlah data normal dan anomali pada data testing
jumlah_normal_test = sum(y_test == 0)
jumlah_anomali_test = sum(y_test == 1)

print("Jumlah data dengan label 'normal' pada data testing:", jumlah_normal_test)
print("Jumlah data dengan label 'anomali' pada data testing:", jumlah_anomali_test)

"""# Convolutional Neural Network"""

# Zero padding
padding_value = 100  # Choose a value suitable for your dataset
X_train = np.pad(X_trains, ((0, 0), (0, padding_value - X_trains.shape[1])), mode='constant')
X_test = np.pad(X_tests, ((0, 0), (0, padding_value - X_tests.shape[1])), mode='constant')

# Reshape input data for CNN
X_train = X_train.reshape(X_train.shape[0], padding_value, 1)
X_test = X_test.reshape(X_test.shape[0], padding_value, 1)

# Learning Rate Scheduling
lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(initial_learning_rate=0.001, decay_steps=10000, decay_rate=0.9)
optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)

# Define the ModelCheckpoint callback
val_checkpoint = ModelCheckpoint(path_model, monitor='val_accuracy', save_best_only=True, save_weights_only=False, mode='max', verbose=1)

# Build CNN 1D model
model = Sequential([
    Conv1D(128, 3, activation='relu', input_shape=(padding_value, 1)),
    MaxPooling1D(),
    Dropout(0.3),
    Conv1D(256, 3, activation='relu'),
    MaxPooling1D(),
    Dropout(0.3),
    Conv1D(512, 3, activation='relu'),
    GlobalAveragePooling1D(),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(1, activation='sigmoid')
])

if(num_output == 2):
  model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
else:
  model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

model.summary()

# Train the model
history = model.fit(X_train, y_train, epochs=200, batch_size=64, validation_data=(X_test, y_test), callbacks=[val_checkpoint])

# Plot accuracy
plt.figure(figsize=(10, 5))
plt.plot(history.history['accuracy'], label='train_accuracy')
plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.ylim([0, 1])
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')
plt.show()

accuracy = history.history['accuracy']
val_accuracy = history.history['val_accuracy']

print("Train_Accuracy", accuracy)
print("Val_Accuracy", val_accuracy)

# Plot loss
plt.figure(figsize=(10, 5))
plt.plot(history.history['loss'], label='train_loss')
plt.plot(history.history['val_loss'], label = 'val_loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.ylim([0, 1])
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

loss = history.history['loss']
val_loss = history.history['val_loss']

print("Train_Loss", loss)
print("Val_Loss", val_loss)

mymodel = load_model(path_model)

# Evaluate the model
y_pred = mymodel.predict(X_test)
y_pred_classes = (y_pred > 0.5).astype(int)

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred_classes))

print("\nClassification Report:")
print(classification_report(y_test, y_pred_classes, target_names=labels))

report = classification_report(y_test, y_pred_classes, output_dict=True)['weighted avg']
classifiers['CNN'] = (report['precision'], report['recall'], report['f1-score'])

"""# SVM with RBF Kernel"""

# SVM
clf_SVM = SVC(kernel='rbf', C=2)
clf_SVM.fit(X_trains, y_train)
y_pred = clf_SVM.predict(X_tests)

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=labels))

report = classification_report(y_test, y_pred, output_dict=True)['weighted avg']
classifiers['SVM'] = (report['precision'], report['recall'], report['f1-score'])

"""# Decision Tree with 'Entropy' criterion"""

# Decision Tree
clf_DT = DecisionTreeClassifier(criterion='entropy', max_depth=5)
clf_DT.fit(X_trains, y_train)
y_pred = clf_DT.predict(X_tests)

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=labels))

report = classification_report(y_test, y_pred, output_dict=True)['weighted avg']
classifiers['DTree'] = (report['precision'], report['recall'], report['f1-score'])

"""# K-Nearest Neighbors (KNN)"""

clf_KNN = KNeighborsClassifier(n_neighbors=7)
clf_KNN.fit(X_trains, y_train)
y_pred = clf_KNN.predict(X_tests)

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=labels))

report = classification_report(y_test, y_pred, output_dict=True)['weighted avg']
classifiers['KNN'] = (report['precision'], report['recall'], report['f1-score'])

"""# Gaussian Naive Bayes"""

# Gaussian Naive bayes
clf_NB = GaussianNB()
clf_NB.fit(X_trains, y_train)
y_pred = clf_NB.predict(X_tests)

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=labels))

report = classification_report(y_test, y_pred, output_dict=True)['weighted avg']
classifiers['GNB'] = (report['precision'], report['recall'], report['f1-score'])

"""# Gradient Boost"""

clf_GR = GradientBoostingClassifier()
clf_GR.fit(X_trains, y_train)
y_pred = clf_GR.predict(X_tests)

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=labels))

report = classification_report(y_test, y_pred, output_dict=True)['weighted avg']
classifiers['GBoost'] = (report['precision'], report['recall'], report['f1-score'])

"""# Perbandingan Model"""

precision   = [classifiers[model][0] for model in classifiers.keys()]
recall      = [classifiers[model][1] for model in classifiers.keys()]
f1_score    = [classifiers[model][2] for model in classifiers.keys()]
annot        = [f'{clf}\nf1-score: {classifiers[clf][2]:.2%}' for clf in classifiers]

plt.title('Comparison of Different Models')
plt.scatter(recall, precision)

# Add label to data points
margin = 0.002
for (x, y, t) in zip(recall, precision, annot):
    plt.text(x + margin, y + margin, t)

plt.xlabel('Recall'), plt.ylabel('Precision')
plt.grid()

plt.tight_layout()
plt.savefig('ModelComparison.jpg', dpi=300)
plt.show()