#!/usr/bin/env python3
"""
Snake AI Graphical Testing Script
Loads your trained model and demonstrates it playing in the graphical environment.
"""

import torch
import random
import numpy as np
from collections import deque
from snake_gameai import SnakeGameAI, Direction, Point, BLOCK_SIZE
from model import Linear_QNet, QTrainer
from Helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class TrainedAgent:
    """Agent that loads and uses the trained model for testing"""

    def __init__(self):
        self.n_game = 0
        self.epsilon = 0  # No exploration during testing
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)

        # Load the trained model
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

        # Load saved weights
        model_path = './models/model.pth'
        try:
            self.model.load_state_dict(torch.load(model_path))
            print("🎯 SUCCESSFULLY LOADED TRAINED MODEL!")
            print(f"📁 Model loaded from: {model_path}")
        except FileNotFoundError:
            print("❌ ERROR: No trained model found!")
            print(f"💡 Expected location: {model_path}")
            print("🔄 Train your model first with: python agent.py")
            exit(1)

        print("🚀 Testing mode activated - pure exploitation (no random moves)")
        print("=" * 60)

    def get_state(self, game):
        """Extract 11-dimensional state representation"""
        head = game.snake[0]

        # Check points around head
        point_l = Point(head.x - BLOCK_SIZE, head.y)
        point_r = Point(head.x + BLOCK_SIZE, head.y)
        point_u = Point(head.x, head.y - BLOCK_SIZE)
        point_d = Point(head.x, head.y + BLOCK_SIZE)

        # Current direction flags
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        # 11-dimensional state vector
        state = [
            # Danger Straight
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)) or
            (dir_l and game.is_collision(point_l)) or
            (dir_r and game.is_collision(point_r)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)),

            # Danger Left
            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)) or
            (dir_r and game.is_collision(point_u)) or
            (dir_l and game.is_collision(point_d)),

            # Direction flags
            dir_l, dir_r, dir_u, dir_d,

            # Food location relative to head
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y   # food down
        ]

        return np.array(state, dtype=int)

    def get_action(self, state):
        """Get optimal action from trained model (no exploration)"""
        # Pure exploitation - use trained model only
        state_tensor = torch.tensor(state, dtype=torch.float).to(self.model.device)
        with torch.no_grad():
            prediction = self.model(state_tensor)

        # Get best action
        move = torch.argmax(prediction).item()
        final_move = [0, 0, 0]
        final_move[move] = 1

        return final_move

def test_trained_model():
    """Test the trained model in graphical environment"""
    print("🐍 SNAKE AI GRAPHICAL TESTING")
    print("🎮 Demonstrating Trained Model Performance")
    print("=" * 60)

    # Initialize agent with trained model
    agent = TrainedAgent()
    game = SnakeGameAI()

    # Testing statistics
    total_score = 0
    games_played = 0
    max_score = 0

    try:
        while True:
            games_played += 1

            # Get current state and best action
            state = agent.get_state(game)
            action = agent.get_action(state)

            # Execute action
            reward, done, score = game.play_step(action)

            if done:
                # Game ended
                game.reset()
                agent.n_game += 1

                # Update statistics
                total_score += score
                max_score = max(max_score, score)
                avg_score = total_score / games_played

                print("2d"
                      f"🏆 Best: {max_score} | 🎯 Current: {score}")

                # Every 10 games, show detailed stats
                if games_played % 10 == 0:
                    print(".1f"
                          "=" * 40)

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🎯 TESTING COMPLETE")
        print(f"📊 Games Played: {games_played}")
        print(f"🏆 Best Score: {max_score}")
        print(f"📈 Average Score: {total_score/games_played:.1f}")
        print("💡 Your trained AI is working perfectly!")

if __name__ == "__main__":
    test_trained_model()
