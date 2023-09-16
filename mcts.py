import math
import random

import numpy as np
from anytree import Node, RenderTree

from Board import Board
from net import load_model
from uci import get_probability


class TreeNode:
    def __init__(self, board=Board(), parent=None, move=None, probability=.0):
        self.board = board
        self.parent = parent

        self.terminal = board.is_game_over()

        self.childMap = {}

        self.visits = 0
        self.scores = 0

        self.move = move
        self.probability = probability

    @staticmethod
    def start_node(board: Board):
        return TreeNode(board, None, None)

    def get_parent(self):
        return self.parent

    def is_terminal(self):
        return self.terminal

    def get_visits(self):
        return self.visits

    def get_scores(self):
        return self.scores

    def get_move(self):
        return self.move

    def increase_visits(self):
        self.visits += 1

    def accumulate_scores(self, score):
        self.scores += score

    @staticmethod
    def child_node(board: Board, parent, move):
        return TreeNode(board, parent, move)

    def replica(self):
        return TreeNode(self.board.clone(), None, (None, None))

    def accumulate(self, visits, scores):
        self.visits += visits
        self.scores += scores

    def get_next_turn(self):
        return 'red' if self.board.is_red_turn() else 'black'

    def get_last_turn(self):
        return 'red' if self.board.is_last_red_turn() else 'black'

    def terminal_score(self):
        if not self.board.is_game_over():
            raise Exception("game is on going.")
        if self.board.is_draw():
            return 0
        if self.board.is_red_win():
            return 1
        if self.board.is_black_win():
            return -1

        raise Exception("error state.")

    def expand(self):
        moves = self.board.possible_moves()

        for nest_state, src, dst in moves:
            if nest_state.encode() not in self.childMap:
                node = TreeNode.child_node(nest_state, self, (src, dst))
                self.childMap[nest_state.encode()] = node
                return node
        return None

    def is_fully_expanded(self):
        moves = self.board.possible_moves()
        return len(self.childMap) == len(moves)

    def rollout(self):
        while not self.board.is_game_over():
            moves = self.board.possible_moves()
            next_state, src, dst = random.choice(moves)
            self.board = next_state
        return self.terminal_score()

    def get_children(self):
        return self.childMap.values()

    def get_possible_moves(self):
        return self.board.possible_moves()


model = load_model()


class Mcts:
    @staticmethod
    def search(root: TreeNode, search_numbers):
        for _ in range(search_numbers):
            print(f"loop {_ + 1}/{search_numbers}")
            node = Mcts.__select(root)
            # rollout = Mcts.__rollout(node)
            Mcts.__back_propagate_with_net(node)

        best_move = Mcts.__select_best(root, 0)

        name = '{} / {}, {}'.format(0 if root.get_visits() == 0 else root.get_scores() / root.get_visits(),
                                    root.get_visits(),
                                    root.board.encode())
        print(name)
        for child in root.get_children():
            name = '{} / {}, {}'.format(0 if child.get_visits() == 0 else child.get_scores() / child.get_visits(),
                                        child.get_visits(),
                                        child.board.encode())
            print(name)
        return best_move.get_move()

    @staticmethod
    def __back_propagate(node: TreeNode, rollout_score):
        node.accumulate(1, rollout_score)
        parent = node.get_parent()
        while parent is not None:
            parent.accumulate(1, rollout_score)
            parent = parent.get_parent()

    @staticmethod
    def __back_propagate_with_net(node: TreeNode):
        node.visits += 1
        parent = node.get_parent()
        while parent is not None:
            parent.increase_visits()
            parent.accumulate_scores(node.get_scores())
            parent = parent.get_parent()

    @staticmethod
    def __rollout(node: TreeNode):
        current = node.replica()
        return current.rollout()

    @staticmethod
    def __select_best(current: TreeNode, exploration_constant):
        best_score = float('-inf')
        best_moves = []

        for child in current.get_children():
            current_player = 1.0 if child.get_last_turn() == 'red' else -1.0
            exploitation = .0

            if child.get_visits() != 0:
                exploitation = (
                        current_player * child.get_scores() / child.get_visits()) if child.get_visits() > 0 else 0

            # exploration = exploration_constant * math.sqrt(math.log(float(current.get_visits()) / child.get_visits()))
            exploration = exploration_constant * child.probability * \
                          (math.sqrt(current.get_visits()) / (1 + child.get_visits()))

            move_score = exploitation + exploration

            if move_score > best_score:
                best_moves = [child]
                best_score = move_score
            elif math.fabs(move_score - best_score) < 0.0001:
                best_moves.append(child)

        if len(best_moves) == 0:
            raise Exception("best move is empty.")

        return random.choice(best_moves)

    @staticmethod
    def __expand(current: TreeNode):
        state_tensor = to_tensor(current)
        policy_pred, value_pred = model.predict(np.expand_dims(state_tensor, axis=0))
        policy_pred = np.squeeze(policy_pred, axis=0)

        possible_moves = current.get_possible_moves()
        for i, possible_move in enumerate(possible_moves):
            board, src, dst = possible_move
            probability = get_probability(src, dst, policy_pred)
            child_node = TreeNode(board, current, (src, dst), probability)

            child_node.scores = value_pred.item()

            current.childMap[board.encode()] = child_node

        if len(current.childMap) != 0:
            best_child = max(current.childMap.values(), key=lambda child: child.probability)
            return best_child

        return None

    @staticmethod
    def __select(root: TreeNode):
        current = root
        while current is not None and not current.is_terminal():
            if current.is_fully_expanded():
                current = Mcts.__select_best(current, 2)
            else:
                return Mcts.__expand(current)

        return current

    @staticmethod
    def draw_search_tree(root: TreeNode):
        with open('mcst_result.txt', 'a', encoding='utf-8') as f:
            tree = {}
            node = dump(root, None, tree)
            for pre, fill, node in RenderTree(node):
                f.write(("%s%s\n" % (pre, node.name)))


def dump(node: TreeNode, parent, dic):
    name = '{} / {}, {}'.format(0 if node.get_visits() == 0 else node.get_scores() / node.get_visits(),
                                node.get_visits(),
                                node.board.encode())
    current = Node(name, parent)

    tree_list = []
    for v in node.childMap.values():
        child = '{} / {}, {}'.format(0 if node.get_visits() == 0 else node.get_scores() / node.get_visits(),
                                     v.get_visits(),
                                     v.board.encode())
        tree_list.append(child)
        dump(v, current, dic)
    dic[name] = tree_list
    return current


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
