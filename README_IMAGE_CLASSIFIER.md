# Image Classifier

An advanced image classification application that uses deep learning to identify objects in images. Built with Python, TensorFlow, and Tkinter.

## Features

- **Image Classification**: Identify objects in images using a pre-trained deep learning model
- **Top Predictions**: View the top 5 most likely classifications with confidence scores
- **Prediction History**: Keep track of previously classified images
- **Save Results**: Export classification results to text files
- **User-friendly Interface**: Clean and intuitive graphical interface

## Screenshots

(Screenshots would be added here)

## Requirements

- Python 3.6 or higher
- TensorFlow 2.x
- Pillow (PIL Fork)
- NumPy
- Tkinter (usually comes with Python)

## Installation

```bash
# Install required packages
pip install tensorflow pillow numpy
```

## How to Run

```bash
python 20_image_classifier.py
```

## Usage Guide

1. **Loading the Model**:
   - The application automatically loads the MobileNetV2 model on startup
   - Wait for the "Model loaded" status message before proceeding

2. **Classifying Images**:
   - Click "Open Image" to select an image file
   - Click "Classify Image" to analyze the image
   - View the top predictions in the right panel

3. **Working with Results**:
   - Save current results to a text file using the "Save Results" button
   - View previous classifications in the history list
   - Click on a history item to reload that image and its predictions

## About the Model

This application uses MobileNetV2, a lightweight convolutional neural network designed for mobile and embedded vision applications. The model is pre-trained on the ImageNet dataset, which contains over a million images across 1,000 categories.

## Technical Details

- **Model**: MobileNetV2 (pre-trained on ImageNet)
- **Input Size**: 224x224 pixels
- **Classes**: 1,000 ImageNet categories
- **Prediction Format**: Class label and confidence score (0-100%)

## Limitations

- The model can only recognize objects it was trained on (ImageNet classes)
- Classification accuracy depends on image quality and clarity
- Processing large images may take longer

## Future Improvements

- Support for custom models
- Batch processing of multiple images
- Object detection with bounding boxes
- Camera integration for real-time classification
- Export results in different formats (CSV, JSON) 