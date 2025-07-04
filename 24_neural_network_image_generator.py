#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Neural Network Image Generator
-----------------------------
A GAN-based image generator that creates new images based on a training set.
This project demonstrates advanced deep learning concepts including:
- Generative Adversarial Networks (GANs)
- Convolutional Neural Networks
- Image processing and generation
- Training deep learning models
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import time
from tqdm import tqdm
import argparse
import random
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import plot_model
from PIL import Image

# Ensure TensorFlow uses GPU if available
physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
    print("Using GPU for training")
else:
    print("No GPU found, using CPU for training (this will be slow)")

class GANImageGenerator:
    """Main class for the GAN Image Generator application"""
    
    def __init__(self, image_size=64, latent_dim=100, channels=3):
        """Initialize the GAN model architecture
        
        Args:
            image_size (int): Size of the generated images (square)
            latent_dim (int): Dimension of the latent space
            channels (int): Number of color channels (3 for RGB)
        """
        self.image_size = image_size
        self.latent_dim = latent_dim
        self.channels = channels
        self.img_shape = (image_size, image_size, channels)
        
        # Build and compile the discriminator
        self.discriminator = self._build_discriminator()
        self.discriminator.compile(
            loss='binary_crossentropy',
            optimizer=optimizers.Adam(learning_rate=0.0002, beta_1=0.5),
            metrics=['accuracy']
        )
        
        # Build the generator
        self.generator = self._build_generator()
        
        # For the combined model, we only train the generator
        self.discriminator.trainable = False
        
        # The combined model takes noise as input and generates images
        z = layers.Input(shape=(self.latent_dim,))
        img = self.generator(z)
        
        # The discriminator determines validity of generated images
        valid = self.discriminator(img)
        
        # The combined model (stacked generator and discriminator)
        self.combined = models.Model(z, valid)
        self.combined.compile(
            loss='binary_crossentropy',
            optimizer=optimizers.Adam(learning_rate=0.0002, beta_1=0.5)
        )
        
        # Create directories for saving results
        os.makedirs("gan_images", exist_ok=True)
        os.makedirs("gan_models", exist_ok=True)
        
        self.training_history = {
            'd_loss': [],
            'g_loss': [],
            'd_accuracy': []
        }
    
    def _build_generator(self):
        """Build the generator network
        
        Returns:
            tf.keras.Model: The generator model
        """
        model = models.Sequential(name="Generator")
        
        # Starting size is image_size/4
        starting_size = self.image_size // 4
        
        # Foundation for 16x16 feature maps
        model.add(layers.Dense(128 * starting_size * starting_size, 
                              input_dim=self.latent_dim, 
                              name="gen_dense_1"))
        model.add(layers.LeakyReLU(alpha=0.2, name="gen_leaky_1"))
        model.add(layers.Reshape((starting_size, starting_size, 128), 
                                name="gen_reshape"))
        
        # Upsample to 32x32
        model.add(layers.Conv2DTranspose(128, kernel_size=4, strides=2, 
                                        padding='same', name="gen_conv_t_1"))
        model.add(layers.LeakyReLU(alpha=0.2, name="gen_leaky_2"))
        model.add(layers.BatchNormalization(momentum=0.8, name="gen_bn_1"))
        
        # Upsample to 64x64
        model.add(layers.Conv2DTranspose(64, kernel_size=4, strides=2, 
                                        padding='same', name="gen_conv_t_2"))
        model.add(layers.LeakyReLU(alpha=0.2, name="gen_leaky_3"))
        model.add(layers.BatchNormalization(momentum=0.8, name="gen_bn_2"))
        
        # Final layer with tanh activation for pixel values in [-1, 1]
        model.add(layers.Conv2D(self.channels, kernel_size=3, padding='same', 
                               activation='tanh', name="gen_conv_final"))
        
        print("Generator Summary:")
        model.summary()
        
        noise = layers.Input(shape=(self.latent_dim,), name="gen_input")
        img = model(noise)
        
        return models.Model(noise, img)
    
    def _build_discriminator(self):
        """Build the discriminator network
        
        Returns:
            tf.keras.Model: The discriminator model
        """
        model = models.Sequential(name="Discriminator")
        
        # First convolutional layer
        model.add(layers.Conv2D(32, kernel_size=3, strides=2, padding='same',
                               input_shape=self.img_shape, name="disc_conv_1"))
        model.add(layers.LeakyReLU(alpha=0.2, name="disc_leaky_1"))
        model.add(layers.Dropout(0.25, name="disc_dropout_1"))
        
        # Second convolutional layer
        model.add(layers.Conv2D(64, kernel_size=3, strides=2, padding='same', 
                               name="disc_conv_2"))
        model.add(layers.ZeroPadding2D(padding=((0, 1), (0, 1)), name="disc_zero_pad_1"))
        model.add(layers.LeakyReLU(alpha=0.2, name="disc_leaky_2"))
        model.add(layers.Dropout(0.25, name="disc_dropout_2"))
        model.add(layers.BatchNormalization(momentum=0.8, name="disc_bn_1"))
        
        # Third convolutional layer
        model.add(layers.Conv2D(128, kernel_size=3, strides=2, padding='same', 
                               name="disc_conv_3"))
        model.add(layers.LeakyReLU(alpha=0.2, name="disc_leaky_3"))
        model.add(layers.Dropout(0.25, name="disc_dropout_3"))
        model.add(layers.BatchNormalization(momentum=0.8, name="disc_bn_2"))
        
        # Fourth convolutional layer
        model.add(layers.Conv2D(256, kernel_size=3, strides=1, padding='same', 
                               name="disc_conv_4"))
        model.add(layers.LeakyReLU(alpha=0.2, name="disc_leaky_4"))
        model.add(layers.Dropout(0.25, name="disc_dropout_4"))
        
        # Flatten and output layer
        model.add(layers.Flatten(name="disc_flatten"))
        model.add(layers.Dense(1, activation='sigmoid', name="disc_output"))
        
        print("Discriminator Summary:")
        model.summary()
        
        img = layers.Input(shape=self.img_shape, name="disc_input")
        validity = model(img)
        
        return models.Model(img, validity)
    
    def train(self, dataset_path, epochs=20000, batch_size=32, save_interval=1000):
        """Train the GAN model
        
        Args:
            dataset_path (str): Path to the training images
            epochs (int): Number of training epochs
            batch_size (int): Batch size for training
            save_interval (int): Interval for saving sample images
        """
        # Load and preprocess the dataset
        print(f"Loading dataset from {dataset_path}")
        
        # Data generator with augmentation
        datagen = ImageDataGenerator(
            rescale=1./127.5 - 1,  # Scale to [-1, 1]
            rotation_range=5,
            width_shift_range=0.05,
            height_shift_range=0.05,
            zoom_range=0.05,
            horizontal_flip=True
        )
        
        # Flow from directory
        try:
            data_generator = datagen.flow_from_directory(
                dataset_path,
                target_size=(self.image_size, self.image_size),
                batch_size=batch_size,
                class_mode=None  # Only images, no labels
            )
        except Exception as e:
            print(f"Error loading dataset: {e}")
            print("Make sure the dataset directory contains images in a subdirectory")
            return
        
        # Labels for real and fake images
        real = np.ones((batch_size, 1))
        fake = np.zeros((batch_size, 1))
        
        print("Starting GAN training...")
        start_time = time.time()
        
        try:
            for epoch in range(1, epochs + 1):
                # ---------------------
                #  Train Discriminator
                # ---------------------
                
                # Select a random batch of real images
                real_images = next(data_generator)
                
                # Generate a batch of fake images
                noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
                gen_images = self.generator.predict(noise, verbose=0)
                
                # Train the discriminator
                d_loss_real = self.discriminator.train_on_batch(real_images, real)
                d_loss_fake = self.discriminator.train_on_batch(gen_images, fake)
                d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
                
                # ---------------------
                #  Train Generator
                # ---------------------
                
                # Train the generator (wants discriminator to mistake images as real)
                noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
                g_loss = self.combined.train_on_batch(noise, real)
                
                # Store loss and accuracy values
                self.training_history['d_loss'].append(d_loss[0])
                self.training_history['d_accuracy'].append(d_loss[1])
                self.training_history['g_loss'].append(g_loss)
                
                # Print progress
                if epoch % 100 == 0:
                    elapsed_time = time.time() - start_time
                    print(f"[Epoch {epoch}/{epochs}] [D loss: {d_loss[0]:.4f}, acc: {100*d_loss[1]:.2f}%] [G loss: {g_loss:.4f}] [Time: {elapsed_time:.2f}s]")
                
                # Save generated images at intervals
                if epoch % save_interval == 0:
                    self.save_images(epoch)
                    self.save_models(epoch)
                    self.plot_training_history()
        
        except KeyboardInterrupt:
            print("Training interrupted by user")
        
        print("Training completed!")
        self.save_models(epochs)
        self.plot_training_history()
    
    def save_images(self, epoch):
        """Save a grid of generated images
        
        Args:
            epoch (int): Current training epoch
        """
        r, c = 4, 4  # Grid size
        noise = np.random.normal(0, 1, (r * c, self.latent_dim))
        gen_imgs = self.generator.predict(noise, verbose=0)
        
        # Rescale images from [-1, 1] to [0, 1]
        gen_imgs = 0.5 * gen_imgs + 0.5
        
        fig, axs = plt.subplots(r, c, figsize=(12, 12))
        cnt = 0
        for i in range(r):
            for j in range(c):
                axs[i, j].imshow(gen_imgs[cnt])
                axs[i, j].axis('off')
                cnt += 1
        
        fig.suptitle(f"Generated Images - Epoch {epoch}", fontsize=16)
        fig.savefig(f"gan_images/epoch_{epoch}.png")
        plt.close()
    
    def save_models(self, epoch):
        """Save the generator and discriminator models
        
        Args:
            epoch (int): Current training epoch
        """
        self.generator.save(f"gan_models/generator_epoch_{epoch}.h5")
        self.discriminator.save(f"gan_models/discriminator_epoch_{epoch}.h5")
    
    def plot_training_history(self):
        """Plot and save the training history"""
        plt.figure(figsize=(12, 5))
        
        # Plot discriminator loss
        plt.subplot(1, 2, 1)
        plt.plot(self.training_history['d_loss'], label='D loss')
        plt.plot(self.training_history['g_loss'], label='G loss')
        plt.title('GAN Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        # Plot discriminator accuracy
        plt.subplot(1, 2, 2)
        plt.plot(self.training_history['d_accuracy'], label='D accuracy')
        plt.title('Discriminator Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig("gan_images/training_history.png")
        plt.close()
    
    def generate_images(self, num_images=10, output_dir="generated_images"):
        """Generate and save a specified number of images
        
        Args:
            num_images (int): Number of images to generate
            output_dir (str): Directory to save the generated images
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Generating {num_images} images...")
        noise = np.random.normal(0, 1, (num_images, self.latent_dim))
        gen_imgs = self.generator.predict(noise, verbose=0)
        
        # Rescale images from [-1, 1] to [0, 1]
        gen_imgs = 0.5 * gen_imgs + 0.5
        gen_imgs = np.clip(gen_imgs, 0, 1)
        
        for i, img in enumerate(gen_imgs):
            img_array = (img * 255).astype(np.uint8)
            img_pil = Image.fromarray(img_array)
            img_pil.save(f"{output_dir}/generated_{i+1}.png")
        
        print(f"Images saved to {output_dir}/")
    
    def load_model(self, generator_path):
        """Load a pre-trained generator model
        
        Args:
            generator_path (str): Path to the saved generator model
        """
        try:
            self.generator = models.load_model(generator_path)
            print(f"Generator model loaded from {generator_path}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

class GANApplication:
    """Application class for the GAN Image Generator"""
    
    def __init__(self):
        """Initialize the application"""
        self.gan = None
        self.parse_arguments()
    
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(description='Neural Network Image Generator')
        
        # Main operation modes
        parser.add_argument('--train', action='store_true', help='Train the GAN model')
        parser.add_argument('--generate', action='store_true', help='Generate images using a trained model')
        
        # Training parameters
        parser.add_argument('--dataset', type=str, default='dataset', help='Path to the training dataset')
        parser.add_argument('--epochs', type=int, default=20000, help='Number of training epochs')
        parser.add_argument('--batch-size', type=int, default=32, help='Batch size for training')
        parser.add_argument('--save-interval', type=int, default=1000, help='Interval for saving sample images')
        
        # Generation parameters
        parser.add_argument('--model', type=str, help='Path to a trained generator model')
        parser.add_argument('--num-images', type=int, default=10, help='Number of images to generate')
        parser.add_argument('--output-dir', type=str, default='generated_images', help='Directory to save generated images')
        
        # Model parameters
        parser.add_argument('--image-size', type=int, default=64, help='Size of the generated images')
        parser.add_argument('--latent-dim', type=int, default=100, help='Dimension of the latent space')
        
        self.args = parser.parse_args()
    
    def run(self):
        """Run the application based on command line arguments"""
        # Initialize the GAN model
        self.gan = GANImageGenerator(
            image_size=self.args.image_size,
            latent_dim=self.args.latent_dim
        )
        
        if self.args.train:
            # Train the GAN model
            self.gan.train(
                dataset_path=self.args.dataset,
                epochs=self.args.epochs,
                batch_size=self.args.batch_size,
                save_interval=self.args.save_interval
            )
        
        elif self.args.generate:
            if self.args.model:
                # Load the model and generate images
                if self.gan.load_model(self.args.model):
                    self.gan.generate_images(
                        num_images=self.args.num_images,
                        output_dir=self.args.output_dir
                    )
            else:
                print("Error: Please provide a trained model path using --model")
        
        else:
            # If no operation specified, show interactive menu
            self.show_menu()
    
    def show_menu(self):
        """Show an interactive menu for the application"""
        while True:
            print("\n===== Neural Network Image Generator =====")
            print("1. Train a new GAN model")
            print("2. Generate images from a trained model")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == '1':
                dataset_path = input("Enter the path to your training dataset: ")
                epochs = int(input("Enter the number of training epochs (default 20000): ") or "20000")
                batch_size = int(input("Enter the batch size (default 32): ") or "32")
                save_interval = int(input("Enter the save interval (default 1000): ") or "1000")
                
                self.gan.train(
                    dataset_path=dataset_path,
                    epochs=epochs,
                    batch_size=batch_size,
                    save_interval=save_interval
                )
            
            elif choice == '2':
                model_path = input("Enter the path to the trained generator model: ")
                num_images = int(input("Enter the number of images to generate (default 10): ") or "10")
                output_dir = input("Enter the output directory (default 'generated_images'): ") or "generated_images"
                
                if self.gan.load_model(model_path):
                    self.gan.generate_images(
                        num_images=num_images,
                        output_dir=output_dir
                    )
            
            elif choice == '3':
                print("Exiting the application...")
                break
            
            else:
                print("Invalid choice. Please try again.")

def main():
    """Main entry point for the application"""
    # Print welcome message
    print("=" * 60)
    print("Neural Network Image Generator".center(60))
    print("A GAN-based image generation system".center(60))
    print("=" * 60)
    
    # Create and run the application
    app = GANApplication()
    app.run()

if __name__ == "__main__":
    main() 