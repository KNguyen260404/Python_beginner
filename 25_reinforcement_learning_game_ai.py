#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reinforcement Learning Game AI
-----------------------------
A sophisticated AI agent that learns to play games through reinforcement learning.
This project demonstrates advanced AI concepts including:
- Deep Q-Networks (DQN)
- Experience replay
- Target networks
- Policy gradient methods
- Custom game environments
"""

import os
import sys
import time
import random
import argparse
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import pygame
from pygame.locals import *
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tqdm import tqdm

# Ensure TensorFlow uses GPU if available
physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
    print("Using GPU for training")
else:
    print("No GPU found, using CPU for training (this will be slower)")

class GridWorldEnv:
    """A simple grid world environment for reinforcement learning"""
    
    # Action space constants
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    
    # Cell types
    EMPTY = 0
    WALL = 1
    GOAL = 2
    TRAP = 3
    AGENT = 4
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    
    def __init__(self, grid_size=10, render_mode="human"):
        """Initialize the grid world environment
        
        Args:
            grid_size (int): Size of the grid (grid_size x grid_size)
            render_mode (str): Rendering mode ("human" or "rgb_array")
        """
        self.grid_size = grid_size
        self.render_mode = render_mode
        self.action_space = 4  # Up, Right, Down, Left
        self.observation_space = (grid_size, grid_size, 5)  # One-hot encoded grid
        
        # Initialize grid
        self.grid = np.zeros((grid_size, grid_size), dtype=int)
        
        # Initialize pygame if rendering is enabled
        if render_mode == "human":
            pygame.init()
            self.cell_size = 50
            self.screen_size = (grid_size * self.cell_size, grid_size * self.cell_size)
            self.screen = pygame.display.set_mode(self.screen_size)
            pygame.display.set_caption("Grid World Environment")
            self.clock = pygame.time.Clock()
        else:
            self.screen = None
            
        # Reset the environment
        self.reset()
    
    def reset(self):
        """Reset the environment to its initial state
        
        Returns:
            numpy.ndarray: Initial observation
        """
        # Clear the grid
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=int)
        
        # Add walls around the edges
        self.grid[0, :] = self.WALL
        self.grid[-1, :] = self.WALL
        self.grid[:, 0] = self.WALL
        self.grid[:, -1] = self.WALL
        
        # Add some random walls
        num_walls = self.grid_size * 2
        for _ in range(num_walls):
            x = random.randint(1, self.grid_size - 2)
            y = random.randint(1, self.grid_size - 2)
            self.grid[x, y] = self.WALL
        
        # Add goal
        while True:
            x = random.randint(1, self.grid_size - 2)
            y = random.randint(1, self.grid_size - 2)
            if self.grid[x, y] == self.EMPTY:
                self.grid[x, y] = self.GOAL
                self.goal_pos = (x, y)
                break
        
        # Add traps
        num_traps = self.grid_size // 2
        for _ in range(num_traps):
            x = random.randint(1, self.grid_size - 2)
            y = random.randint(1, self.grid_size - 2)
            if self.grid[x, y] == self.EMPTY:
                self.grid[x, y] = self.TRAP
        
        # Place agent
        while True:
            x = random.randint(1, self.grid_size - 2)
            y = random.randint(1, self.grid_size - 2)
            if self.grid[x, y] == self.EMPTY:
                self.agent_pos = (x, y)
                break
        
        # Initialize state
        self.steps = 0
        self.max_steps = self.grid_size * 4
        
        return self._get_observation()
    
    def step(self, action):
        """Take a step in the environment
        
        Args:
            action (int): The action to take (0: Up, 1: Right, 2: Down, 3: Left)
            
        Returns:
            tuple: (observation, reward, done, info)
        """
        assert 0 <= action < 4, f"Invalid action: {action}"
        
        # Current position
        x, y = self.agent_pos
        
        # Calculate new position
        if action == self.UP:
            new_pos = (x - 1, y)
        elif action == self.RIGHT:
            new_pos = (x, y + 1)
        elif action == self.DOWN:
            new_pos = (x + 1, y)
        elif action == self.LEFT:
            new_pos = (x, y - 1)
        
        # Check if the move is valid
        new_x, new_y = new_pos
        if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
            cell_type = self.grid[new_x, new_y]
            
            if cell_type == self.WALL:
                # Hit a wall, don't move
                reward = -0.5
                done = False
            elif cell_type == self.GOAL:
                # Reached the goal
                self.agent_pos = new_pos
                reward = 10.0
                done = True
            elif cell_type == self.TRAP:
                # Fell into a trap
                self.agent_pos = new_pos
                reward = -5.0
                done = True
            else:
                # Empty cell
                self.agent_pos = new_pos
                reward = -0.1  # Small penalty for each step
                done = False
        else:
            # Out of bounds (shouldn't happen with walls around the edges)
            reward = -1.0
            done = False
        
        # Check if maximum steps reached
        self.steps += 1
        if self.steps >= self.max_steps:
            done = True
        
        # Calculate distance-based reward component
        goal_distance = abs(self.agent_pos[0] - self.goal_pos[0]) + abs(self.agent_pos[1] - self.goal_pos[1])
        distance_reward = -0.1 * goal_distance / self.grid_size
        
        # Combine rewards
        reward += distance_reward
        
        return self._get_observation(), reward, done, {"steps": self.steps}
    
    def _get_observation(self):
        """Get the current observation
        
        Returns:
            numpy.ndarray: One-hot encoded grid
        """
        # Create a one-hot encoded representation of the grid
        obs = np.zeros((self.grid_size, self.grid_size, 5), dtype=np.float32)
        
        # Encode each cell type
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                cell_type = self.grid[i, j]
                if cell_type < 4:  # Wall, empty, goal, or trap
                    obs[i, j, cell_type] = 1.0
        
        # Encode agent position
        x, y = self.agent_pos
        obs[x, y, 4] = 1.0
        
        return obs
    
    def render(self):
        """Render the environment"""
        if self.render_mode == "human" and self.screen is not None:
            # Clear the screen
            self.screen.fill(self.BLACK)
            
            # Draw the grid
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    rect = pygame.Rect(
                        j * self.cell_size, 
                        i * self.cell_size, 
                        self.cell_size, 
                        self.cell_size
                    )
                    
                    # Draw cell based on type
                    if self.grid[i, j] == self.EMPTY:
                        pygame.draw.rect(self.screen, self.WHITE, rect)
                    elif self.grid[i, j] == self.WALL:
                        pygame.draw.rect(self.screen, self.BLACK, rect)
                    elif self.grid[i, j] == self.GOAL:
                        pygame.draw.rect(self.screen, self.GREEN, rect)
                    elif self.grid[i, j] == self.TRAP:
                        pygame.draw.rect(self.screen, self.RED, rect)
                    
                    # Draw grid lines
                    pygame.draw.rect(self.screen, self.BLACK, rect, 1)
            
            # Draw agent
            x, y = self.agent_pos
            agent_rect = pygame.Rect(
                y * self.cell_size + self.cell_size // 4, 
                x * self.cell_size + self.cell_size // 4, 
                self.cell_size // 2, 
                self.cell_size // 2
            )
            pygame.draw.rect(self.screen, self.BLUE, agent_rect)
            
            # Update the display
            pygame.display.flip()
            self.clock.tick(10)  # Limit to 10 FPS
            
            # Process events
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
    
    def close(self):
        """Close the environment"""
        if self.render_mode == "human" and pygame.get_init():
            pygame.quit()

class DQNAgent:
    """Deep Q-Network Agent for reinforcement learning"""
    
    def __init__(self, state_shape, action_space, learning_rate=0.001, gamma=0.99, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        """Initialize the DQN agent
        
        Args:
            state_shape (tuple): Shape of the state space
            action_space (int): Number of possible actions
            learning_rate (float): Learning rate for the optimizer
            gamma (float): Discount factor
            epsilon (float): Exploration rate
            epsilon_decay (float): Decay rate for epsilon
            epsilon_min (float): Minimum value for epsilon
        """
        self.state_shape = state_shape
        self.action_space = action_space
        self.learning_rate = learning_rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Experience replay buffer
        self.memory = deque(maxlen=10000)
        
        # Batch size for training
        self.batch_size = 64
        
        # Build the models
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
        
        # Training metrics
        self.loss_history = []
        self.reward_history = []
        self.epsilon_history = []
    
    def _build_model(self):
        """Build a neural network model for Q-value prediction
        
        Returns:
            tf.keras.Model: The Q-network model
        """
        # Input layer
        inputs = layers.Input(shape=self.state_shape)
        
        # Convolutional layers
        x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
        x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
        x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
        
        # Flatten and dense layers
        x = layers.Flatten()(x)
        x = layers.Dense(256, activation='relu')(x)
        x = layers.Dense(128, activation='relu')(x)
        
        # Output layer (Q-values for each action)
        outputs = layers.Dense(self.action_space, activation='linear')(x)
        
        # Create and compile the model
        model = models.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer=optimizers.Adam(learning_rate=self.learning_rate), loss='mse')
        
        return model
    
    def update_target_model(self):
        """Update the target model weights from the main model"""
        self.target_model.set_weights(self.model.get_weights())
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in memory
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether the episode is done
        """
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state, training=True):
        """Choose an action based on the current state
        
        Args:
            state: Current state
            training (bool): Whether the agent is training
            
        Returns:
            int: The chosen action
        """
        if training and np.random.rand() <= self.epsilon:
            # Exploration: choose a random action
            return random.randrange(self.action_space)
        
        # Exploitation: choose the best action based on Q-values
        q_values = self.model.predict(np.expand_dims(state, axis=0), verbose=0)[0]
        return np.argmax(q_values)
    
    def replay(self):
        """Train the model using experience replay
        
        Returns:
            float: Loss value
        """
        if len(self.memory) < self.batch_size:
            return 0
        
        # Sample a batch of experiences from memory
        minibatch = random.sample(self.memory, self.batch_size)
        
        # Extract components from the batch
        states = np.array([experience[0] for experience in minibatch])
        actions = np.array([experience[1] for experience in minibatch])
        rewards = np.array([experience[2] for experience in minibatch])
        next_states = np.array([experience[3] for experience in minibatch])
        dones = np.array([experience[4] for experience in minibatch])
        
        # Predict Q-values for current states
        targets = self.model.predict(states, verbose=0)
        
        # Predict Q-values for next states using target model
        next_q_values = self.target_model.predict(next_states, verbose=0)
        
        # Update target Q-values with the Bellman equation
        for i in range(self.batch_size):
            if dones[i]:
                targets[i, actions[i]] = rewards[i]
            else:
                targets[i, actions[i]] = rewards[i] + self.gamma * np.max(next_q_values[i])
        
        # Train the model
        history = self.model.fit(states, targets, epochs=1, verbose=0, batch_size=self.batch_size)
        loss = history.history['loss'][0]
        self.loss_history.append(loss)
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            self.epsilon_history.append(self.epsilon)
        
        return loss
    
    def load(self, name):
        """Load model weights
        
        Args:
            name (str): Path to the model file
        """
        self.model.load_weights(name)
        self.update_target_model()
    
    def save(self, name):
        """Save model weights
        
        Args:
            name (str): Path to save the model file
        """
        self.model.save_weights(name)
    
    def plot_metrics(self, save_path=None):
        """Plot training metrics
        
        Args:
            save_path (str): Path to save the plot
        """
        plt.figure(figsize=(15, 5))
        
        # Plot loss
        plt.subplot(1, 3, 1)
        plt.plot(self.loss_history)
        plt.title('Model Loss')
        plt.xlabel('Training Steps')
        plt.ylabel('Loss')
        
        # Plot rewards
        plt.subplot(1, 3, 2)
        plt.plot(self.reward_history)
        plt.title('Episode Rewards')
        plt.xlabel('Episodes')
        plt.ylabel('Total Reward')
        
        # Plot epsilon
        plt.subplot(1, 3, 3)
        plt.plot(self.epsilon_history)
        plt.title('Exploration Rate (Epsilon)')
        plt.xlabel('Training Steps')
        plt.ylabel('Epsilon')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        
        plt.show()

class RLTrainer:
    """Trainer class for reinforcement learning agents"""
    
    def __init__(self, env, agent):
        """Initialize the trainer
        
        Args:
            env: The environment
            agent: The RL agent
        """
        self.env = env
        self.agent = agent
        self.best_reward = float('-inf')
        
        # Create directories for saving models and plots
        os.makedirs("rl_models", exist_ok=True)
        os.makedirs("rl_plots", exist_ok=True)
    
    def train(self, episodes=1000, target_update_freq=10, render_freq=100):
        """Train the agent
        
        Args:
            episodes (int): Number of episodes to train
            target_update_freq (int): Frequency of target model updates
            render_freq (int): Frequency of rendering
            
        Returns:
            tuple: (reward_history, loss_history)
        """
        print(f"Starting training for {episodes} episodes...")
        
        for episode in tqdm(range(episodes)):
            # Reset the environment
            state = self.env.reset()
            total_reward = 0
            done = False
            step = 0
            
            while not done:
                # Render occasionally
                if episode % render_freq == 0:
                    self.env.render()
                
                # Choose and take an action
                action = self.agent.act(state)
                next_state, reward, done, _ = self.env.step(action)
                
                # Store the experience
                self.agent.remember(state, action, reward, next_state, done)
                
                # Move to the next state
                state = next_state
                total_reward += reward
                step += 1
                
                # Train the agent
                self.agent.replay()
            
            # Update target model periodically
            if episode % target_update_freq == 0:
                self.agent.update_target_model()
            
            # Store the episode reward
            self.agent.reward_history.append(total_reward)
            
            # Print progress
            if episode % 10 == 0:
                avg_reward = np.mean(self.agent.reward_history[-10:])
                print(f"Episode: {episode}, Reward: {total_reward:.2f}, Avg Reward: {avg_reward:.2f}, Epsilon: {self.agent.epsilon:.4f}")
            
            # Save the best model
            if total_reward > self.best_reward:
                self.best_reward = total_reward
                self.agent.save("rl_models/best_model.h5")
                print(f"New best model saved with reward: {total_reward:.2f}")
            
            # Save intermediate models
            if episode % 100 == 0 and episode > 0:
                self.agent.save(f"rl_models/model_episode_{episode}.h5")
                self.agent.plot_metrics(f"rl_plots/metrics_episode_{episode}.png")
        
        print("Training completed!")
        
        # Save the final model
        self.agent.save("rl_models/final_model.h5")
        
        # Plot and save the final metrics
        self.agent.plot_metrics("rl_plots/final_metrics.png")
        
        return self.agent.reward_history, self.agent.loss_history
    
    def test(self, model_path="rl_models/best_model.h5", episodes=10, render=True):
        """Test a trained agent
        
        Args:
            model_path (str): Path to the model file
            episodes (int): Number of episodes to test
            render (bool): Whether to render the environment
            
        Returns:
            list: Rewards for each episode
        """
        # Load the model
        self.agent.load(model_path)
        self.agent.epsilon = 0.0  # No exploration during testing
        
        rewards = []
        
        print(f"Testing agent for {episodes} episodes...")
        
        for episode in range(episodes):
            state = self.env.reset()
            total_reward = 0
            done = False
            step = 0
            
            while not done:
                if render:
                    self.env.render()
                    time.sleep(0.1)  # Slow down rendering for visibility
                
                action = self.agent.act(state, training=False)
                next_state, reward, done, _ = self.env.step(action)
                
                state = next_state
                total_reward += reward
                step += 1
            
            rewards.append(total_reward)
            print(f"Episode: {episode}, Reward: {total_reward:.2f}, Steps: {step}")
        
        print(f"Average reward over {episodes} episodes: {np.mean(rewards):.2f}")
        
        return rewards

class RLApplication:
    """Application class for the Reinforcement Learning Game AI"""
    
    def __init__(self):
        """Initialize the application"""
        self.parse_arguments()
        
        # Create the environment and agent
        self.env = None
        self.agent = None
        self.trainer = None
    
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(description='Reinforcement Learning Game AI')
        
        # Main operation modes
        parser.add_argument('--train', action='store_true', help='Train the RL agent')
        parser.add_argument('--test', action='store_true', help='Test a trained agent')
        parser.add_argument('--play', action='store_true', help='Play the game manually')
        
        # Training parameters
        parser.add_argument('--episodes', type=int, default=1000, help='Number of episodes for training')
        parser.add_argument('--grid-size', type=int, default=10, help='Size of the grid world')
        parser.add_argument('--render-freq', type=int, default=100, help='Frequency of rendering during training')
        
        # Testing parameters
        parser.add_argument('--model', type=str, default='rl_models/best_model.h5', help='Path to the trained model')
        parser.add_argument('--test-episodes', type=int, default=10, help='Number of episodes for testing')
        
        self.args = parser.parse_args()
    
    def setup(self):
        """Set up the environment and agent"""
        # Create the environment
        render_mode = "human" if self.args.test or self.args.play else "human"
        self.env = GridWorldEnv(grid_size=self.args.grid_size, render_mode=render_mode)
        
        # Create the agent
        state_shape = self.env.observation_space
        action_space = self.env.action_space
        self.agent = DQNAgent(state_shape, action_space)
        
        # Create the trainer
        self.trainer = RLTrainer(self.env, self.agent)
    
    def run(self):
        """Run the application based on command line arguments"""
        self.setup()
        
        if self.args.train:
            # Train the agent
            self.trainer.train(
                episodes=self.args.episodes,
                render_freq=self.args.render_freq
            )
        
        elif self.args.test:
            # Test the agent
            self.trainer.test(
                model_path=self.args.model,
                episodes=self.args.test_episodes
            )
        
        elif self.args.play:
            # Play the game manually
            self.play_manually()
        
        else:
            # If no operation specified, show interactive menu
            self.show_menu()
    
    def play_manually(self):
        """Play the game manually using keyboard controls"""
        print("Playing the game manually...")
        print("Controls: Arrow keys to move, Q to quit")
        
        state = self.env.reset()
        self.env.render()
        
        done = False
        total_reward = 0
        
        while not done:
            action = None
            
            # Wait for a valid key press
            while action is None:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        return
                    elif event.type == KEYDOWN:
                        if event.key == K_UP:
                            action = self.env.UP
                        elif event.key == K_RIGHT:
                            action = self.env.RIGHT
                        elif event.key == K_DOWN:
                            action = self.env.DOWN
                        elif event.key == K_LEFT:
                            action = self.env.LEFT
                        elif event.key == K_q:
                            pygame.quit()
                            return
            
            # Take the action
            next_state, reward, done, _ = self.env.step(action)
            state = next_state
            total_reward += reward
            
            # Render the environment
            self.env.render()
            
            # Print information
            print(f"Action: {action}, Reward: {reward:.2f}, Total Reward: {total_reward:.2f}")
        
        print(f"Game over! Total reward: {total_reward:.2f}")
        time.sleep(2)  # Pause to see the final state
    
    def show_menu(self):
        """Show an interactive menu for the application"""
        while True:
            print("\n===== Reinforcement Learning Game AI =====")
            print("1. Train a new agent")
            print("2. Test a trained agent")
            print("3. Play manually")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                episodes = int(input("Enter the number of training episodes (default 1000): ") or "1000")
                grid_size = int(input("Enter the grid size (default 10): ") or "10")
                render_freq = int(input("Enter the rendering frequency (default 100): ") or "100")
                
                # Recreate environment and agent with new parameters
                self.env = GridWorldEnv(grid_size=grid_size, render_mode="human")
                self.agent = DQNAgent(self.env.observation_space, self.env.action_space)
                self.trainer = RLTrainer(self.env, self.agent)
                
                self.trainer.train(
                    episodes=episodes,
                    render_freq=render_freq
                )
            
            elif choice == '2':
                model_path = input("Enter the path to the trained model (default 'rl_models/best_model.h5'): ") or "rl_models/best_model.h5"
                episodes = int(input("Enter the number of test episodes (default 10): ") or "10")
                
                self.trainer.test(
                    model_path=model_path,
                    episodes=episodes
                )
            
            elif choice == '3':
                self.play_manually()
            
            elif choice == '4':
                print("Exiting the application...")
                break
            
            else:
                print("Invalid choice. Please try again.")

def main():
    """Main entry point for the application"""
    # Print welcome message
    print("=" * 60)
    print("Reinforcement Learning Game AI".center(60))
    print("A deep Q-learning based game AI system".center(60))
    print("=" * 60)
    
    # Create and run the application
    app = RLApplication()
    app.run()

if __name__ == "__main__":
    main() 