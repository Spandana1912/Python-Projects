import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import to_categorical

DATA_PATH = "collected_data"
IMG_SIZE = 64

images = []
labels = []

print("[INFO] Loading dataset...")

for label in os.listdir(DATA_PATH):
    folder_path = os.path.join(DATA_PATH, label)

    for img_name in os.listdir(folder_path):
        img_path = os.path.join(folder_path, img_name)
        img = cv2.imread(img_path)

        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        img = img / 255.0  # Normalize
        images.append(img)
        labels.append(int(label))

images = np.array(images)
labels = to_categorical(labels, 10)

print("[INFO] Dataset loaded. Training starting...")

# Model
model = Sequential([
    Conv2D(32, (3,3), activation="relu", input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    MaxPooling2D((2,2)),

    Conv2D(64, (3,3), activation="relu"),
    MaxPooling2D((2,2)),

    Flatten(),
    Dense(128, activation="relu"),
    Dense(10, activation="softmax")
])

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

model.fit(images, labels, epochs=10, batch_size=32)

model.save("gesture_model.h5")
print("[INFO] Model saved as gesture_model.h5")
