# Training Estimator from Kifu.
# It saaumes that test.csv file is alreay esixting.
# NOTE that it imports model_fn.py from model directory.
#
# Usage: python train_kifu.py <dir> [steps]
# Sample usage: python train_kifu.py dnnregressor test.csv 2000

import numpy as np
import tensorflow as tf

import csv
import importlib
import logging
import sys

from tensorflow.python.platform import gfile

import play_go

if len(sys.argv) < 4:
  print('Usage: python train_policy.py <dir> <training_csv> <steps>')
  exit(1)

model_dir=sys.argv[1]
training_csv=sys.argv[2]
steps=int(sys.argv[3])
BATCH_SIZE=16
LEARN_RATE=0.01

def parse_row(row):
  board_exp = [[0] * 81 for _ in range(3)]
  liberty_idx = 81
  liberty_map = [[0] * 81 for _ in range(2)]
  group_idx = 81 * 2
  group_size = [[0] * 81 for _ in range(2)]
  valid_idx = 81 * 3
  valid_move_exp = [[0] * 81 for _ in range(2)]

  for i in range(81):
    stone = int(row[i])
    # Mark empty, black and white for each layer
    board_exp[stone][i] = 1
    if stone != 0:
      liberty_map[stone - 1][i] = row[liberty_idx + i]
      group_size[stone - 1][i] = row[group_idx + i]
  for i in range(81):
    valid_move = int(row[valid_idx + i])
    valid_move_exp[valid_move - 1][i] = 1
  x_out = []
  for l in [board_exp[0], board_exp[1], board_exp[2], liberty_map[0], liberty_map[1],
            group_size[0], group_size[1], valid_move_exp[0] + valid_move_exp[1]]: # 3 + 2 + 2 + 2 (9 layers)
    x_out += l

  y_num = int(row[-2])
  return x_out, y_num

def load_dataset(filename):
  with gfile.Open(filename) as csv_file:
    data_file = csv.reader(csv_file)
    data, target = [], []
    for row in data_file:
      x, y = parse_row(row)
      data.append(np.asarray(x, dtype=np.float32))
      target.append(y)
    return np.array(data), target

def target_nparray(target):
  npas = []
  for t in target:
    npa = [0] * 83
    if t == 0:
      npa[0] = 1
    elif t == 1:
      npa[82] = 1
    else:
      npa[play_go.PackAction(t)] = 1  # Convert 11~99 to 1~81
    npas.append(np.asarray(npa, dtype=np.float32))
  return np.array(npas) 

# Flip functions.
def flip_vertical(x_train, target):
  for feature in x_train:
    feature = feature.reshape((9, 9, 9))[:,::-1,:].reshape((9 * 9 * 9))
  for i in range(len(target)):
    if target[i] < 11:
      continue
    y = int((target[i]) / 10)
    x = target[i] % 10
    y = 10 - y
    target[i] = y * 10 + x

def flip_horizontal(x_train, target):
  for feature in x_train:
    feature = feature.reshape((9, 9, 9))[:,:,::-1].reshape((9 * 9 * 9))
  for i in range(len(target)):
    if target[i] == 0 or target[i] == 82:
      continue
    y = int((target[i]) / 10)
    x = target[i] % 10
    x = 10 - x
    target[i] = y * 10 + x

# Read data set
print('Loading training data')
x_train, target = load_dataset(training_csv)

# Load network model.
print('Working on directory: ', model_dir)
logging.getLogger().setLevel(logging.INFO)
model_fn = importlib.import_module('%s.model_fn' % model_dir)
config = tf.contrib.learn.RunConfig()
config.tf_config.gpu_options.allow_growth=True
estimator = model_fn.GetEstimator(model_dir, config, {"learning_rate": LEARN_RATE})
estimator.fit(x=x_train, y=target_nparray(target), steps=steps, batch_size=BATCH_SIZE)

# Expend to 4 flips.
flip_vertical(x_train, target)
estimator.fit(x=x_train, y=target_nparray(target), steps=steps, batch_size=BATCH_SIZE)

flip_horizontal(x_train, target)
estimator.fit(x=x_train, y=target_nparray(target), steps=steps, batch_size=BATCH_SIZE)

flip_vertical(x_train, target)
estimator.fit(x=x_train, y=target_nparray(target), steps=steps, batch_size=BATCH_SIZE)