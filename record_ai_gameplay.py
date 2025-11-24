#!/usr/bin/env python3
"""
Snake AI Gameplay Video Recording Script
Records the trained model's gameplay to MP4 video file
"""

import torch
import cv2
import numpy as np
import pygame
from pygame.locals import *
from collections import deque
from snake_gameai import SnakeGameAI, Direction, Point, BLOCK_SIZE
# Import game speed for matching recording FPS
from snake_gameai import SPEED
from model import Linear_QNet, QTrainer

class VideoRecorder:
    """Records pygame gameplay to video file"""

    def __init__(self, output_filename='testreinf.mp4', fps=10):
        self.output_filename = output_filename
        self.fps = fps
        self.frames = []
        self.recording = False

    def start_recording(self, width=640, height=480):
        """Initialize video writer"""
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(self.output_filename, fourcc, self.fps, (width, height))
        self.recording = True
        print(f"🎥 STARTED RECORDING: {self.output_filename}")
        print(f"📐 Resolution: {width}x{height} | FPS: {self.fps}")

    def capture_frame(self, surface):
        """Capture current pygame surface"""
        if not self.recording:
            return

        # Convert pygame surface to OpenCV format
        frame_string = pygame.image.tostring(surface, 'RGB')
        frame_np = np.frombuffer(frame_string, dtype=np.uint8)
        frame_np = frame_np.reshape((surface.get_height(), surface.get_width(), 3))

        # Convert RGB to BGR (OpenCV format)
        frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)

        # Write frame to video
        self.video_writer.write(frame_bgr)

    def stop_recording(self):
        """Finalize and save the video"""
        if self.recording:
            self.video_writer.release()
            self.recording = False
            print(f"✅ RECORDING COMPLETE: {self.output_filename}")
            print("🎬 Video saved successfully!")

class RecordedTrainedAgent:
    """Agent that loads and uses the trained model for video recording"""

    def __init__(self):
        self.n_game = 0
        self.epsilon = 0  # No exploration during recording
        self.gamma = 0.9
        self.memory = deque(maxlen=100_000)

        # Load the trained model
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=0.001, gamma=self.gamma)

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

        print("🎥 Recording mode activated - demonstrating trained AI")
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

def record_ai_gameplay():
    """Record trained AI gameplay to video file"""
    print("🎥 SNAKE AI GAMEPLAY VIDEO RECORDER")
    print("🎮 Recording Trained Model Performance")
    print("=" * 60)

    # Initialize components
    agent = RecordedTrainedAgent()
    game = SnakeGameAI()
    recorder = VideoRecorder('testreinf.mp4', fps=SPEED)
    recorder.start_recording(width=640, height=480)

    # Recording parameters
    max_games = 3  # Record 3 games for demo
    games_recorded = 0

    print(f"📹 Recording {max_games} games at {SPEED} FPS (matches your game speed!)")
    print("🎯 Your AI is playing optimally!")

    try:
        while games_recorded < max_games:
            # Get AI action
            state = agent.get_state(game)
            action = agent.get_action(state)

            # Execute action
            reward, done, score = game.play_step(action)

            # Capture frame for video
            recorder.capture_frame(game.display)

            if done:
                games_recorded += 1
                print(f"🎮 Game {games_recorded} completed | Score: {score}")
                game.reset()

                if games_recorded < max_games:
                    print(f"🎯 Starting Game {games_recorded + 1}...")

    except KeyboardInterrupt:
        print("\n⏹️ Recording interrupted by user")

    # Finalize recording
    recorder.stop_recording()

    print("\n" + "=" * 60)
    print("🎬 RECORDING SESSION COMPLETE")
    print("📁 Video saved as: testreinf.mp4")
    print(f"🎮 Games recorded: {games_recorded}")
    print("💡 Video showcases your AI's learned strategies at real-time speed!")

def check_requirements():
    """Check if required packages are installed"""
    try:
        import cv2
        print("✅ OpenCV available for video recording")
    except ImportError:
        print("❌ OpenCV required for video recording")
        print("💡 Install with: pip install opencv-python")
        exit(1)

if __name__ == "__main__":
    check_requirements()
    record_ai_gameplay()
