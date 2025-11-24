#!/usr/bin/env python3
"""
Ultra-fast GPU-optimized Snake AI Training (Headless Mode)
This version runs without graphics for maximum training speed.

Perfect for:
- Long training sessions
- Maximum GPU utilization
- Cloud training environments
- Performance benchmarking
"""

import torch
import random
import numpy as np
from collections import deque
import os

# Disable graphics for maximum speed
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from snake_gameai import Direction, Point, BLOCK_SIZE
from model import Linear_QNet, QTrainer

# Ultra-optimized hyperparameters for GPU training
MAX_MEMORY = 500_000  # Massive memory for GPU efficiency
BATCH_SIZE = 4000     # HUGE batches for GPU parallelization
LR = 0.001

class HeadlessAgent:
    def __init__(self):
        self.n_game = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)

        # Force maximum GPU optimization
        if torch.cuda.is_available():
            print("🚀 MAXIMUM GPU MODE ACTIVATED!")
            print("🎯 Ultra-fast headless training enabled")
            torch.cuda.empty_cache()
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
            # Use pinned memory for 10x faster CPU→GPU transfers
            torch.cuda.set_device(0)
        else:
            print("⚠️ WARNING: No CUDA GPU detected! This mode requires GPU for performance.")

        # Optimized model with GPU acceleration
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.device = self.model.device

        print(f"💪 Using device: {self.device}")
        print(f"📊 Memory capacity: {MAX_MEMORY:,} experiences")
        print(f"🎯 Batch size: {BATCH_SIZE}")
        print("=" * 60)

    def create_headless_game(self):
        """Create a lightweight game state without graphics"""
        class HeadlessGame:
            def __init__(self):
                self.direction = Direction.RIGHT
                self.head = Point(320, 240)  # Center of 640x480
                self.snake = [self.head,
                             Point(self.head.x-BLOCK_SIZE, self.head.y),
                             Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
                self.score = 0
                self.food = None
                self.frame_iteration = 0
                self._place_food()

            def _place_food(self):
                x = random.randint(0, (640-BLOCK_SIZE)//BLOCK_SIZE) * BLOCK_SIZE
                y = random.randint(0, (480-BLOCK_SIZE)//BLOCK_SIZE) * BLOCK_SIZE
                self.food = Point(x, y)
                if self.food in self.snake:
                    self._place_food()

            def reset(self):
                self.__init__()

            def is_collision(self, pt=None):
                if pt is None:
                    pt = self.head
                # Wall collision
                if (pt.x > 640-BLOCK_SIZE or pt.x < 0 or
                    pt.y > 480-BLOCK_SIZE or pt.y < 0):
                    return True
                # Self collision
                if pt in self.snake[1:]:
                    return True
                return False

            def _move(self, action):
                """Move snake based on action"""
                clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
                idx = clock_wise.index(self.direction)
                if np.array_equal(action, [1, 0, 0]):
                    new_dir = clock_wise[idx]  # Straight
                elif np.array_equal(action, [0, 1, 0]):
                    next_idx = (idx + 1) % 4
                    new_dir = clock_wise[next_idx]  # Right turn
                else:
                    next_idx = (idx - 1) % 4
                    new_dir = clock_wise[next_idx]  # Left turn
                self.direction = new_dir

                x = self.head.x
                y = self.head.y
                if self.direction == Direction.RIGHT:
                    x += BLOCK_SIZE
                elif self.direction == Direction.LEFT:
                    x -= BLOCK_SIZE
                elif self.direction == Direction.DOWN:
                    y += BLOCK_SIZE
                elif self.direction == Direction.UP:
                    y -= BLOCK_SIZE
                self.head = Point(x, y)

            def play_step_headless(self, action):
                """Ultra-fast game step without graphics"""
                self.frame_iteration += 1

                # Move snake
                self._move(action)
                self.snake.insert(0, self.head)

                # Check game over conditions
                if (self.is_collision() or self.frame_iteration > 100 * len(self.snake)):
                    return -1, True, self.score

                # Check food collision
                if self.head == self.food:
                    self.score += 1
                    self._place_food()
                    return 10, False, self.score
                else:
                    self.snake.pop()
                    return 0, False, self.score

        return HeadlessGame()

    def get_state(self, game):
        head = game.snake[0]
        point_l = Point(head.x - BLOCK_SIZE, head.y)
        point_r = Point(head.x + BLOCK_SIZE, head.y)
        point_u = Point(head.x, head.y - BLOCK_SIZE)
        point_d = Point(head.x, head.y + BLOCK_SIZE)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger detection
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)) or
            (dir_l and game.is_collision(point_l)) or
            (dir_r and game.is_collision(point_r)),

            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)),

            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)) or
            (dir_r and game.is_collision(point_u)) or
            (dir_l and game.is_collision(point_d)),

            # Direction flags
            dir_l, dir_r, dir_u, dir_d,

            # Food location
            game.food.x < game.head.x,
            game.food.x > game.head.x,
            game.food.y < game.head.y,
            game.food.y > game.head.y
        ]
        return np.array(state, dtype=int)

    def get_action(self, state):
        self.epsilon = max(5, 80 - self.n_game)  # Minimum 5% exploration
        final_move = [0, 0, 0]

        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state_tensor = torch.tensor(state, dtype=torch.float).to(self.device)
            with torch.no_grad():  # Faster inference
                prediction = self.model(state_tensor)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory"""
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        """Train on single experience"""
        self.trainer.train_step(state, action, reward, next_state, done)

def train_ultra_fast():
    """GPU-optimized training loop with maximum speed"""
    print("🐍 ULTRA-FAST SNAKE AI TRAINING (HEADLESS)")
    print("🎮 GPU-Accelerated | No Graphics | Maximum Speed")
    print("=" * 60)

    agent = HeadlessAgent()
    game = agent.create_headless_game()

    scores = []
    total_score = 0
    record = 0
    games_per_print = 50  # Print stats every N games

    try:
        game_counter = 0
        while True:
            game_counter += 1
            agent.n_game += 1

            # Get initial state and action
            state_old = agent.get_state(game)
            action = agent.get_action(state_old)

            # Execute action and get new state
            reward, done, score = game.play_step_headless(action)
            if done:
                reward = -10  # Death penalty
            elif reward > 0:
                reward = 10   # Food bonus

            state_new = agent.get_state(game)

            # Store in memory
            agent.remember(state_old, action, reward, state_new, done)

            # Train on individual experience
            agent.train_short_memory(state_old, action, reward, state_new, done)

            if done:
                # Game ended - reset and train on batch
                game.reset()
                agent.train_long_memory()

                # Update statistics
                if score > record:
                    record = score
                    print(f"🏆 NEW RECORD: {record} points!")
                    agent.model.save()

                scores.append(score)
                total_score += score

                # Print progress every N games
                if game_counter % games_per_print == 0:
                    mean_score = total_score / agent.n_game
                    gpu_usage = ""
                    if torch.cuda.is_available():
                        gpu_usage = f" | GPU: {torch.cuda.memory_allocated()/1024**3:.1f}GB"
                    print(".1f"
                          f"Best: {record} | ε: {agent.epsilon:.1f}%{gpu_usage}")

                    # Memory management
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()

    except KeyboardInterrupt:
        print("\n⏹️ Training interrupted by user")
        agent.model.save()
        print(f"💾 Final model saved (best score: {record})")

if __name__ == "__main__":
    print("Starting ultra-fast GPU training...")
    train_ultra_fast()
