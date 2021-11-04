
# 4 iterace Odchytávanie udalostí


import pygame
from pygame.locals import *
import sys
import random

# Create the constants (go ahead and experiment with different values)
TILE_SIZE = 80
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
FPS = 30
BLANK = None

# Colours are coded as tuples in form of (Red, Green, Blue)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHT_BLUE = (0, 50, 255)
DARK_TURQUOISE = (3, 54, 73)
GREEN = (0, 204, 0)

BG_COLOR = DARK_TURQUOISE
TILE_COLOR = GREEN
TEXT_COLOR = WHITE
BORDER_COLOR = BRIGHT_BLUE
BASIC_FONT_SIZE = 20

BUTTON_COLOR = WHITE
BUTTON_TEXT_COLOR = BLACK
MESSAGE_COLOR = WHITE


# constants for all four movement directions
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

# global variable to be used in multiple functions, default value is None
FPS_CLOCK = None
DISPLAY_SURFACE = None
BASIC_FONT = None
BUTTONS = None



class Board:
    def __init__(self):
        self.board = []
        self.board_width = 4
        self.board_height = 4
        self.difficulty = 10
        self.x_margin = int((WINDOW_WIDTH - (TILE_SIZE * self.board_width + (self.board_width - 1))) / 2)
        self.y_margin = int((WINDOW_HEIGHT - (TILE_SIZE * self.board_height + (self.board_height - 1))) / 2)
        self.highest_tile = self.board_width * self.board_height - 1

    def generate_board(self):
        for i in range(self.board_height):
            x = []
            for j in range(self.board_width):
                x.append(i * self.board_height + j)
            self.board.append(x)
        self.board[-1][-1] = BLANK


    def generate_new_puzzle(self):
        moves = []
        last = None
        while len(moves) < self.difficulty:
            rnd_move = get_random_move(self, last)
            if is_valid_move(self, rnd_move):
                make_move(self, rnd_move)
                moves.append(rnd_move)
                last = rnd_move
        return moves


class Tile:
    def __init__(self, num, x, y):
        self.num = num
        self.x = x
        self.y = y


    def __eq__(self, ob):
        return self.num == ob.num


    def __str__(self):
        return self.num


def slide_animation(board, direction, animation_speed):
    blank_x, blank_y = get_blank_position(board)
    if direction == UP:
        tile_pos_x, tile_pos_y = blank_x, blank_y + 1
    elif direction == DOWN:
        tile_pos_x, tile_pos_y = blank_x, blank_y - 1
    elif direction == LEFT:
        tile_pos_x, tile_pos_y = blank_x + 1, blank_y
    elif direction == RIGHT:
        tile_pos_x, tile_pos_y = blank_x - 1, blank_y

    num = board.board[tile_pos_y][tile_pos_x]

    blank_x_pix, blank_y_pix = get_left_top_of_tile(board, Tile(None, blank_x, blank_y))
    tile_x_pix, tile_y_pix = get_left_top_of_tile(board, Tile(num, tile_pos_x, tile_pos_y))

    for i in range(1, animation_speed + 1):
        draw_board(board, "")

        tile = Tile(num, tile_pos_x, tile_pos_y)
        rect = pygame.Rect(get_left_top_of_tile(board, tile), (TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(DISPLAY_SURFACE, BG_COLOR, rect)
        text_surf = BASIC_FONT.render(str(tile.num), True, BG_COLOR)
        text_rect = text_surf.get_rect()
        x, y = get_left_top_of_tile(board, tile)
        text_rect.center = (x + TILE_SIZE/2, y + TILE_SIZE/2)
        DISPLAY_SURFACE.blit(text_surf, text_rect)

        if direction == UP:
            distance = blank_y_pix - tile_y_pix
            fraction = distance/animation_speed * i
            draw_tile(board, tile, adj_y=fraction)
        elif direction == DOWN:
            distance = tile_y_pix - blank_y_pix
            fraction = distance/animation_speed * i
            draw_tile(board, tile, adj_y=fraction)
        if direction == LEFT:
            distance = blank_x_pix - tile_x_pix
            fraction = distance/animation_speed * i
            draw_tile(board, tile, adj_x=fraction)
        if direction == RIGHT:
            distance = tile_x_pix - blank_x_pix
            fraction = distance/animation_speed * i
            draw_tile(board, tile, adj_x=fraction)    
    
        pygame.display.update()
        FPS_CLOCK.tick(FPS)





def get_random_move(board, last_move=None):
    list_of_moves = [UP, DOWN, LEFT, RIGHT]
    if last_move == UP:
        list_of_moves.remove(DOWN)
    elif last_move == DOWN:
        list_of_moves.remove(UP)
    elif last_move == LEFT:
        list_of_moves.remove(RIGHT)
    elif last_move == RIGHT:
        list_of_moves.remove(LEFT)
    return random.choice(list_of_moves)


def handle_tile_click(tile_x, tile_y, board):
    blank = get_blank_position(board)
    if tile_x is None or tile_y is None:
        return None
    if (tile_x + 1, tile_y) == blank:
        return RIGHT
    elif (tile_x - 1, tile_y) == blank:
        return LEFT
    elif (tile_x, tile_y + 1) == blank:
        return DOWN
    elif (tile_x, tile_y - 1) == blank:
        return UP
    else:
        return None


def handle_key_press(key, board):
    if (key == pygame.K_LEFT or key == pygame.K_a) and is_valid_move(board, LEFT):
        return LEFT
    elif (key == pygame.K_RIGHT or key == pygame.K_d) and is_valid_move(board, RIGHT):
        return RIGHT
    elif (key == pygame.K_UP or key == pygame.K_w) and is_valid_move(board, UP):
        return UP
    elif (key == pygame.K_DOWN or key == pygame.K_s) and is_valid_move(board, DOWN):
        return DOWN
    else:
        return None


def is_valid_move(board, move):
    blank_x, blank_y = get_blank_position(board)
    if move == UP and blank_y + 1 == board.board_height:
        return False
    elif move == DOWN and blank_y == 0:
        return False
    elif move == RIGHT and blank_x == 0:
        return False
    elif move == LEFT and blank_x + 1 == board.board_width:         
        return False
    else:   
        return True


def get_clicked(x, y, board):
    for index_i, i in enumerate(board.board):
        for index_j, j in enumerate(i):
            left, top = get_left_top_of_tile(board, Tile(j, index_j, index_i))         # maybe error with Blank tile
            rect = pygame.Rect(left, top, TILE_SIZE, TILE_SIZE)
            if rect.collidepoint(x, y):
                return index_j, index_i
    return None, None


def make_move(board, move):
    blank_x, blank_y = get_blank_position(board)
    if move == UP:
        board.board[blank_y][blank_x] = board.board[blank_y + 1][blank_x]
        board.board[blank_y + 1][blank_x] = BLANK
    elif move == DOWN:
        board.board[blank_y][blank_x] = board.board[blank_y - 1][blank_x]
        board.board[blank_y - 1][blank_x] = BLANK
    elif move == LEFT:
        board.board[blank_y][blank_x] = board.board[blank_y][blank_x + 1]       # maybe oppositely
        board.board[blank_y][blank_x + 1] = BLANK
    elif move == RIGHT:
        board.board[blank_y][blank_x] = board.board[blank_y][blank_x - 1]
        board.board[blank_y][blank_x - 1] = BLANK        


def get_blank_position(board):
    for index_i, i in enumerate(board.board):
        for index_j, j in enumerate(i):
            if j is BLANK:
                return index_j, index_i


def draw_board(board, message):
    DISPLAY_SURFACE.fill(BG_COLOR)
    surf, rect = make_text(message, MESSAGE_COLOR, BG_COLOR, 0, 0)          # maybe error with BLANK tile 
    DISPLAY_SURFACE.blit(surf, rect)
    for index_i, i in enumerate(board.board):
        for index_j, j in enumerate(i):
            if j is BLANK:
                continue
            draw_tile(board, Tile(j, index_j, index_i))


def make_text(text, color, bg_color, top, left):
    text_surf = BASIC_FONT.render(text, True, color, bg_color)
    text_rect = text_surf.get_rect()
    text_rect.topleft = (top, left)
    return text_surf, text_rect


def get_left_top_of_tile(board, tile):
    if tile is BLANK:
        return (None, None)
    return (board.x_margin + tile.x * TILE_SIZE + tile.x - 1, board.y_margin + tile.y * TILE_SIZE + tile.y - 1)


def draw_tile(board, tile, adj_x=0, adj_y=0):
    rect = pygame.Rect(get_left_top_of_tile(board, tile), (TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(DISPLAY_SURFACE, TILE_COLOR, rect)
    text_surf = BASIC_FONT.render(str(tile.num), True, MESSAGE_COLOR)
    text_rect = text_surf.get_rect()
    x, y = get_left_top_of_tile(board, tile)
    x += adj_x
    y += adj_y
    text_rect.center = (x + TILE_SIZE/2, y + TILE_SIZE/2)
    DISPLAY_SURFACE.blit(text_surf, text_rect)


def terminate():
    pygame.quit()
    sys.exit()


def main():
    global FPS_CLOCK, DISPLAY_SURFACE, BASIC_FONT, BUTTONS

    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Slide Puzzle')
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', BASIC_FONT_SIZE)

    game_board = Board()
    game_board.generate_board()

    solved_board = Board()
    solved_board.generate_board()

    moves_board = Board()
    moves_board.generate_board()

    draw_board(game_board, "")
    moves = moves_board.generate_new_puzzle()
    for i in moves:
        make_move(game_board, i)


    while True:
        pygame. display.update()
        FPS_CLOCK.tick(FPS)

        draw_board(game_board, "")

        if game_board.board == solved_board.board:
            draw_board(game_board, "SOLVED")
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        terminate()
        else:
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        terminate()
                    move = handle_key_press(event.key, game_board)
                    if move:
                        make_move(game_board, move)
                if event.type == MOUSEBUTTONUP:
                    pos_x, pos_y = pygame.mouse.get_pos()
                    tile_x, tile_y = get_clicked(pos_x, pos_y, game_board)
                    move = handle_tile_click(tile_x, tile_y, game_board)
                    if is_valid_move(game_board, move):
                        make_move(game_board, move)







if __name__ == '__main__':
    main()