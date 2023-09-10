import numpy as np

from mcts import TreeNode
from Board import Board
import random


def to_tensor(node: TreeNode):
    # one-hot representation for each piece
    brd = node.board
    turn = 1 if brd.is_red_turn() else 0

    piece_to_onehot = {
        'R': np.array([1, 0, 0, 0, 0, 0, 0]),
        'N': np.array([0, 1, 0, 0, 0, 0, 0]),
        'B': np.array([0, 0, 1, 0, 0, 0, 0]),
        'A': np.array([0, 0, 0, 1, 0, 0, 0]),
        'K': np.array([0, 0, 0, 0, 1, 0, 0]),
        'C': np.array([0, 0, 0, 0, 0, 1, 0]),
        'P': np.array([0, 0, 0, 0, 0, 0, 1]),
        'r': np.array([-1, 0, 0, 0, 0, 0, 0]),
        'n': np.array([0, -1, 0, 0, 0, 0, 0]),
        'b': np.array([0, 0, -1, 0, 0, 0, 0]),
        'a': np.array([0, 0, 0, -1, 0, 0, 0]),
        'k': np.array([0, 0, 0, 0, -1, 0, 0]),
        'c': np.array([0, 0, 0, 0, 0, -1, 0]),
        'p': np.array([0, 0, 0, 0, 0, 0, -1]),
        '_': np.array([0, 0, 0, 0, 0, 0, 0])
    }

    # create an empty tensor
    tensor = np.zeros((10, 9, 9))  # the dimension of the tensor is (10, 9, 9)

    # fill in the tensor with one-hot encoding of the pieces
    for i in range(10):
        for j in range(9):
            tensor[i, j, :7] = piece_to_onehot[brd.board[i][j]]

    # fill in the tensor with the last move
    last_step = node.move
    if last_step is not None:
        source, target = last_step
        if source is not None and target is not None:
            tensor[source[0], source[1], 7] = -1
            tensor[target[0], target[1], 7] = 1

    # fill in the tensor with the current turn
    tensor[:, :, 8] = turn

    return tensor


def test_to_tensor():
    test_board = Board()
    # Create a root node
    root = TreeNode(test_board)

    for _ in range(5):
        moves = test_board.possible_moves()
        next_state, src, dst = random.choice(moves)

        node = TreeNode(next_state, root, (src, dst))

        print(next_state.encode())
        print(to_tensor(node).transpose((2, 0, 1)))
        root = node


if __name__ == '__main__':
    test_to_tensor()
    exit()
