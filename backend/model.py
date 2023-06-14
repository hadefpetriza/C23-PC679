# Importing required libs
from keras.models import load_model
from keras.utils import img_to_array
import numpy as np
from PIL import Image
import tensorflow as tf



# Loading model
interpreter = tf.lite.Interpreter(model_path="model_classification.tflite")
interpreter.allocate_tensors()

# Preparing and pre-processing the image
def preprocess_img(img_path):
    op_img = Image.open(img_path)
    img_resize = op_img.resize((224, 224))
    img2arr = np.array(img_resize, dtype=np.float32) / 255.0
    img_reshape = np.expand_dims(img2arr, axis=0)
    return img_reshape



# Predicting function
def predict_result(predict):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], predict)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    predicted_class = np.argmax(output_data[0], axis=-1)
    return predicted_class

