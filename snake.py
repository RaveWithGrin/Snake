import curses
import math
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
from random import randint, choice

MIN_X = 0
MIN_Y = 0
MAX_X = 60
MAX_Y = 20

WRAP_AROUND = False
HIT_SELF = False

KEY_ESCAPE = 27


class Game():
    def __init__(self):
        curses.initscr()
        self.window = curses.newwin(MAX_Y, MAX_X, MIN_Y, MIN_X)
        self.window.keypad(1)
        curses.noecho()
        curses.curs_set(0)
        self.window.border(0)
        self.window.nodelay(1)
        self.score = 0
        self.snake = [[4, 10], [4, 9], [4, 8], [
            4, 7], [4, 6], [4, 5], [4, 4], [4, 3]]
        self.game_over = False
        self.last_move = KEY_RIGHT
        self.place_food()

    def check_borders(self):
        if WRAP_AROUND:
            if self.snake[0][0] == MIN_Y:
                self.snake[0][0] = MAX_Y - 2
            if self.snake[0][1] == MIN_X:
                self.snake[0][1] = MAX_X - 2
            if self.snake[0][0] == MAX_Y - 1:
                self.snake[0][0] = MIN_Y + 1
            if self.snake[0][1] == MAX_X - 1:
                self.snake[0][1] = MIN_X + 1
        elif self.snake[0][0] in [MIN_Y, MAX_Y - 1] or self.snake[0][1] in [MIN_X, MAX_X - 1]:
            self.game_over = True

    def check_food(self):
        if self.snake[0] == self.food:
            self.score += 1
            self.place_food()
        else:
            tail = self.snake.pop()
            self.window.addch(tail[0], tail[1], ' ')

    def check_self(self):
        if not HIT_SELF:
            if self.snake[0] in self.snake[1:]:
                self.game_over = True

    def draw_game(self):
        self.window.border(0)
        self.window.addstr(0, 2, 'Snake: {}'.format(self.snake[0]))
        self.window.addstr(0, 22, 'Score: {}'.format(str(self.score)))
        self.window.addstr(0, 42, 'Food: {}'.format(self.food))
        self.window.addstr(0, 56, str(self.last_move))
        self.window.timeout(
            150 - (len(self.snake) / 5 + len(self.snake) / 10) % 120)
        self.window.addch(self.snake[0][0], self.snake[0][1], '%')
        for index, position in enumerate(self.snake[1:]):
            self.window.addch(position[0], position[1], '#')

    def finished(self):
        return self.game_over

    def get_food(self):
        return self.food

    def get_key(self):
        return self.window.getch()

    def get_score(self):
        return self.score

    def get_snake(self):
        return self.snake

    def get_window(self):
        return self.window

    def move_snake(self, move):
        self.last_move = move
        self.snake.insert(0, [self.snake[0][0] + (move == KEY_DOWN and 1) + (move == KEY_UP and -1),
                              self.snake[0][1] + (move == KEY_LEFT and -1) + (move == KEY_RIGHT and 1)])

    def place_food(self):
        self.food = [randint(MIN_Y + 1, MAX_Y - 2),
                     randint(MIN_X + 1, MAX_X - 2)]
        while self.food in self.snake:
            self.food = [randint(MIN_Y + 1, MAX_Y - 2),
                         randint(MIN_X + 1, MAX_X - 2)]
        self.window.addch(self.food[0], self.food[1], '*')


def get_distance(head, food):
    return math.sqrt(((head[0] - food[0]) ** 2) + ((head[1] - food[1]) ** 2))


def get_random_movement(previous_key, window, snake):
    event = window.getch()
    if event != -1:
        key = event
    else:
        key = previous_key
    if key == KEY_ESCAPE:
        return key
    else:
        valid_moves = get_valid_moves(snake)
        if len(valid_moves) > 0:
            if len(valid_moves == 1):
                return valid_moves[0]
            else:
                move = choice(valid_moves)
                new_position = [snake[0][0] + (move == KEY_DOWN and 1) + (move == KEY_UP and -1),
                                snake[0][1] + (move == KEY_LEFT and -1) + (move == KEY_RIGHT and 1)]
                while new_position in snake or new_position[0] in [MIN_Y, MAX_Y - 1] or new_position[1] in [MIN_X, MAX_X - 1]:
                    move = choice([KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN])
                    new_position = [snake[0][0] + (move == KEY_DOWN and 1) + (
                        move == KEY_UP and -1), snake[0][1] + (move == KEY_LEFT and -1) + (move == KEY_RIGHT and 1)]
                return move
        else:
            return KEY_ESCAPE


def get_shortest_movement(previous_key, window, snake, food):
    event = window.getch()
    if event != -1:
        key = event
    else:
        key = previous_key
    if key == KEY_ESCAPE:
        return key
    else:
        valid_moves = get_valid_moves(snake)
        if len(valid_moves) > 0:
            shortest_distance = float('inf')
            for move in valid_moves:
                new_position = [snake[0][0] + (move == KEY_DOWN and 1) + (
                    move == KEY_UP and -1), snake[0][1] + (move == KEY_LEFT and -1) + (move == KEY_RIGHT and 1)]
                distance = get_distance(new_position, food)
                if distance < shortest_distance:
                    shortest_distance = distance
                    shortest_move = move
            return shortest_move
        else:
            return KEY_ESCAPE


def opposite_direction(direction):
    opposite = {
        KEY_LEFT: KEY_RIGHT,
        KEY_RIGHT: KEY_LEFT,
        KEY_DOWN: KEY_UP,
        KEY_UP: KEY_DOWN
    }
    return opposite.get(direction)


def get_user_movement(previous_key, window):
    event = window.getch()
    if event != -1:
        key = event
    else:
        key = previous_key
    if key not in [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, 27] or key == opposite_direction(previous_key):
        key = previous_key
    return key


def get_valid_moves(snake):
    valid = []
    for move in [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN]:
        new_position = [snake[0][0] + (move == KEY_DOWN and 1) + (move == KEY_UP and -1),
                        snake[0][1] + (move == KEY_LEFT and -1) + (move == KEY_RIGHT and 1)]
        if new_position not in snake and new_position[0] not in [MIN_Y, MAX_Y - 1] and new_position[1] not in [MIN_X, MAX_X - 1]:
            valid.append(move)
    return valid


game = Game()
move = KEY_RIGHT
# While ESCAPE not pressed
while move != KEY_ESCAPE and not game.finished():
    game.draw_game()
    #move = get_user_movement(move, game.get_window())
    #move = get_random_movement(move, game.get_window(), game.get_snake())
    move = get_shortest_movement(
        move, game.get_window(), game.get_snake(), game.get_food())
    game.move_snake(move)
    game.check_borders()
    game.check_self()
    game.check_food()

curses.endwin()
print('\nScore - {}'.format(str(game.get_score())))
