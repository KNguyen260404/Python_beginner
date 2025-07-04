# Neural Network Image Generator

A sophisticated Python application that uses Generative Adversarial Networks (GANs) to create new images based on a training dataset.

## Features

- **GAN Architecture**: Implements a deep convolutional GAN (DCGAN) with generator and discriminator networks
- **Training Pipeline**: Complete training workflow with progress tracking and visualization
- **Image Generation**: Generate new, unique images from random noise after training
- **Model Management**: Save and load trained models for later use
- **Interactive Interface**: Both command-line arguments and interactive menu options

## Requirements

- Python 3.7+
- TensorFlow 2.x
- NumPy
- Matplotlib
- Pillow (PIL)
- tqdm

## Installation

1. Install the required packages:

```bash
pip install -r requirements_neural_network.txt
```

2. Prepare your dataset:
   - Create a directory structure with images in subdirectories
   - For best results, use images of consistent size and style

## Usage

### Command Line Interface

**Training a new model:**

```bash
python 24_neural_network_image_generator.py --train --dataset path/to/dataset --epochs 10000
```

**Generating images with a trained model:**

```bash
python 24_neural_network_image_generator.py --generate --model path/to/model.h5 --num-images 20
```

### Interactive Menu

Run the script without arguments to use the interactive menu:

```bash
python 24_neural_network_image_generator.py
```

## How GANs Work

Generative Adversarial Networks consist of two neural networks that work against each other:

1. **Generator**: Creates images from random noise, trying to make them look real
2. **Discriminator**: Tries to distinguish between real images and generated fakes

Through this adversarial process, the generator learns to create increasingly realistic images.

## Training Tips

- Use a GPU for significantly faster training
- Start with a smaller image size (64x64) before attempting larger resolutions
- Training GANs can be unstable - if results deteriorate, try loading from an earlier checkpoint
- For best results, use a dataset with at least several hundred images

## Project Structure

- `GANImageGenerator`: Core class implementing the GAN model and training logic
- `GANApplication`: User interface handling command-line arguments and interactive menu
- Training produces:
  - Sample images saved to `gan_images/` at regular intervals
  - Model checkpoints saved to `gan_models/`
  - Training history plots

## Advanced Usage

### Model Parameters

Fine-tune your GAN with these parameters:

```bash
python 24_neural_network_image_generator.py --train --image-size 128 --latent-dim 200
```

### Custom Save Intervals

Control how often samples and models are saved:

```bash
python 24_neural_network_image_generator.py --train --save-interval 500
```

## Troubleshooting

- **"No GPU found"**: The script will run on CPU but will be much slower
- **Memory errors**: Reduce batch size or image dimensions
- **Mode collapse**: If all generated images look similar, try adjusting learning rates or model architecture
- **Training instability**: GANs can be difficult to train - try different hyperparameters

## License

This project is open source and available under the MIT License. 