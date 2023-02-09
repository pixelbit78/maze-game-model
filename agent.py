import csv
import argparse
import torch
import random
import numpy as np
from collections import deque
from game import MazeGameAI, Direction, Point, BLOCK_SIZE
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001 #learning rate

class Agent:

    def __init__(self, game, mode):
        self.game = game
        self.mode = mode
        self.plot_scores = []
        self.plot_mean_scores = []
        self.total_score = 0
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(13, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.append_csv(header=['l_coll', 'r_coll', 'u_coll', 'd_coll', 'left', 'right', 'up',
            'down', 'target', 'l_t_loc_vis', 'r_t_loc_vis',
            'u_t_loc_vis', 'd_t_loc_vis', 't_vis', 'elapsed', 'score'])

    def append_csv(self, header=None, data=None):
        csv_file = "data/maze.csv"

        if header != None:
            with open(csv_file, mode='w') as file:
                writer = csv.writer(file)
                writer.writerow(header)
        else:
            with open(csv_file, mode='a') as file:
                writer = csv.writer(file)
                writer.writerow(data)

    def load_model(self, file_name='model/model.pth'):
        self.loaded_model = torch.load(file_name)

    def get_state(self):
        tmp_block_size = BLOCK_SIZE
        player = self.game.player
        point_l = Point(player.x - tmp_block_size, player.y)
        point_r = Point(player.x + tmp_block_size, player.y)
        point_u = Point(player.x, player.y - tmp_block_size)
        point_d = Point(player.x, player.y + tmp_block_size)

        dir_l = int(self.game.direction == Direction.LEFT)
        dir_r = int(self.game.direction == Direction.RIGHT)
        dir_u = int(self.game.direction == Direction.UP)
        dir_d = int(self.game.direction == Direction.DOWN)

        state = [

            # collision warning L
            # Danger straight
            (dir_r and self.game.is_collision(point_r)) or
            (dir_l and self.game.is_collision(point_l)) or
            (dir_u and self.game.is_collision(point_u)) or
            (dir_d and self.game.is_collision(point_d)),

            # Danger right
            (dir_u and self.game.is_collision(point_r)) or
            (dir_d and self.game.is_collision(point_l)) or
            (dir_l and self.game.is_collision(point_u)) or
            (dir_r and self.game.is_collision(point_d)),

            # Danger left
            (dir_d and self.game.is_collision(point_r)) or
            (dir_u and self.game.is_collision(point_l)) or
            (dir_r and self.game.is_collision(point_u)) or
            (dir_l and self.game.is_collision(point_d)),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # target location visible
            int(self.game.target.x < self.game.player.x),
            int(self.game.target.x > self.game.player.x),
            int(self.game.target.y < self.game.player.y),
            int(self.game.target.y > self.game.player.y),

            int(self.game.get_distance(self.game.player, self.game.target) < 150),
            int(self.game.is_visible()),

            # target visible
            #int(game.is_visible(point_l)) or
            #int(game.is_visible(point_r)) or
            #int(game.is_visible(point_u)) or
            #int(game.is_visible(point_d)),

             # is target reached
            #int(game.player == game.target),

            # time elapsed
            #int(game.get_elapsed_time()),

            # score of game
            #game.score
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        final_move = [0,0,0]
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.loaded_model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1
        return final_move

    def get_training_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 200 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 300) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move
    
    def handle_input(self, event):
        pass

    def draw(self):
        if self.mode == "play":
            # get old state
            state_old = self.get_state()

            # get move
            final_move = self.get_action(state_old)

            # perform move and get new state
            done, score = self.game.play_step(final_move)

            if done:
                self.game.reset()
                self.n_games += 1

                if score > self.game.record:
                    self.game.record = score

                print('Game', self.n_games, 'Score', score, 'Record:', self.game.record)
        else:
            # get old state
            state_old = self.get_state()

            # get move
            final_move = self.get_training_action(state_old)

            # perform move and get new state
            reward, done, score = self.game.train_step(final_move)
            state_new = self.get_state()

            # train short memory
            self.train_short_memory(state_old, final_move, reward, state_new, done)

            # remember
            self.remember(state_old, final_move, reward, state_new, done)

            self.append_csv(data=np.append(state_old, final_move))
            if done:
                # train long memory, plot result
                self.game.reset()
                self.n_games += 1
                self.train_long_memory()

                if score > self.game.record:
                    self.game.record = score
                    self.model.save()

                print('Game', self.n_games, 'Score', score, 'Record:', self.game.record)

                self.plot_scores.append(score)
                self.total_score += score
                mean_score = self.total_score / self.n_games
                self.plot_mean_scores.append(mean_score)
                plot(self.plot_scores, self.plot_mean_scores)

def train(width, height, train_time):
    agent = Agent(MazeGameAI(width, height, game_time=train_time), "train")

    return agent    

def play(width, height, play_time):
    agent = Agent(MazeGameAI(width, height, game_time=play_time), "play")
    agent.load_model()

    return agent

