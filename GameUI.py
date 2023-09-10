import pygame
import tkinter
from tkinter import messagebox
from pygame.locals import *
from Board import Board
from mcts import TreeNode
from mcts import Mcts


class GameUI(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("cchess")
        self.__screen = pygame.display.set_mode((720, 800), 0, 32)
        self.__background = pygame.image.load('images/boardchess.jpg').convert()

        self.__chess_file_mapping = {('R', 'red_rook'), ('N', 'red_knight'), ('B', 'red_bison'), ('A', 'red_advisor'),
                                     ('C', 'red_cannon'), ('P', 'red_pawn'), ('K', 'red_king'),
                                     ('r', 'black_rook'), ('n', 'black_knight'), ('b', 'black_bison'),
                                     ('a', 'black_advisor'), ('c', 'black_cannon'), ('p', 'black_pawn'),
                                     ('k', 'black_king')}
        self.__chess_img_mapping = {}
        for (key, name) in self.__chess_file_mapping:
            self.__chess_img_mapping[key] = pygame.image.load('images/' + name + '.jpg')

    def put_piece(self, piece, position):
        row, col = position
        self.__screen.blit(self.__chess_img_mapping[piece], (col * 80, row * 80))

    def run(self):
        board = Board()
        is_piece_picked = False
        piece_src_position = None

        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    print("get an mouse button up event.")
                    button_up_pos = pygame.mouse.get_pos()
                    if not is_piece_picked:
                        which_piece_is_picked = get_piece_by_position(board, button_up_pos)
                        if which_piece_is_picked != '_':
                            is_piece_picked = True
                            piece_src_position = button_up_pos
                            print(f"pick an chess {which_piece_is_picked}, src pos is {piece_src_position}")
                    else:
                        src = to_board_pos(piece_src_position)
                        dst = to_board_pos(button_up_pos)
                        another_pick = get_piece_by_position(board, button_up_pos)
                        if another_pick != '_' and is_same_side(board, src, dst):
                            which_piece_is_picked = another_pick
                            piece_src_position = button_up_pos
                            print(f"pick another chess {which_piece_is_picked}, src pos is {piece_src_position}")
                            break
                        else:
                            if not board.is_valid_move(src, dst):
                                is_piece_picked = False
                                piece_src_position = None
                                break

                            board = board.move(src, dst)
                            is_piece_picked = False
                            self.refresh_board(board)

                            if board.is_game_over():
                                game_over(board)
                                board = Board()
                                break

                            node = TreeNode.start_node(board)
                            src, dst = Mcts.search(node, 1000)
                            Mcts.draw_search_tree(node)

                            board = board.move(src, dst)
                            self.refresh_board(board)
                            if board.is_game_over():
                                game_over(board)
                                board = Board()

                if event.type == QUIT:
                    print("get an quit event.")
                    exit()

                self.refresh_board(board)

    def refresh_board(self, board):
        self.__screen.blit(self.__background, (0, 0))
        piece_dict = board.get_all_piece_position()
        for piece in piece_dict:
            for pos in piece_dict[piece]:
                self.put_piece(piece, pos)
        pygame.display.update()


def get_piece_by_position(board, button_up_pos):
    row, col = to_board_pos(button_up_pos)
    return board.board[row][col]


def to_board_pos(pos):
    x, y = pos
    return int(y/80), int(x/80)


def is_same_side(board, src, dst):
    src_row, src_col = src
    dst_row, dst_col = dst
    return board.board[src_row][src_col].islower() == board.board[dst_row][dst_col]


def show_message_box(title, message):
    root = tkinter.Tk()
    root.withdraw()  # 隐藏主窗口
    messagebox.showinfo(title, message)  # 显示消息框
    root.destroy()  # 销毁主窗口


def game_over(board):
    if board.is_draw():
        show_message_box('游戏结束', '和棋')
    if board.is_red_win():
        show_message_box('游戏结束', '红棋胜利')
    else:
        show_message_box('游戏结束', '黑棋胜利')


if __name__ == '__main__':
    e = GameUI()
    e.run()
