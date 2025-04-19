import string
import random
from time import sleep

class Bot:
    def __init__(self, board):
        self.board = board
        self.side = "W" if self.board.side == "B" else "B"
        self.notations = {}
        self.history = []

        self.sidePieces = []
        # from https://en.wikipedia.org/wiki/Chess_piece_relative_value
        self.values = {"p" : 1, "n" : 3, "b" : 3, "r" : 5, "q" : 9, "k" : 200}
        self.pieces = [piece for piece in self.board.pieces if piece[1] == self.side]
 
        self.autos = {
            "random" : self.randomMoves
        }

        for i in range(0, 400, 50):
            self.notations.update({ string.ascii_letters[(i//50)] : i })
            self.notations.update({ str(i//50) : i })

    def move(self, _from: str, to: str):
        _x, _y = _from[0], _from[1]
        x, y = self.notations[_x.lower()], self.notations[_y]

        if (x, y) in self.board.pieces.values():
            piece = list(self.board.pieces.keys())[list(self.board.pieces.values()).index((x, y))]
            self.board.movePiece = piece

            toX, toY = self.notations[to[0].lower()], self.notations[to[1]]
            self.board.updatePos((toX, toY))
        self.board.draw()

    def randomMoves(self, selfPlay=False):
        if (self.side == "W") == self.board.turn or selfPlay:
            if selfPlay: 
                sleep(.3)
                self.switchSide()

            self.pieces = [piece for piece in self.board.pieces if piece[1] == self.side]

            piece = random.choice(self.pieces)
            self.board.movePiece = piece

            self.board.pieceRoutes = self.board.rules.moveRule(self.board.movePiece)
            if len(self.board.pieceRoutes) < 0: self.randomMoves()

            self.board.updatePos(random.choice(self.board.pieceRoutes))

    def switchSide(self):
        # if the player wants the bot to selfplay
        self.side = "B" if self.side == "W" else "W"

    def evaluateBoard(self):
        # function to get total value of player's piece (higher is better)
        totalValues = 0
        for piece in self.board.pieces:
            totalValues += self.values[piece[0]] \
                           if piece[1] == self.side else -self.values[piece[0]]

        return totalValues
    
    def makeMove(self, piece, position):
        self.history.append((piece, self.board.pieces[piece]))
        self.board.pieces[piece] = position

    def undoMove(self):
        piece, position = self.history.pop()
        self.board.pieces[piece] = position

    def minimax(self, piece, depth, maximize): 
        # credit https://www.youtube.com/watch?v=l-hh51ncgDI
        if depth == 0: return (None, self.evaluateBoard()) 
        
        bestMove = None
        moves = set(self.board.rules.moveRule(piece))
        self.board.pieceRoutes = moves

        if maximize:
            maxEval = -float("inf")
            for move in moves:
                if self.board.pieces[piece] == move or \
                   (move in self.board.pieces.values() and\
                       move not in self.board.rules.takes): continue
                self.makeMove(piece, move)

                _, eval = self.minimax(piece, depth-1, False)
                if eval > maxEval:
                    maxEval = eval
                    bestMove = move

                self.undoMove()
            return bestMove, maxEval

        else: 
            minEval = float("inf")
            for move in moves:
                if self.board.pieces[piece] == move or \
                   (move in self.board.pieces.values() and\
                       move not in self.board.rules.takes): continue

                self.makeMove(piece, move)

                _, eval = self.minimax(piece, depth-1, True)
                if eval < minEval:
                    minEval = eval
                    bestMove = move

                self.undoMove()
            return bestMove, minEval

    def play(self, stepsAhead=3, selfPlay=False):
        if (self.side == "W") == self.board.turn:
            bestMove = (None, None)
            maxEval = -float("inf")
            self.pieces = [piece for piece in self.board.pieces.keys() if piece[1] == self.side]
            
            for piece in self.pieces:
                move, eval = self.minimax(piece, stepsAhead, True)
                
                if eval > maxEval:
                    maxEval = eval
                    bestMove = (piece, move)

            self.board.movePiece = bestMove[0]
            self.board.pieceRoutes = self.board.rules.moveRule(bestMove[0])

            self.board.updatePos(bestMove[1])
            
            if selfPlay:
                sleep(.3) 
                self.switchSide()