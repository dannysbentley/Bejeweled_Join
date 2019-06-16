import pygame
from pygame.locals import *
import random
import time
import sys
import itertools
import os

RED = (255, 0, 0) # Color for box
BLACK = (0, 0 , 0) # color for background

#CONSTANTS for board and jewel objects. 
BOARD_COLUMNS = 7   #number of columns
BOARD_ROWS = 7      #number of rows
JEWEL_WIDTHS = 50   #width of the jewel 
JEWEL_HEIGHT = 50  #height of the jewel
MARGIN = 2          #margin around display

#window width using column, jewel size and margin
WINDOW_WIDTH = BOARD_COLUMNS * JEWEL_WIDTHS + 2 * MARGIN 
#window height using column, jewel size and margin
WINDOW_HEIGHT = BOARD_ROWS * JEWEL_HEIGHT + 2 * MARGIN + 75
FONT_SIZE = 30
TEXT_OFFSET = MARGIN + 5

SCORE_TABLE = {0: 0, 1: .9, 2: 3, 3: 9, 4: 27}
MINIMUM_MATCH = 3   #matches found
FPS = 30 # Frame rate

#Cell to fill out board with images. 
#sprite - game sprite to fill cell. 
class Cell(object):
    def __init__(self, sprite, key, loc):
        self.offset = 0.0
        self.sprite = sprite
        self.key = key
        self.loc = loc

#read and load the images to fill cell. 
class image(object):
    def __init__(self, joinImage):
        self.images_dictionary = {}
        for c in joinImage:
            value = (pygame.image.load("img/{}.png".format(c)))
            self.images_dictionary[c] = [value]

# object to hold all board information 
class Board(object):
    def __init__(self, width, height):
        joinImage = ['black','yellow','red', 'aqua', 'green', 'purple', 'orange']
        self.images = image(joinImage)
        self.blank = pygame.image.load("img/init.png")
        self.w = width
        self.h = height
        self.size = width * height
        self.board = [Cell(self.blank, 'key', 0) for _ in range(self.size)]
        self.matches = []
        self.score = 0

    #create random cells using a dictionary and filling in the cell class. 
    def randomize(self):
        for i in range(self.size):
            dictionary_sprite = self.images.images_dictionary #dictionary of sprites
            key = random.choice(list(dictionary_sprite)) #random sprite
            self.board[i] = Cell(dictionary_sprite[key][0], key[0], i) #assign to board

    #Make new random sprite at the top 
    def randomize_cell(self, cell):
        i = cell.loc % BOARD_ROWS # use modulo operator for remainder 
        dictionary_sprite = self.images.images_dictionary #dictionary of sprites
        key = random.choice(list(dictionary_sprite)) #random sprite
        self.board[i] = Cell(dictionary_sprite[key][0], key[0], i) #assign to board

    #helper function to get position of cursor. 
    def pos(self, i, j):
        assert(0 <= i < self.w)
        assert(0 <= j < self.h)
        return j * self.w + i

    # frame rate rendering will check matches and fills 
    def tick(self, dt):
        self.matches = self.find_matches() #constantly looking for matches
        #if matches contains length run update. 
        if self.matches:
            for cell in self.matches:
                self.refill_columns(cell) #move columns down.
                self.randomize_cell(cell) #fill in top row cells. 
            self.matches = [] #reset matches to none. 

    #draw sprite in location on the board. 
    def draw(self, display):
        for i, c in enumerate(self.board):
            display.blit(c.sprite, (MARGIN + JEWEL_WIDTHS * (i % self.w), MARGIN + JEWEL_HEIGHT * (i // self.w - c.offset)))

    #swap two sprites with in cursor. 
    def swap(self, cursor):
        i = self.pos(*cursor) #Location of cursor. 
        b = self.board
        b[i].loc = b[i].loc + 1 #change the loc id in class
        b[i+1].loc = b[i].loc - 1 #change the loc id in class

        b[i], b[i+1] = b[i+1], b[i] #swap the sprites
    
    #check for matches along lines.
    def find_matches(self): 
        # divide the board by individual rows. 
        def lines():       
            chunks = [self.board[i * BOARD_ROWS:(i + 1) * BOARD_ROWS] for i in range((len(self.board) + BOARD_ROWS - 1) // BOARD_ROWS )]
            return chunks
        #check fr matches using pointers at current and neightbors 
        def matches():           
            match = []
            chunks = lines()
            ''' DEBUG BOARD AND PRINT ARRAYS
            print('--------------------BOARD--------------------'
                '\n', chunks[0][0].loc, chunks[0][1].loc, chunks[0][2].loc, chunks[0][3].loc, chunks[0][4].loc, chunks[0][5].loc, chunks[0][6].loc,
                '\n', chunks[1][0].loc, chunks[1][1].loc, chunks[1][2].loc, chunks[1][3].loc, chunks[1][4].loc, chunks[1][5].loc, chunks[1][6].loc,
                '\n', chunks[2][0].loc, chunks[2][1].loc, chunks[2][2].loc, chunks[2][3].loc, chunks[2][4].loc, chunks[2][5].loc, chunks[2][6].loc,
                '\n', chunks[3][0].loc, chunks[3][1].loc, chunks[3][2].loc, chunks[3][3].loc, chunks[3][4].loc, chunks[3][5].loc, chunks[3][6].loc,
                '\n', chunks[4][0].loc, chunks[4][1].loc, chunks[4][2].loc, chunks[4][3].loc, chunks[4][4].loc, chunks[4][5].loc, chunks[4][6].loc,
                '\n', chunks[5][0].loc, chunks[5][1].loc, chunks[5][2].loc, chunks[5][3].loc, chunks[5][4].loc, chunks[5][5].loc, chunks[5][6].loc,   
                '\n', chunks[6][0].loc, chunks[6][1].loc, chunks[6][2].loc, chunks[6][3].loc, chunks[6][4].loc, chunks[6][5].loc, chunks[6][6].loc)
            '''
            # iterate over the chunks
            for line in chunks:
                i = 0
                #iterate over the cells by checking the current and neighbor
                while i < BOARD_ROWS - 1: 
                    match_list = []       
                    current = line[i]      
                    neighbor = line[i + 1]
                    #if a match add to temp list                    
                    if current.key == neighbor.key:
                        match_list.append(current)
                        match_list.append(neighbor)
                        j = i + 1
                        #Check nextdoor neightbor till it doesn't match 
                        while j < BOARD_ROWS - 1:
                            nextdoor_neighbor = line[j + 1]
                            if current.key == nextdoor_neighbor.key:
                                match_list.append(nextdoor_neighbor)
                            elif current.key != nextdoor_neighbor.key:
                                i = j
                                break
                            j += 1
                    #if the temp list is larger  or equal to the min match 
                    #add to master list to replace
                    if len(match_list) >= MINIMUM_MATCH:
                        #update score
                        self.score = len(match_list) + self.score
                        #add matches to list 
                        for m in match_list:
                            match.append(m)
                    i += 1
            return match                     
        return matches()

    #Column moves one space down 
    def refill_columns(self, cell):
        b = self.board
        i = cell.loc
        while i > BOARD_ROWS - 1:  
            b[i] = b[i-BOARD_ROWS] # swap sprite from above
            b[i].loc = b[i].loc + BOARD_ROWS #relabel number       
            i -= BOARD_ROWS

class Game(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Join, Inc. Bejewlled Game")
        self.clock = pygame.time.Clock()
        #Built the window for the game.
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) 
        #Set the board for the game 7x7.
        self.board = Board(BOARD_COLUMNS, BOARD_ROWS) 
        #Set game font size 
        self.font = pygame.font.Font(None, FONT_SIZE) 

    #Start of game.
    def start(self):
        self.board.randomize()
        self.cursor = [0,0]
        self.score = 0

    #Quit game
    def quit(self):
        pygame.quit()
        sys.exit()

    def play(self):
        self.start()
        while True:
            self.draw()
            dt = min(self.clock.tick(FPS) / 1000.0, 1.0/FPS)
            #self.swap_time += dt
            for event in pygame.event.get():
                if event.type == KEYUP:
                    self.input(event.key)
                elif event.type == QUIT:
                    self.quit()
            self.board.tick(dt)

    #keyboard inputs for game. 
    def input(self, key):
        if key == K_q:
            self.quit()
        elif key == K_RETURN:
            self.board.score = 0
            self.start()
        elif key == K_RIGHT and self.cursor[0] < self.board.w - 2:
            self.cursor[0] += 1
        elif key == K_LEFT and self.cursor[0] > 0:
            self.cursor[0] -= 1
        elif key == K_DOWN and self.cursor[1] < self.board.h -1:
            self.cursor[1] += 1
        elif key == K_UP and self.cursor[1] > 0:
            self.cursor[1] -= 1
        elif key == K_SPACE:
            self.swap()

    def swap(self):
        self.board.swap(self.cursor)

    def draw(self):
        self.board.draw(self.display)
        self.draw_score()
        self.draw_cursor()
        pygame.display.update()

    def draw_score(self):
        rect = pygame.Rect(0, WINDOW_HEIGHT*.9, WINDOW_WIDTH, WINDOW_HEIGHT / 6)
        pygame.draw.rect(self.display,(0,0,0), rect)
        total_score = self.board.score
        text = self.font.render('Score: {}'.format(int(total_score)), False, RED)
        self.display.blit(text, (TEXT_OFFSET, WINDOW_HEIGHT - FONT_SIZE))

    def draw_cursor(self):
        topLeft = (MARGIN + self.cursor[0] * JEWEL_WIDTHS, MARGIN + self.cursor[1] * JEWEL_HEIGHT)
        topRight = (topLeft[0] + JEWEL_WIDTHS * 2, topLeft[1])
        bottomLeft = (topLeft[0], topLeft[1] + JEWEL_HEIGHT)
        bottomRight = (topRight[0], topRight[1] + JEWEL_HEIGHT)
        pygame.draw.lines(self.display, RED, True, [topLeft, topRight, bottomRight, bottomLeft], 3)

if __name__ == '__main__':
    Game().play()