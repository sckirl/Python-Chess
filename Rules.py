class Rules:
    def __init__(self, pieces, side):
        self.pieces = pieces
        self.side = side

        self.takes = []
        self.castleCoords = []
        
    def moveRule(self, name):
        x, y = self.pieces[name] # get the coord of the piece

        # put all of the rules/routes in a dictionary
        self.rules = { 
            "p" : [(x, y+50)] if name[1] != self.side else [(x, y-50)],
            "k" : [(xn, yn) for xn in range(x-50, x+100, 50) \
                  for yn in range(y-50, y+100, 50) if -50 < xn < 400 and  -50 < yn < 400],

            "r" : [], # rook to queen have to be filled with its own 
            "b" : [], # function, for reasons like time complexity and
            "n" : [], # to run a separate algorithm just to fill the rule
            "q" : []
            }

        def pawn():
            # pawn first move (2 squares ahead)
            if y == 50 and name[1] != self.side and (x, y+50) not in self.pieces.values(): 
                self.rules["p"].append((x, y+100))
            elif y == 300 and name[1] == self.side and (x, y-50) not in self.pieces.values(): 
                self.rules["p"].append((x, y-100))

        values = list(self.pieces.values())
        values.remove((x, y))
        
        bishopMoves = [(x+i, y+i) for i in range(-400, 400, 50)] + \
                      [(x+i, y-i) for i in range(-400, 400, 50)]
        
        def rook(_x, _y):
            # run a flood fill algorithm to fill the rook and bishop rule/routes
            # this is to prevent the rook and bishop to "jump" over other pieces

            if not (-50 < _x and _x < 400) or\
               not (-50 < _y and _y < 400): return
               
            # make sure to not run this if the current chosen piece is not rook or queen
            # and ONLY process if the _x and _y is a straight line either horizontal or vertical
            if (name[0] in "rq") and \
                (_x == x or _y == y) and \
                (_x, _y) not in self.rules["r"]:
                
                # fill the possible piece takes along the way of rook's route
                if (_x, _y) in values: 
                    # make sure the rook can only take opponent's side
                    # and this also prevent the program to revisit visited route.
                    piece = list(self.pieces.keys())[list(self.pieces.values()).index((_x, _y))]
                    if piece[1] != name[1]: self.takes.append((_x, _y))
                    return 

                # when values get through all of the filters, make it into route
                self.rules["r"].append((_x, _y))
                # recursively call other positions (if not clear, check for flood fill algo)
                rook(_x+50, _y)
                rook(_x-50, _y)
                rook(_x, _y+50)
                rook(_x, _y-50)
            return

        def bishop(_x, _y):
            # same principle as rook, but instead of up-down and right-left, its diagonal
            if not (-50 < _x and _x < 400) or\
               not (-50 < _y and _y < 400): return

            # bishopMoves list contains all possible movements of bishop
            # the filter will only pick possible movements
            if (name[0] in "bq") and \
                (_x, _y) in bishopMoves and \
                (_x, _y) not in self.rules["b"]:

                if (_x, _y) in values: 
                    piece = list(self.pieces.keys())[list(self.pieces.values()).index((_x, _y))]
                    if piece[1] != name[1]: self.takes.append((_x, _y))
                    return 

                self.rules["b"].append((_x, _y))
                bishop(_x+50, _y+50)
                bishop(_x+50, _y-50)
                bishop(_x-50, _y-50)
                bishop(_x-50, _y+50)
            return
        
        def knight():
            # knight has a very specific and unique moves, and it can also 
            # jump over pieces. So it doesn't need flood fill.
            # this approach also runs on O(n) time (instead of possibly O(4n))
            knights = []
            for i in range(-50, 100, 50):
                knights.append((x-i, y-i*2))
                knights.append((x-i*2, y-i))
                knights.append((x-i*2, y+i))
                knights.append((x-i, y+i*2))

            for (_x, _y) in knights:
                if  (0 <= _x and _x < 400) and \
                    (0 <= _y and _y < 400): self.rules["n"].append((_x, _y))

        pawn()
        bishop(x, y)
        rook(x, y)
        knight()
        self.castle(name)

        # queen is basically (and in this implementation, literally) just 
        # rook and bishop movements combined
        self.rules["q"] = self.rules["b"] + self.rules["r"]
        
        self.rules[name[0]].append((x, y))
        self.canTake(name, self.rules[name[0]])
        # take is a part of move
        self.rules[name[0]] += self.takes
        return self.rules[name[0]]

    def canTake(self, name, routes):
        # function to fill the self.takes list
        # specifically for pawn, knight and king. (listing possible takes)
        blocks = set(routes).intersection(set(self.pieces.values()))
        
        if name[0] == "p":
            x, y = routes[-1]
            
            blocks = [(x-50, y-50), (x+50, y-50)]
            if name[1] != self.side: blocks = [(x-50, y+50), (x+50, y+50)]
        
        for route in blocks:
            if route not in self.pieces.values(): continue
            piece = list(self.pieces.keys())[list(self.pieces.values()).index(route)]
            if piece[1] != name[1]: 
                self.takes.append(route)

    def promotion(self, name):
        # promote the pawn when hitting the opponent's last grid
        
        if name[0] == "p" and (self.pieces[name][1] == 350 \
            or self.pieces[name][1] == 0):
                totalQueen = len([queen for queen in self.pieces.keys() if queen[:2] == "q%s"%(name[1])])

                self.pieces.update({"q%s%i"%(name[1], totalQueen) : self.pieces[name]})
                self.pieces.pop(name)

    def castle(self, name):
        # is the king 
        if name[0] == "k" and self.pieces[name][0] == 200: 

            for x, y, z in [(100, self.pieces[name][1], -100), (300, self.pieces[name][1], 50)]:
                if (x-50, y) in self.pieces.values(): continue
                try:
                    piece = list(self.pieces.keys())[list(self.pieces.values()).index((x+z, y))]
                    if piece[:2] == "r%s"%(name[1]):
                        self.castleCoords.append((x, y))
                        self.rules["k"].append((x, y))
                except: pass
                        
        # move the rook
        if self.pieces[name] in self.castleCoords and name[0] == "k":
            for num in [50, -100]:

                rook = (self.pieces[name][0]+num, self.pieces[name][1])
                if rook in self.pieces.values():
                    num = 50 if num > 0 else -50
                    nearbyRook = list(self.pieces.keys())[list(self.pieces.values()).index(rook)]
                    self.pieces.update({ nearbyRook : (self.pieces[name][0]-num, self.pieces[name][1]) })

            self.castleCoords.clear()