from copy import deepcopy


class Board:
    def __init__(self, board=None):
        self.board = [
            ['r', 'n', 'b', 'a', 'k', 'a', 'b', 'n', 'r'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', 'c', '_', '_', '_', '_', '_', 'c', '_'],
            ['p', '_', 'p', '_', 'p', '_', 'p', '_', 'p'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['P', '_', 'P', '_', 'P', '_', 'P', '_', 'P'],
            ['_', 'C', '_', '_', '_', '_', '_', 'C', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['R', 'N', 'B', 'A', 'K', 'A', 'B', 'N', 'R']
        ]
        self.player_1 = 'red'  # player_1 表示轮到谁走，player_2表示上一步是谁走的
        self.player_2 = 'black'
        self._is_game_over = False
        self._num_steps_no_capture = 0
        self._winner = None

    def move(self, start_pos, end_pos):
        next_board = self.clone()
        if not next_board.is_game_over():
            start_x, start_y = start_pos
            end_x, end_y = end_pos
            piece = next_board.board[start_x][start_y]
            target = next_board.board[end_x][end_y]

            if next_board.is_valid_move(start_pos, end_pos):
                next_board.board[end_x][end_y] = piece
                next_board.board[start_x][start_y] = '_'

                if target.lower() == 'k':
                    next_board._is_game_over = True

                    if target.islower():
                        next_board._winner = 'red'
                    else:
                        next_board._winner = 'black'

            if target != '_':
                next_board._num_steps_no_capture = 0
            else:
                next_board._num_steps_no_capture += 1

            (next_board.player_1, next_board.player_2) = (next_board.player_2, next_board.player_1)
        return next_board

    def encode(self):
        return "".join(["".join(row) for row in self.board])

    def possible_moves(self):
        next_states = []
        for x in range(10):
            for y in range(9):
                piece = self.board[x][y]
                if piece != '_' and piece.islower() == self.is_black_turn():
                    piece_moves = self.__get_piece_moves__((x, y))
                    for move in piece_moves:
                        next_states.append((self.move((x, y), move), (x, y), move))
        return next_states

    def is_game_over(self):
        return self._is_game_over

    def is_red_win(self):
        return self._winner == 'red'

    def is_black_win(self):
        return self._winner == 'black'

    def is_red_turn(self):
        return self.player_1 == 'red'

    def is_black_turn(self):
        return self.player_1 == 'black'

    def is_last_red_turn(self):
        return self.player_2 == 'red'

    def is_last_black_turn(self):
        return self.player_2 == 'black'

    def is_draw(self):
        return self._num_steps_no_capture >= 60

    def get_all_piece_position(self):
        piece_positions = {}
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                if piece != '_':
                    if piece not in piece_positions:
                        piece_positions[piece] = []
                    piece_positions[piece].append((i, j))
        return piece_positions

    def dump(self):
        board_symbols = {
            'k': '将', 'K': '帅',
            'a': '士', 'A': '仕',
            'b': '象', 'B': '相',
            'n': '马', 'N': '马',
            'r': '车', 'R': '車',
            'c': '炮', 'C': '砲',
            'p': '卒', 'P': '兵',
            '_': '十'
        }

        print("  0 1 2 3 4 5 6 7 8")
        for x in range(10):
            row = []
            for y in range(9):
                piece = self.board[x][y]
                row.append(board_symbols[piece])
            print(f"{x} {' '.join(row)}")

    def clone(self):
        board = Board()
        board.__dict__ = deepcopy(self.__dict__)
        return board

    def __get_piece_moves__(self, position):
        x, y = position
        piece = self.board[x][y]

        piece_type = piece.lower()
        moves = []

        if piece_type == 'k':
            moves = self.__get_piece_king_moves__(position)
        elif piece_type == 'a':
            moves = self.__get_piece_advisor_moves__(position)
        elif piece_type == 'b':
            moves = self.__get_piece_bison_moves__(position)
        elif piece_type == 'n':
            moves = self.__get_piece_knight_moves__(position)
        elif piece_type == 'r':
            moves = self.__get_piece_rook_moves__(position)
        elif piece_type == 'c':
            moves = self.__get_piece_canon_moves__(position)
        elif piece_type == 'p':
            moves = self.__get_piece_pawn_moves__(position)

        return moves

    def __get_piece_king_moves__(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < 10 and 0 <= ny < 9:
                # 帅/将的宫限制
                if piece.islower() and (0 <= nx <= 2) and (3 <= ny <= 5):
                    target = self.board[nx][ny]
                    if target == '_' or target.isupper():
                        moves.append((nx, ny))
                elif piece.isupper() and (7 <= nx <= 9) and (3 <= ny <= 5):
                    target = self.board[nx][ny]
                    if target == '_' or target.islower():
                        moves.append((nx, ny))

                if piece == 'K' and nx == x - 1 and ny == y:
                    # 判断将/帅之间是否隔着棋子
                    for i in range(x - 1, -1, -1):
                        if self.board[i][y] != '_' and self.board[i][y] != 'k':
                            break
                        if self.board[i][y] == 'k':
                            moves.append((i, y))
                            break

                elif piece == 'k' and nx == x + 1 and ny == y:
                    for i in range(x + 1, 10):
                        if self.board[i][y] != '_' and self.board[i][y] != 'K':
                            break
                        if self.board[i][y] == 'K':
                            moves.append((i, y))

        return moves

    def __get_piece_advisor_moves__(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < 10 and 0 <= ny < 9:
                # 士/仕的宫限制
                if piece.islower() and (3 <= ny <= 5) and (0 <= nx <= 2):
                    target = self.board[nx][ny]
                    if target == '_' or target.isupper():
                        moves.append((nx, ny))
                elif piece.isupper() and (3 <= ny <= 5) and (7 <= nx <= 9):
                    target = self.board[nx][ny]
                    if target == '_' or target.islower():
                        moves.append((nx, ny))

        return moves

    def __get_piece_bison_moves__(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # 确保在棋盘内
            if 0 <= nx < 10 and 0 <= ny < 9:
                target = self.board[nx][ny]
                # 没有越过河
                if piece.islower() and (0 <= nx <= 4) or piece.isupper() and (5 <= nx <= 9):
                    # 没有被蹩腿
                    blocking_x, blocking_y = (x + dx // 2, y + dy // 2)
                    blocking_piece = self.board[blocking_x][blocking_y]
                    if blocking_piece == '_':
                        if target == '_' or piece.islower() != target.islower():
                            moves.append((nx, ny))

        return moves

    def __get_piece_rook_moves__(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            while 0 <= nx < 10 and 0 <= ny < 9:
                target = self.board[nx][ny]
                if target == '_':
                    moves.append((nx, ny))
                else:
                    if piece.islower() != target.islower():
                        moves.append((nx, ny))
                    break

                nx, ny = nx + dx, ny + dy

        return moves

    def __get_piece_knight_moves__(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        offsets = [
            (-1, -2), (1, -2), (-1, 2), (1, 2),
            (-2, -1), (-2, 1), (2, -1), (2, 1)
        ]

        for dx, dy in offsets:
            nx, ny = x + dx, y + dy

            # 确保在棋盘内
            if 0 <= nx < 10 and 0 <= ny < 9:
                target = self.board[nx][ny]
                # 没有被蹩腿
                blocking_x, blocking_y = x, y
                if dx == 2 or dx == -2:
                    blocking_x = x + dx // 2
                elif dy == 2 or dy == -2:
                    blocking_y = y + dy // 2
                blocking_piece = self.board[blocking_x][blocking_y]
                if blocking_piece == '_':
                    if target == '_' or piece.islower() != target.islower():
                        moves.append((nx, ny))

        return moves

    def __get_piece_canon_moves__(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            has_cannon = False

            while 0 <= nx < 10 and 0 <= ny < 9:
                target = self.board[nx][ny]

                if not has_cannon:
                    if target == '_':
                        moves.append((nx, ny))
                    else:
                        has_cannon = True
                else:
                    if target != '_':
                        if piece.islower() != target.islower():
                            moves.append((nx, ny))
                        break

                nx, ny = nx + dx, ny + dy

        return moves

    def __get_piece_pawn_moves__(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        if piece.islower():
            directions = [(1, 0)]
            if x >= 5:
                directions.extend([(0, 1), (0, -1)])
        else:
            directions = [(-1, 0)]
            if x <= 4:
                directions.extend([(0, 1), (0, -1)])

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < 10 and 0 <= ny < 9:
                target = self.board[nx][ny]
                if target == '_' or piece.islower() != target.islower():
                    moves.append((nx, ny))

        return moves

    def is_valid_move(self, start_pos, end_pos):
        start_x, start_y = start_pos
        piece = self.board[start_x][start_y]

        # 如果起始位置没有棋子，返回False
        if piece == '_':
            return False

        # 确保棋子的颜色与当前回合颜色相符
        if self.is_red_turn() and piece.islower():
            return False
        if not self.is_red_turn() and piece.isupper():
            return False

        # 获取给定棋子的所有合法走子
        legal_moves = self.__get_piece_moves__(start_pos)

        # 检查终止位置是否在合法走子中
        return end_pos in legal_moves
