import os
import ssl
import pandas as pd
from tensorflow import keras
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.preprocessing import MultiLabelBinarizer

ssl._create_default_https_context = ssl._create_unverified_context

data_dir = '.'  
images_dir = os.path.join(data_dir, 'Food Images')
csv_file = 'Food Ingredients and Recipe Dataset with Image Name Mapping.csv'

df = pd.read_csv(os.path.join(data_dir, csv_file))

df['Image_Path'] = df['Image_Name'].apply(lambda x: os.path.join(images_dir, x))
df = df[df['Image_Path'].apply(os.path.isfile)]

train_df = df.sample(frac=0.8, random_state=42)
val_df = df.drop(train_df.index)

mlb = MultiLabelBinarizer()
train_ingredients = mlb.fit_transform(train_df['Cleaned_Ingredients'])
val_ingredients = mlb.transform(val_df['Cleaned_Ingredients'])

datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)

train_generator = datagen.flow_from_dataframe(
    dataframe=train_df,
    x_col='Image_Path',  
    y_col=train_df.columns[1:],  
    target_size=(224, 224),
    batch_size=32,
    class_mode='raw',  
    subset='training'
)

val_generator = datagen.flow_from_dataframe(
    dataframe=val_df,
    x_col='Image_Path',  
    y_col=val_df.columns[1:],  
    target_size=(224, 224),
    batch_size=32,
    class_mode='raw',  
    subset='validation'
)

base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dense(512, activation='relu'),
    Dropout(0.5),
    Dense(len(mlb.classes_), activation='sigmoid')  
])

optimizer = Adam(learning_rate=0.0001)
model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

history = model.fit(
    train_generator,
    steps_per_epoch=len(train_generator),
    validation_data=val_generator,
    validation_steps=len(val_generator),
    epochs=10
)

model.save('food_ingredients_model.h5')