import math
import random

from anytree import Node, RenderTree

from Board import Board


class TreeNode:
    def __init__(self, board=Board(), parent=None, move=None):
        self.board = board
        self.parent = parent

        self.terminal = board.is_game_over()

        self.childMap = {}

        self.visits = 0
        self.scores = 0

        self.move = move

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


class Mcts:

    def __init__(self, model):
        self.model = model

    @staticmethod
    def search(root: TreeNode, search_numbers):
        for _ in range(search_numbers):
            print(f"loop {_ + 1}/{search_numbers}")
            node = Mcts.__select(root)
            rollout = Mcts.__rollout(node)
            Mcts.__back_propagate(node, rollout)

        best_move = Mcts.__select_best(root, 0)
        return best_move.get_move()

    @staticmethod
    def __back_propagate(node: TreeNode, rollout_score):
        node.accumulate(1, rollout_score)
        parent = node.get_parent()
        while parent is not None:
            parent.accumulate(1, rollout_score)
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
                exploitation = (current_player * child.get_scores() / child.get_visits())

            exploration = exploration_constant * math.sqrt(math.log(float(current.get_visits()) / child.get_visits()))

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
        return current.expand()

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
        tree = {}
        node = dump(root, None, tree)
        for pre, fill, node in RenderTree(node):
            print("%s%s" % (pre, node.name))


def dump(node: TreeNode, parent, dic):
    name = '{} / {}, {}'.format(node.get_scores(), node.get_visits(), node.board.encode())
    current = Node(name, parent)

    tree_list = []
    for v in node.childMap.values():
        child = '{} / {}, {}'.format(v.get_scores(), v.get_visits(), v.board.encode())
        tree_list.append(child)
        dump(v, current, dic)
    dic[name] = tree_list
    return current
