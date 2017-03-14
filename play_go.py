# Library to play Go.

import copy

def NearPositions(x, y):
  return ((x-1, y), (x+1, y), (x, y-1), (x, y+1))

def GetConnented(board, group, x, y):
  group.add((x, y))
  stone = board[x][y]
  for pos in NearPositions(x, y):
    if board[pos[0]][pos[1]] == stone and not (pos[0], pos[1]) in group:
      GetConnented(board, group, pos[0], pos[1])
      
def GetLiberty(board, group):
  # It should check dup of liberty. Just ok to check 0 or Ko.
  liberty = 0
  for pos in group:
    for n_pos in NearPositions(pos[0], pos[1]):
      if board[n_pos[0]][n_pos[1]] == 0:
        liberty = liberty + 1
  return liberty

def CaptureGroup(board, group):
  for pos in group:
    board[pos[0]][pos[1]] = 0

def IsOpponentStone(target, source):
  return target in (1,-1) and target != source

def PlayGo(board, stone, x, y):
  board[x][y] = stone
  
  # Capture stones
  capture_count = 0
  capture_pos = None
  for pos in NearPositions(x, y):
    if IsOpponentStone(board[pos[0]][pos[1]], stone):
      group = set()
      GetConnented(board, group, pos[0], pos[1])
      liberty = GetLiberty(board, group)      
      if liberty == 0:
        CaptureGroup(board, group)
        capture_count = capture_count + len(group)
        capture_pos = pos

  # Check forbidden move
  group = set()
  GetConnented(board, group, x, y)
  if GetLiberty(board, group) == 0:
    return False, None

  # Check Ko
  if capture_count == 1:
    if len(group) == 1 and GetLiberty(board, group) == 1:
      return True, [capture_pos[0], capture_pos[1]]
  return True, None

def FowardFeatures(feature):
  board, last_move, ko = FromFeature(feature)
  next_move = -last_move
  features = []
  # Try all valid moves
  for i in range(1,10):
    for j in range(1,10):
      if not board[i][j] == 0 or [i, j] == ko:
        continue
      board2 = copy.deepcopy(board)  # make clone for a move
      valid, ko = PlayGo(board2, next_move, i, j)
      if not valid:
        continue
      feature2 = list(feature)  # make clone for eval
      feature2[(i-1)*9+j-1] = next_move
      feature2[81] = next_move
      if ret != None:
        feature2[82:84] = ko[0:2]
      features.append(feature2)
  return features  

def InitBoard():
  board = [x[:] for x in [[0] * 11] * 11]
  for i in range(11):
    board[i][0] = 'E'
    board[0][i] = 'E'
    board[i][10] = 'E'
    board[10][i] = 'E'
  return board

def ToFeature(board, last_move, ko, result):
  if ko == None:
    ko = [0, 0]
  else:
    board[ko[0]][ko[1]] = last_move / 2  # Set 0.5 or -0.5 for ko position.
  board_serial = [item for innerlist in board[1:-1] for item in innerlist[1:-1]]
  if not ko == None:
    board[ko[0]][ko[1]] = 0
  return board_serial + [last_move] + ko + [result]

def FromFeature(feature):
  board = InitBoard()  
  last_move = int(feature[81])
  ko = feature[82:84]
  idx = 0
  for i in range(1,10):
    for j in range(1,10):
      if abs(feature[idx]) == 1:
        # 0.5 and -0.5 indicates ko.
        board[i][j] = feature[idx]
      idx = idx + 1
  return board, last_move, ko

# Print out human readable.
BOARD_CHAR = { -1: 'O', 1: '@', 0: '.' }
TURN_MSG = { 1: 'BLACK(@)', -1: 'WHITE(O)' }
def SPrintBoard(feature):
  lines = []
  board = feature[:81]
  last_move = feature[81]
  ko = feature[82:84]
  pos = 0
  for row in range(1, 10):
    outstr = ''
    for col in range(1, 10):
      if row == ko[0] and col == ko[1]:
        outstr = outstr + '*'
      else:
        outstr = outstr + BOARD_CHAR[board[pos]]
      pos = pos + 1
    lines.append(outstr)
  lines.append('Last move %s' % TURN_MSG[last_move])
  return '\n'.join(lines)

 
# Main loop
def main():
  while True:
    feature = input('Enter board feature [[board]*81, last_move, [ko]*2]:\n')
    if isinstance(feature, (list, tuple)):
      feature = list(feature)
    else:
      feature = feature.split(',')
    if len(feature) < 84:
      continue
    feature = list(map(float, feature))[:84]
    board, last_move, ko = FromFeature(feature)
    print(SPrintBoard(feature))

if __name__ == "__main__":
    main()
