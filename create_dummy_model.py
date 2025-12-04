import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force TensorFlow to use CPU
import tensorflow as tf
from tensorflow.keras import layers, models

# Example minimal CNN model for demonstration
model = models.Sequential([
    layers.Input(shape=(224, 224, 1)),
    layers.Conv2D(8, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(16, activation='relu'),
    layers.Dense(10, activation='softmax')  # Example: 10 output classes
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Save the model as model.h5
model.save('model.h5')
print('Dummy model saved as model.h5')
