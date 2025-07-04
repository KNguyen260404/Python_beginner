# Reinforcement Learning Game AI

An advanced Python application that implements reinforcement learning algorithms to train an AI agent to play grid-based games.

## Features

- **Deep Q-Network (DQN)**: Implementation of modern deep reinforcement learning
- **Custom Grid World Environment**: Configurable game environment with goals, traps, and obstacles
- **Experience Replay**: Efficient learning through stored experiences
- **Target Networks**: Stable training with separate target Q-network
- **Visualization**: Real-time game rendering and training metrics
- **Interactive Interface**: Play the game yourself or watch the trained AI

## Requirements

- Python 3.7+
- TensorFlow 2.x
- NumPy
- Matplotlib
- Pygame
- tqdm

## Installation

1. Install the required packages:

```bash
pip install -r requirements_reinforcement_learning.txt
```

## Usage

### Command Line Interface

**Training a new agent:**

```bash
python 25_reinforcement_learning_game_ai.py --train --episodes 2000 --grid-size 10
```

**Testing a trained agent:**

```bash
python 25_reinforcement_learning_game_ai.py --test --model rl_models/best_model.h5
```

**Playing the game manually:**

```bash
python 25_reinforcement_learning_game_ai.py --play
```

### Interactive Menu

Run the script without arguments to use the interactive menu:

```bash
python 25_reinforcement_learning_game_ai.py
```

## How Reinforcement Learning Works

The agent learns through trial and error by interacting with the environment:

1. **State**: The agent observes the current state of the environment
2. **Action**: The agent selects an action based on its policy
3. **Reward**: The environment provides a reward signal
4. **Next State**: The environment transitions to a new state
5. **Learning**: The agent updates its policy to maximize future rewards

## Deep Q-Network (DQN)

This project uses DQN, which combines Q-learning with deep neural networks:

- Neural network approximates the Q-value function
- Experience replay buffer stores and reuses past experiences
- Target network stabilizes training
- Epsilon-greedy exploration balances exploration and exploitation

## Grid World Environment

The custom environment features:

- Configurable grid size
- Walls and obstacles
- Goal states with positive rewards
- Trap states with negative rewards
- Distance-based reward shaping

## Training Tips

- Larger grid sizes require more training episodes
- Monitor the average reward to track learning progress
- If training is unstable, try adjusting the learning rate or discount factor
- Save and test models periodically during training

## Project Structure

- `GridWorldEnv`: Custom environment implementing the grid world game
- `DQNAgent`: Implementation of the Deep Q-Network algorithm
- `RLTrainer`: Training and evaluation utilities
- `RLApplication`: User interface and application logic

## Advanced Usage

### Customizing the Environment

Modify grid size and complexity:

```bash
python 25_reinforcement_learning_game_ai.py --train --grid-size 15
```

### Adjusting Training Parameters

Fine-tune the training process:

```bash
python 25_reinforcement_learning_game_ai.py --train --episodes 5000 --render-freq 500
```

## Troubleshooting

- **"No GPU found"**: The script will run on CPU but will be much slower
- **Slow training**: Reduce rendering frequency or disable rendering during training
- **Poor performance**: Try increasing the number of training episodes
- **Game window not responding**: Make sure Pygame is properly installed

## License

This project is open source and available under the MIT License. 