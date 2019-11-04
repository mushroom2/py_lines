from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import random

MAP_WIDTH = 9
MAP_HEIGHT = 9
ACTIVE = 'active'
MOVE_TO = 'move_to'


colors = [
    Qt.red,
    Qt.yellow,
    Qt.darkYellow,
    Qt.green,
    Qt.blue,
    Qt.cyan,
    Qt.magenta
]


class GameCell(QWidget):
    clicked = pyqtSignal()
    pre_clicked = pyqtSignal()
    refreshed = pyqtSignal()

    def __init__(self, x, y, color, *args, **kwargs):
        super(GameCell, self).__init__(*args, **kwargs)
        self.setFixedSize(QSize(40, 40))
        self.x = x
        self.y = y
        self.color = color
        self.state = None
        self.marked = None
        print(f'created {x} {y}')

    def click(self):
        print(self.x, self.y)
        if self.color:
            self.state = ACTIVE
        else:
            self.state = MOVE_TO
        self.clicked.emit()
        self.refreshed.emit()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        r = event.rect()
        outer, inner = Qt.black, self.color or Qt.lightGray

        p.fillRect(r, QBrush(inner))
        pen = QPen(outer)
        pen.setWidth(1 if not self.state == ACTIVE else 7)
        p.setPen(pen)
        p.drawRect(r)

    def mouseReleaseEvent(self, e):
        if (e.button() == Qt.LeftButton):
            self.pre_clicked.emit()
            self.click()

    def reset(self):
        self.update()

    def refresh(self):
        self.update()

    def turn(self):
        pass


class CellStore(list):
    def get_empty_cells(self):
        return [i for i in self if not i.color]

    def set_color(self):
        target_color = colors[random.randint(0, len(colors) - 1)]
        empty_cells = self.get_empty_cells()
        random.shuffle(empty_cells)
        print(empty_cells[0].x, empty_cells[0].y)
        empty_cells[0].color = target_color

    # todo merge to 1 function
    def get_active(self):
        res = [i for i in self if i.state == ACTIVE]
        return res[0] if res else None

    def get_to_move(self):
        res = [i for i in self if i.state == MOVE_TO]
        return res[0] if res else None

    def get_by_coord(self, x, y):
        return self[(MAP_HEIGHT * x) + y]

    def update_cells(self, demark=False):
        for i in self:
            if demark:
                i.marked = None
            i.update()


class GameWindow(QMainWindow):
    cells = CellStore()
    board = {'prev_active': None, 'allow_turn': False, 'score': 0, 'way_variants': {'actual': [], 'used': []}}

    def __init__(self, *args, **kwargs):
        super(GameWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle('pyLines')
        w = QWidget()
        vb = QVBoxLayout()
        hb = QHBoxLayout()
        self.scoreBoard = QLabel()
        self.scoreBoard.setText(f'{self.board["score"]}')
        hb.addWidget(self.scoreBoard)
        self.grid = QGridLayout()
        self.grid.setSpacing(1)

        vb.addLayout(hb)
        vb.addLayout(self.grid)
        w.setLayout(vb)
        self.setCentralWidget(w)
        self.init_map()
        self.reset_map()
        self.show()

    def is_allow_to_move(self, active_x, active_y, to_move_x, to_move_y):
        current_x = active_x
        current_y = active_y

        while current_x != to_move_x or current_y != to_move_y:
            # todo merge this two methods
            if current_x != to_move_x:
                next_x = current_x + 1 if current_x < to_move_x else current_x - 1
                next_cell = self.cells.get_by_coord(next_x, current_y)

                if next_cell.color and not (next_cell.x == to_move_x and next_cell.y == to_move_y):
                    if current_y - 1 >= 0:
                        possible_cell = self.cells.get_by_coord(current_x, current_y - 1)
                        if not possible_cell.marked and not possible_cell.color \
                                and not(current_x == active_x and current_y - 1 == active_y)\
                                and (current_x, current_y - 1) not in self.board['way_variants']['used']:
                            self.board['way_variants']['actual'].append((current_x, current_y - 1))

                    if current_y + 1 <= MAP_WIDTH:
                        possible_cell = self.cells.get_by_coord(current_x, current_y + 1)
                        if not possible_cell.marked and not possible_cell.color \
                                and not(current_x == active_x and current_y + 1 == active_y)\
                                and (current_x, current_y + 1) not in self.board['way_variants']['used']:
                            self.board['way_variants']['actual'].append((current_x, current_y + 1))

                    if not len(self.board['way_variants']['actual']):
                        return False

                    if (active_x, active_y) in self.board['way_variants']['actual']:
                        self.board['way_variants']['actual'].remove((active_x, active_y))
                        self.board['way_variants']['used'].append((active_x, active_y))
                else:
                    next_cell.marked = True
                    current_x = next_x
                    continue
                    #next_cell.color = colors[0]

            if current_y != to_move_y:
                next_y = current_y + 1 if current_y < to_move_y else current_y - 1
                next_cell = self.cells.get_by_coord(current_x, next_y)

                if next_cell.color and not (next_cell.x == to_move_x and next_cell.y == to_move_y):
                    if current_x - 1 >= 0:
                        possible_cell = self.cells.get_by_coord(current_x - 1, current_y)
                        if not possible_cell.marked and not possible_cell.color\
                                and not(current_x - 1 == active_x and current_y == active_y)\
                                and (current_x - 1, current_y) not in self.board['way_variants']['used']:
                            self.board['way_variants']['actual'].append((current_x - 1, current_y))
                    if current_x + 1 <= MAP_WIDTH:
                        possible_cell = self.cells.get_by_coord(current_x + 1, current_y)
                        if not possible_cell.marked and not possible_cell.color \
                                and not(current_x + 1 == active_x and current_y == active_y)\
                                and (current_x + 1, current_y) not in self.board['way_variants']['used']:
                            self.board['way_variants']['actual'].append((current_x + 1, current_y))
                    if not len(self.board['way_variants']['actual']):
                        return False
                    if (active_x, active_y) in self.board['way_variants']['actual']:
                        self.board['way_variants']['actual'].remove((active_x, active_y))
                        self.board['way_variants']['used'].append((active_x, active_y))
                else:
                    next_cell.marked = True
                    current_y = next_y
                    continue
                    #next_cell.color = colors[0]
            if self.board['way_variants']['actual']:
                for v_x, v_y in self.board['way_variants']['actual']:
                    if self.is_allow_to_move(v_x, v_y, to_move_x, to_move_y):
                        return True
                return False
            return True

        self.update_map(demark=True)
        self.board['way_variants'] = {'actual': [], 'used': []}
        return True

    def click_hook(self, *args):
        active_cell = self.cells.get_active()
        if not active_cell and self.board['prev_active']:
            self.board['prev_active'].state = ACTIVE
            active_cell = self.board['prev_active']
        to_move = self.cells.get_to_move()
        if to_move and active_cell and self.board['allow_turn']:
            # next turn here and analyze if success
            if self.is_allow_to_move(active_cell.x, active_cell.y, to_move.x, to_move.y):
                to_move.color = active_cell.color
                active_cell.color = None
                to_move.state = None
                active_cell.state = None
                self.board['prev_active'] = None
                if self.analyze(to_move.x, to_move.y, to_move.color):
                    self.new_turn()
            else:
                print('disallowed')
                to_move.state = None
                pass

    @staticmethod
    def groupby_delta(inp, delta):
        res = []
        buff = []
        for i in inp:
            if not buff or (buff[-1] == (i - delta)):
                buff.append(i)
            else:
                res.append(buff[:])
                buff = [i]
        if buff:
            res.append(buff)
        res.sort(key=lambda x: len(x), reverse=True)
        if len(res[0]) >= 5:
            # todo do smt with len row to combo score
            return [inp.index(i) for i in res[0]]

    @staticmethod
    def groupby_delta_diagonal(inp, delta, left=False):
        res = []
        buff = []
        cond_delta = -delta if left else delta
        print(inp)
        for x, y in inp:
            if not buff or (buff[-1][0] == x - delta and buff[-1][1] == y + cond_delta):
                buff.append((x, y))
            else:
                res.append(buff[:])
                buff = [(x, y)]
        if buff:
            res.append(buff)
        res.sort(key=lambda x: len(x), reverse=True)
        print(res)
        if len(res[0]) >= 5:
            # todo do smt with len row to combo score
            return [inp.index(i) for i in res[0]]

    def analyze(self, _x, _y, _color) -> bool:
        combos = 0
        # analyze by x
        x_analyze_set = [c for c in self.cells[_y::MAP_HEIGHT] if (c.color == _color or (c.x == _x and c.y == _y))]
        x_combination = self.groupby_delta([i.x for i in x_analyze_set], 1)
        if x_combination:
            for i in x_analyze_set[x_combination[0]: x_combination[-1]+1]:
                i.color = None
                combos += 1
        # analyze by y
        y_analyze_set = [c for c in self.cells if (c.x == _x and (c.color == _color or (c.x == _x and c.y == _y)))]
        y_combination = self.groupby_delta([i.y for i in y_analyze_set], 1)
        if y_combination:
            for i in y_analyze_set[y_combination[0]: y_combination[-1]+1]:
                i.color = None
                combos += 1
        # analyze by z1
        right_diagonals = self.cells[_y + _x::8]
        xy_sum = _x + _y
        right_diagonal = right_diagonals[:xy_sum + 1] if xy_sum <= 8 else \
            right_diagonals[-(8 - ((((_x + _y) % 8) or 8) - 1)):]
        right_diagonal_analyze_set = [i for i in right_diagonal if i.color == _color or (i.x == _x and i.y == _y)]
        right_diagonal_combination = self.groupby_delta_diagonal([(i.x, i.y) for i in right_diagonal_analyze_set], 1)
        if right_diagonal_combination:
            for i in right_diagonal_analyze_set[right_diagonal_combination[0]: right_diagonal_combination[-1]+1]:
                i.color = None
                combos += 1
        # analyze by z2
        start = (_y - _x)
        if start < 0:
            start = 10 - (_x - _y)
        left_diagonals = self.cells[start::10]
        delta = _y - _x
        left_diagonal = left_diagonals[:(8 - delta) + 1] if delta >= 0 else \
            left_diagonals[-(8 - ((((_x - _y) % 8) or 8) - 1)):]
        left_diagonal_analyze_set = [i for i in left_diagonal if i.color == _color or (i.x == _x and i.y == _y)]
        left_diagonal_combination = self.groupby_delta_diagonal([(i.x, i.y) for i in left_diagonal_analyze_set], 1,
                                                                left=True)
        if left_diagonal_combination:
            for i in left_diagonal_analyze_set[left_diagonal_combination[0]: left_diagonal_combination[-1]+1]:
                i.color = None
                combos += 1
        if combos:
            self.board['score'] += (5 * combos)
            return False
        return True

    def pre_click_hook(self):
        # check to switch
        active_cell = self.cells.get_active()
        if active_cell:
            self.board['prev_active'] = active_cell
            active_cell.state = None
            self.board['allow_turn'] = True
        else:
            self.board['allow_turn'] = False
            to_move = self.cells.get_to_move()
            if to_move:
                to_move.state = None

    def init_map(self):
        for x in range(0, MAP_WIDTH):
            for y in range(0, MAP_HEIGHT):
                c = GameCell(x, y, None)
                self.grid.addWidget(c, y, x)
                self.cells.append(c)
                c.clicked.connect(self.click_hook)
                c.pre_clicked.connect(self.pre_click_hook)
                c.refreshed.connect(self.update_map)
        self.new_turn()

    def new_turn(self):
        for i in range(3):
            self.cells.set_color()
        self.update_map()

    def reset_map(self):
        for y in range(0, MAP_WIDTH):
            for x in range(0, MAP_WIDTH):
                w = self.grid.itemAtPosition(x, y).widget()
                w.reset()

    def update_map(self, demark=False):
        self.scoreBoard.setText(f'{self.board["score"]}')
        self.cells.update_cells(demark=demark)


if __name__ == '__main__':
    app = QApplication([])
    window = GameWindow()
    app.exec_()
