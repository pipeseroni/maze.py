#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from curses import *
from locale import setlocale, LC_ALL
from random import choice, randint
from sys import argv, exit
from time import sleep

setlocale(LC_ALL, '')

# Symbols
ARCHIVE = [
    # ASCII lines
    {
        '0000': ' ',
        '0001': '-',
        '0010': '|',
        '0011': '\\',
        '0100': '-',
        '0101': '-',
        '0110': '/',
        '0111': 'v',
        '1000': '|',
        '1001': '/',
        '1010': '|',
        '1011': '<',
        '1100': '\\',
        '1101': '^',
        '1110': '>',
        '1111': '+',
    },

    # Thick lines
    {
        '0000': ' ',
        '0001': '╸',
        '0010': '╻',
        '0011': '┓',
        '0100': '╺',
        '0101': '━',
        '0110': '┏',
        '0111': '┳',
        '1000': '╹',
        '1001': '┛',
        '1010': '┃',
        '1011': '┫',
        '1100': '┗',
        '1101': '┻',
        '1110': '┣',
        '1111': '╋',
    },

    # Thin lines
    {
        '0000': ' ',
        '0001': '╴',
        '0010': '╷',
        '0011': '┐',
        '0100': '╶',
        '0101': '─',
        '0110': '┌',
        '0111': '┬',
        '1000': '╵',
        '1001': '┘',
        '1010': '│',
        '1011': '┤',
        '1100': '└',
        '1101': '┴',
        '1110': '├',
        '1111': '┼',
    },

    # Double lines
    {
        '0000': ' ',
        '0001': '═',
        '0010': '║',
        '0011': '╗',
        '0100': '═',
        '0101': '═',
        '0110': '╔',
        '0111': '╦',
        '1000': '║',
        '1001': '╝',
        '1010': '║',
        '1011': '╣',
        '1100': '╚',
        '1101': '╩',
        '1110': '╠',
        '1111': '╬',
    },
]
SYMBOLS = [ARCHIVE[3]]


# Init
def init(screen):
    rows, cols = screen.getmaxyx()

    matrix = {
        'grid': [[None for _ in range(rows)] for _ in range(cols)],
        'cols': cols,
        'rows': rows
    }

    start = {
        'col': randint(0, cols-1),
        'row': randint(0, rows-1)
    }

    screen.clear()

    def redraw(matrix, seq):
        for point in seq:
            render(screen, matrix, point)

    mazes = []
    # for color in [1,2,4]:
    type = randint(0, 2)
    if type == 0:
        for _ in range(25):
            maze = Maze(matrix,
                        color=choice([1, 2, 3, 4, 5, 9, 10, 11, 12, 13]))
            maze.redraw(redraw)
            mazes.append(maze)

    elif type == 1:
        for _ in range(25):
            maze = Maze(matrix, color=choice([0, 7, 8, 15]))
            maze.redraw(redraw)
            mazes.append(maze)

    elif type == 2:
        maze = Maze(matrix, color=1)
        maze.redraw(redraw)
        mazes.append(maze)
        maze = Maze(matrix, color=2)
        maze.redraw(redraw)
        mazes.append(maze)
        maze = Maze(matrix, color=4)
        maze.redraw(redraw)
        mazes.append(maze)

    return matrix, mazes


# Init colors
def init_colors():
    if has_colors():
        for c in range(0, 8):
            init_pair(c+1, c, -1)


# Get color
def get_color(n):
    if has_colors() != True:
        return color_pair(0)

    if n in range(0, 8):
        return color_pair(n+1)

    if n in range(8, 16):
        return color_pair(n+1-8) | A_BOLD

    return color_pair(0)


# Render matrix
def render(screen, matrix, loc):

    def in_bounds(matrix, col, row):
        cols = len(matrix)
        rows = len(matrix[0])
        return 0 <= col and col < cols and 0 <= row and row < rows

    # col = loc['col']
    # row = loc['row']
    # print(loc)
    col = loc[0]
    row = loc[1]
    dirs = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0)]
    for dir in dirs:
        ncol = col + dir[0]
        nrow = row + dir[1]
        if in_bounds(matrix, ncol, nrow) != True:
            continue
        srows, scols = screen.getmaxyx()
        """
        if (0 <= ncol and ncol < scols and 0 <= nrow and nrow < srows) != True:
            continue
        """
        try:
            if matrix[ncol][nrow] is None:
                screen.addstr(nrow, ncol,
                              SYMBOLS[matrix[ncol][nrow][2]]['0000'])
            else:
                key = ''
                for val in matrix[ncol][nrow][0]:
                    key += str(val)
                screen.addstr(nrow, ncol,
                              SYMBOLS[matrix[ncol][nrow][2]][key],
                              get_color(matrix[ncol][nrow][1]))
        except:
            """
            when drawing to the bottom-right corner, addstr() moves the cursor
            one-past the end, thus failing...
            """
            pass


# Maze class
class Maze:

    # Init
    def __init__(self, matrix, color=None, symbol=None):
        self._matrix = matrix['grid']
        self._cols = matrix['cols']
        self._rows = matrix['rows']
        col = randint(0, self._cols-1)
        row = randint(0, self._rows-1)
        self._color = 0 if color is None else color
        if symbol is None:
            self._symbol = randint(0, len(SYMBOLS)-1)
        else:
            self._symbol = symbol % len(SYMBOLS)
        if self._matrix[col][row] is None:
            self._matrix[col][row] = [[0, 0, 0, 0], self._color, self._symbol]
            self._stack = [(col, row)]
        else:
            self._stack = []
        self._redraw = None

    # Redraw
    def redraw(self, f):
        self._redraw = f

    # Bounds check
    def _in_bounds(self, col, row):
        return 0 <= col and col < self._cols and 0 <= row and row < self._rows

    # Get neighbors
    def _neighbors(self, col, row):
        dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        adj = []
        for i, dir in enumerate(dirs):
            ncol = col + dir[0]
            nrow = row + dir[1]
            comb = self._in_bounds(ncol, nrow) and self._matrix[ncol][nrow]
            if comb is None:
                adj.append({
                    'dir': i,
                    'col': ncol,
                    'row': nrow
                })
        return adj

    # Step
    def step(self, multi=True):
        if multi is True:
            while self._step() == False:
                pass
        else:
            self._step()

        return len(self._stack) != 0

    # Step internal
    def _step(self):
        if len(self._stack) < 1:
            return True

        col = self._stack[-1][0]
        row = self._stack[-1][1]

        """
        print('at (%d,%d) = %s' % (col, row, str(matrix['grid'][col][row])))
        if self._matrix[col][row] is None:
            self._matrix[col][row] = [0,0,0,0]
            return False
        print('at (%d,%d) = %s' % (col, row, str(matrix['grid'][col][row])))
        """

        adj = self._neighbors(col, row)
        if len(adj) == 0:  # no neighbors...
            self._stack = self._stack[:-1]
            # self._stack = []
            return False

        next = choice(adj)
        # next = adj[0]
        # print('at (%d,%d) = %s' % (col, row,
        #                            str(matrix['grid'][col][row][next['dir']])))
        self._matrix[col][row][0][next['dir']] = 1
        self._matrix[next['col']][next['row']] = [[0, 0, 0, 0],
                                                  self._color, self._symbol]
        self._matrix[next['col']][next['row']][0][(next['dir']+2) % 4] = 1
        self._stack.append((next['col'], next['row']))
        self._redraw(self._matrix, [self._stack[-1], self._stack[-2]])
        return True
        # fill(matrix, next['col'], next['row'])
        # break


# Run
def run():
    initscr()
    start_color()
    use_default_colors()
    noecho()
    curs_set(0)
    screen = initscr()
    screen.nodelay(1)
    screen.keypad(1)
    screen.clear()

    init_colors()

    matrix, mazes = init(screen)

    (running, paused, quitting) = range(0, 3)
    state = running

    while state != quitting:

        if state != paused:
            mazes = set([maze for maze in mazes if maze.step()])

            if len(mazes) < 1:
                matrix, mazes = init(screen)

        sleep(0.01)

        event = screen.getch()

        if event == ERR:
            continue
        elif event == ord('q'):
            state = quitting
        elif event == ord('p'):
            state = running if state == paused else paused
        elif event == ord(' '):
            matrix, mazes = init(screen)
            state = running
        elif event == KEY_RESIZE:
            matrix, mazes = init(screen)
            state = running

    screen.clear()
    endwin()

    return 0


# Main
def main(argv=None):
    if argv is None:
        argv = ""
    argc = len(argv)
    run()
    return 0


if __name__ == '__main__':
    exit(main())
