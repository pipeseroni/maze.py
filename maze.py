#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
from locale import setlocale, LC_ALL
from random import choice, randint, shuffle
from math import ceil
from time import sleep
from argparse import ArgumentParser

VERSION = '0.0.0'

setlocale(LC_ALL, '')

# Symbols
ARCHIVE = {
    'ASCII': ' -|\\--/v|/|<\\^>+',
    'THICK': ' ╸╻┓╺━┏┳╹┛┃┫┗┻┣╋',
    'THIN': ' ╴╷┐╶─┌┬╵┘│┤└┴├┼',
    'DOUBLE': ' ═║╗══╔╦║╝║╣╚╩╠╬',
}

# possible kinds of color sets, user can also use 'random' to pick a different
# one each iteration
COLOR_SETS = ['basic', 'rainbow', 'drab']

MAX_FRAMERATE_CHOICES = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


# Create a randomized color palette based on the given color set with at least
# 'colors_needed' values
def get_color_palette(color_set, colors_needed):
    if color_set == 'random' or color_set not in COLOR_SETS:
        color_set = choice(COLOR_SETS)

    base_palette = None

    if color_set == 'rainbow':
        base_palette = [1, 2, 3, 4, 5, 9, 10, 11, 12, 13]
    elif color_set == 'drab':
        base_palette = [0, 7, 8, 15]
    elif color_set == 'basic':
        base_palette = [1, 2, 4]

    full_palette = base_palette * ceil(colors_needed / len(base_palette))
    shuffle(full_palette)

    return full_palette


def init(screen, all_symbols, color_set, min_pipes, max_pipes):
    rows, cols = screen.getmaxyx()

    matrix = {
        'symbols': all_symbols,
        'grid': [[None for _ in range(rows)] for _ in range(cols)],
        'cols': cols,
        'rows': rows
    }

    screen.clear()

    def redraw(all_symbols, matrix, seq):
        for point in seq:
            render(screen, all_symbols, matrix, point)

    mazes = []

    seed_count = randint(min_pipes, max_pipes)

    palette = get_color_palette(color_set, seed_count)

    for i in range(seed_count):
        maze = Maze(matrix,
                    color=palette[i])
        maze.redraw(redraw)
        mazes.append(maze)

    return matrix, mazes


def init_colors():
    if curses.has_colors():
        for c in range(0, 8):
            curses.init_pair(c + 1, c, -1)


def get_color(n):
    if not curses.has_colors():
        return curses.color_pair(0)

    if n in range(0, 8):
        return curses.color_pair(n + 1)

    if n in range(8, 16):
        return curses.color_pair(n + 1 - 8) | curses.A_BOLD

    return curses.color_pair(0)


# Render matrix
def render(screen, all_symbols, matrix, loc):

    def in_bounds(matrix, col, row):
        cols = len(matrix)
        rows = len(matrix[0])
        return 0 <= col and col < cols and 0 <= row and row < rows

    col = loc[0]
    row = loc[1]
    dirs = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0)]
    for dir in dirs:
        ncol = col + dir[0]
        nrow = row + dir[1]
        if not in_bounds(matrix, ncol, nrow):
            continue
        srows, scols = screen.getmaxyx()
        try:
            cell = matrix[ncol][nrow]
            if matrix[ncol][nrow] is None:
                screen.addstr(nrow, ncol, all_symbols[[2]][0])
            else:
                key = sum(cell[0][i] << (3 - i) for i in range(0, 4))
                screen.addstr(nrow, ncol, all_symbols[cell[2]][key],
                              get_color(cell[1]))
        except (TypeError, curses.error):
            # when drawing to the bottom-right corner, addstr() moves the
            # cursor one-past the end, thus failing...
            pass


class Maze:

    def __init__(self, matrix, color=None, symbol=None):
        self._matrix = matrix['grid']
        self._cols = matrix['cols']
        self._rows = matrix['rows']
        self._all_symbols = matrix['symbols']
        col = randint(0, self._cols - 1)
        row = randint(0, self._rows - 1)
        self._color = 0 if color is None else color
        if symbol is None:
            self._symbol = randint(0, len(self._all_symbols) - 1)
        else:
            self._symbol = symbol % len(self._all_symbols)
        if self._matrix[col][row] is None:
            self._matrix[col][row] = [[0, 0, 0, 0], self._color, self._symbol]
            self._stack = [(col, row)]
        else:
            self._stack = []
        self._redraw = None

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

    def step(self, multi=True):
        if multi is True:
            while not self._step():
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

        adj = self._neighbors(col, row)
        if len(adj) == 0:  # no neighbors...
            self._stack = self._stack[:-1]
            return False

        next = choice(adj)
        self._matrix[col][row][0][next['dir']] = 1
        self._matrix[next['col']][next['row']] = [[0, 0, 0, 0],
                                                  self._color, self._symbol]
        self._matrix[next['col']][next['row']][0][(next['dir'] + 2) % 4] = 1
        self._stack.append((next['col'], next['row']))
        self._redraw(self._all_symbols, self._matrix, self._stack[-1:-3:-1])
        return True


def run(max_framerate, all_symbols, color_set, min_pipes, max_pipes):
    curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.noecho()
    curses.curs_set(0)
    screen = curses.initscr()
    screen.nodelay(1)
    screen.keypad(1)
    screen.clear()

    init_colors()

    frame_sleep_time = 1.0 / max_framerate

    matrix, mazes = init(screen, all_symbols, color_set, min_pipes, max_pipes)

    (running, paused, quitting) = range(0, 3)
    state = running

    while state != quitting:

        if state != paused:
            mazes = set([maze for maze in mazes if maze.step()])

            if len(mazes) < 1:
                matrix, mazes = init(screen, all_symbols, color_set, min_pipes,
                                     max_pipes)

        sleep(frame_sleep_time)

        event = screen.getch()

        if event == curses.ERR:
            continue
        elif event == ord('q'):
            state = quitting
        elif event == ord('p'):
            state = running if state == paused else paused
        elif event == ord(' '):
            matrix, mazes = init(screen, all_symbols, color_set, min_pipes,
                                 max_pipes)
            state = running
        elif event == curses.KEY_RESIZE:
            matrix, mazes = init(screen, all_symbols, color_set, min_pipes,
                                 max_pipes)
            state = running

    screen.clear()
    screen.keypad(0)
    screen.nodelay(0)
    curses.echo()
    curses.endwin()

    return 0


def main():
    p = ArgumentParser(description='Simple curses pipes')
    p.add_argument(
        '-s', '--symbol_set', nargs='*',
        choices=list(ARCHIVE.keys()), default=['ASCII'],
        help=('One or more allowable symbol sets to use, defaults to ASCII '
              'symbols')
        )
    p.add_argument(
        '-f', '--max_framerate', type=int, choices=MAX_FRAMERATE_CHOICES,
        default=100, help='Maximum allowable drawing rate')
    p.add_argument(
        '-c', '--color_set', type=str, choices=COLOR_SETS + ['random'],
        default='random',
        help='Change the color set pipes are drawn with, defaults to random'
        )
    p.add_argument(
        '-p', '--min_pipes', type=int, default=5,
        help='Minimum number of pipes to draw each round, defaults to 5'
        )
    p.add_argument(
        '-P', '--max_pipes', type=int, default=25,
        help='Maximum number of pipes to draw each round, defaults to 25'
        )

    args = p.parse_args()

    # validate number of pipes
    if args.min_pipes < 1:
        p.error('--min_pipes must be greater than 0')
    if args.max_pipes < 1:
        p.error('--max_pipes must be greater than 0')
    if args.min_pipes > args.max_pipes:
        p.error('--min_pipes must be less than or equal to --max_pipes')

    run(
        max_framerate=args.max_framerate,
        all_symbols=[ARCHIVE.get(syms) for syms in args.symbol_set],
        color_set=args.color_set,
        min_pipes=args.min_pipes,
        max_pipes=args.max_pipes
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
