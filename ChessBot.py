import pygame
from Bot import Bot
import sys, os

import Chess

CLOCK = pygame.time.Clock()

def main():
    board = Chess.Board(side="W")
    bot = Bot.Bot(board)
    
    while True:
        CLOCK.tick(1000)
        
        bot.board = board
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        
        # visualize/draw the board
        bot.randomMoves(2)
        board.move()
        board.draw()

if __name__ == "__main__":
    main()