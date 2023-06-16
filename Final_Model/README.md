# Waste Classification Machine Learning Model

## Overview

This repository contains a machine learning model, model h5, and also model that has been convert to TensorFlow Lite for waste classification using image data. The model is based on transfer learning using the MobileNet V2 architecture.

## Dataset

The dataset used for training and validation consists of a diverse range of waste images, including various types of plastic, iron, wood, organic waste, and Non Recycle waste. The dataset was carefully curated and labeled to ensure accurate classification.
Link for datset : https://drive.google.com/drive/folders/1JV_d9I8TtRz4Kq72Klax60NrzoaQoJE5?usp=sharing

## Model Training

The model was trained using the following configuration:

- Base Model: MobileNet V2
- Training Dataset Accuracy: 95.45%
- Validation Dataset Accuracy: 84.83%

During the training process, the weights of the MobileNet V2 model were frozen, except for the top layers which were fine-tuned to adapt to the waste classification task. The model was trained using the Adam optimizer with a learning rate of 0.001 and a batch size of 32. The training process took approximately 5 hours on a GPU-enabled machine.

## Evaluation

The trained model achieved an accuracy of 95.45% on the training dataset, indicating a strong ability to learn and classify waste images accurately. On the validation dataset, the model achieved an accuracy of 84.83%, demonstrating its effectiveness in generalizing to unseen data.

## Conclusion

The waste classification machine learning model, based on transfer learning with MobileNet V2, demonstrates promising accuracy in classifying various types of waste in images. The model achieved a training dataset accuracy of 95.45% and a validation dataset accuracy of 84.83%. With further improvements and fine-tuning, this model has the potential to be utilized in waste management systems, recycling initiatives, and environmental conservation efforts.
