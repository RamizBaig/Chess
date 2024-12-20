import pygame
pygame.init()

SCREEN_WIDTH = 800
SCREEN_LENGTH = SCREEN_WIDTH*3/4 # 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_LENGTH))
pygame.display.set_caption("Chess")

enPassantable = None
checkmated=False
stalemated=False
promote=False
gameRunning=True
playerTurn = "l"
hasMoved = {"lleft": False, "lright": False, "dleft": False, "dright": False}
size = 8
legalMoves = set()
activeChecks = set()
pieceImages = {
    "lr": pygame.transform.scale(pygame.image.load("whiteRook.png"), (50, 50)),
    "lh": pygame.transform.scale(pygame.image.load("whiteHorse.png"), (50, 50)),
    "lb": pygame.transform.scale(pygame.image.load("whiteBishop.png"), (50, 50)),
    "lq": pygame.transform.scale(pygame.image.load("whiteQueen.png"), (50, 50)),
    "lk": pygame.transform.scale(pygame.image.load("whiteKing.png"), (50, 50)),
    "lp": pygame.transform.scale(pygame.image.load("whitePawn.png"), (50, 50)),
    "dr": pygame.transform.scale(pygame.image.load("blackRook.png"), (50, 50)),
    "dh": pygame.transform.scale(pygame.image.load("blackHorse.png"), (50, 50)),
    "db": pygame.transform.scale(pygame.image.load("blackBishop.png"), (50, 50)),
    "dq": pygame.transform.scale(pygame.image.load("blackQueen.png"), (50, 50)),
    "dk": pygame.transform.scale(pygame.image.load("blackKing.png"), (50, 50)),
    "dp": pygame.transform.scale(pygame.image.load("blackPawn.png"), (50, 50)),
}
board = [
        ["dr","dh","db","dq","dk","db","dh","dr"],
        ["dp","dp","dp","dp","dp","dp","dp","dp"],
        [None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None],
        [None,"lb",None,None,None,"lq",None,None],
        ["lp","lp","lp","lp","lp","lp","lp","lp"],
        ["lr","lh","lb","lq","lk","lb","lh","lr"]
    ]
board = [
        [None,None,None,None,None,None,None,"dk"],
        ["lr",None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None],
        ["lr",None,None,None,None,None,None,None],
        ["lp","lp","lp","lp","lp","lp","lp","lp"],
        ["lr","lh","lb","lq","lk","lb","lh","lr"]
    ]
hasMoved = {"lleft": False, "lright": False, "dleft": True, "dright": True}

viewingMove = False
pieceSelected = ()

def drawBoard():
    color = ((196, 195, 159), (21, 64, 62))# light and dark
    pygame.draw.rect(screen, (36, 51, 30),pygame.Rect(190, 115, 420, 420))
    for i in range(size):
        for j in range(size):
            pygame.draw.rect(screen, color[(i+j)%2],pygame.Rect(200+j*50, 125+i*50, 50, 50))

def drawPieces():
    global pieceImages
    for i in range(size):
        for j in range(size):
            if (board[i][j]!=None):
                screen.blit(pieceImages.get(board[i][j]), (200+j*50,125+i*50))

def drawViewMoves():
    for var in legalMoves:
        pygame.draw.circle(screen, (120,120,120), (225+var[1]*50,150+var[0]*50), 9)

def isKingInCheck(kingPos):
    global pieceSelected
    originalPieceSelected = pieceSelected
    for i in range(size):
        for j in range(size):
            if board[i][j] and board[i][j][0] != playerTurn: 
                
                pieceSelected = (i, j)
                findLegalMoves()  
                if kingPos in legalMoves:
                    pieceSelected = originalPieceSelected
                    return True
    pieceSelected = originalPieceSelected 
    return False

def filterLegalMoves():
    global pieceSelected
    piece = board[pieceSelected[0]][pieceSelected[1]]
    originalPos = pieceSelected
    player = piece[0]

    kingPos = None
    for i in range(size):
        for j in range(size):
            if board[i][j] and board[i][j][0] == player and board[i][j][1] == 'k':
                kingPos = (i, j)
                break
        if kingPos:
            break

    safe_moves = set()
    for move in list (legalMoves):
        targetPiece = board[move[0]][move[1]] # place to be potentailly captured
        board[move[0]][move[1]] = piece # capture plcae
        board[originalPos[0]][originalPos[1]] = None 

        if piece[1] == "k": 
            kingPos = move # move king cords to new place
            if not isKingInCheck(kingPos):
                if abs(originalPos[1] - move[1]) == 2:
                    kingPos = (originalPos[0], (originalPos[1] + move[1]) / 2)
                    if not isKingInCheck(kingPos) and not isKingInCheck(originalPos):
                        safe_moves.add(move)
                else: 
                    safe_moves.add(move)
        else:
            if not isKingInCheck(kingPos):
                safe_moves.add(move)
        board[originalPos[0]][originalPos[1]] = piece
        board[move[0]][move[1]] = targetPiece

    pieceSelected = originalPos
    legalMoves.clear()
    legalMoves.update(safe_moves)

def checkMate():
    global checkmated, stalemated, pieceSelected
    orignalPieceSelected = pieceSelected
    kingPos = None
    for i in range(size):
        for j in range(size):
            if (board[i][j] and board[i][j][0]==playerTurn):
                pieceSelected = (i,j)
                if board[i][j][1] == "k": 
                    kingPos = pieceSelected
                findLegalMoves()
                filterLegalMoves()
                if legalMoves: 
                    legalMoves.clear()
                    pieceSelected = orignalPieceSelected
                    return False
    pieceSelected = orignalPieceSelected
    if isKingInCheck(kingPos):
        checkmated=True
    else:
        stalemated=True

def findLegalMoves():
    legalMoves.clear()
    piece = board[pieceSelected[0]][pieceSelected[1]]
    row, col = pieceSelected
    match piece[1]:
        case "r" | "b" | "q" | "k" | "h":
            vectors = {"r": ((1,0), (0,1), (-1, 0), (0,-1)), 
                       "b": ((1,1), (1,-1), (-1,1), (-1,-1)), 
                       "q": ((1,0), (0,1), (-1, 0), (0,-1),(1,1),(1,-1),(-1,1),(-1,-1)),
                       "k": ((1,0), (0,1), (-1, 0), (0,-1),(1,1),(1,-1),(-1,1),(-1,-1)),
                       "h": ((1,2), (2,1), (-1,-2), (-2,-1),(-1,2),(-2,1),(1,-2),(2,-1))}
            max = 8
            if piece[1] == "k" or piece[1] == "h":
                max = 2

            for vec in (vectors.get(piece[1])):
                for i in range(1, max):        
                    if (not (0 <= row+i*vec[0] < 8 and 0 <= col+i*vec[1] < 8)):
                        break
                    target = board[row+i*vec[0]][col+i*vec[1]]

                    if (not target):
                        legalMoves.add((row+i*vec[0], col+i*vec[1]))
                    elif (target[0] != piece[0]):
                        legalMoves.add((row+i*vec[0],col+i*vec[1]))
                        break
                    else: 
                        break
            if piece[1] == "k":
                if not hasMoved.get(piece[0]+"right"):
                    if not board[pieceSelected[0]][pieceSelected[1]+2] and not board[pieceSelected[0]][pieceSelected[1]+1]:
                        legalMoves.add((pieceSelected[0],pieceSelected[1]+2))
                if not hasMoved.get(piece[0]+"left"):
                    if not board[pieceSelected[0]][pieceSelected[1]-3] and not board[pieceSelected[0]][pieceSelected[1]-2] and not board[pieceSelected[0]][pieceSelected[1]-1]:
                        legalMoves.add((pieceSelected[0],pieceSelected[1]-2))
        case "p":
            direction = -1 if piece[0] == "l" else 1  
            startRow = 6 if piece[0] == "l" else 1  
            if row + direction in range(8) and not board[row + direction][col]:
                legalMoves.add((row + direction, col))
                if row==startRow and not board[row+direction*2][col]:
                    legalMoves.add((row+direction*2,col))
                
            for offset in (-1, 1):  
                if col + offset in range(8):
                    target = board[row + direction][col + offset] if row + direction in range(8) else None
                    if target and target[0] != piece[0]:  
                        legalMoves.add((row + direction, col + offset))
                    elif enPassantable == (row, col + offset):  
                        legalMoves.add((row + direction, col + offset))
        
while (gameRunning):
    screen.fill((30,30,30))
    
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            gameRunning=False            
    
        if not checkmated and not promote:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                pos = ((pos[1]-25)//50-2, pos[0]//50-4)
                if (pos[0] > 7 or pos[0] < 0 or pos[1] > 7 or pos[1] < 0):
                    legalMoves.clear()
                    continue
                
                if viewingMove:
                    if ((pos[0],pos[1]) in legalMoves):
                        piece = board[pieceSelected[0]][pieceSelected[1]]                        
                        if piece[1]=="p":
                            if enPassantable and enPassantable[0] == pos[0]- (-1 if playerTurn == "l" else 1) and enPassantable[1]==pos[1]:
                                board[enPassantable[0]][enPassantable[1]]=None

                            enPassantable = pos if piece[1] == "p" and abs(pos[0]-pieceSelected[0])==2 else None

                            if pos[0] == 0 or pos[0] == 7:
                                promote=True

                        if piece[1] == "k":
                            hasMoved[piece[0]+"left"] = True
                            hasMoved[piece[0]+"right"] = True
                            if (pos[1]-pieceSelected[1]==2):
                                board[pos[0]][pos[1]-1] = board[pos[0]][pos[1]+1]
                                board[pos[0]][pos[1]+1] = None

                            if (pos[1]-pieceSelected[1]==-2):
                                board[pos[0]][pos[1]+1] = board[pos[0]][pos[1]-2]
                                board[pos[0]][pos[1]-2] = None

                        if piece[1] == "r":
                            if pieceSelected[1]==7:
                                hasMoved[piece[0]+"right"] = True
                            if pieceSelected[1]==0:
                                hasMoved[piece[0]+"left"] = True
                        board[pos[0]][pos[1]] = board[pieceSelected[0]][pieceSelected[1]]
                        board[pieceSelected[0]][pieceSelected[1]] = None
                        
                        if piece[1] != "p" or abs(pos[0] - pieceSelected[0]) != 2:
                            enPassantable = None

                        pieceSelected=(pos[0],pos[1])
                        viewingMove = False
                        legalMoves.clear()
                        playerTurn = "d" if playerTurn == "l" else "l"
                        checkMate()
                    elif (board[pos[0]][pos[1]] and board[pos[0]][pos[1]][0] == playerTurn and pos!=pieceSelected):
                        pieceSelected = pos
                        findLegalMoves()
                        filterLegalMoves()
                    else: 
                        viewingMove = False
                        legalMoves.clear()
                else:
                    if (board[pos[0]][pos[1]]):
                        if board[pos[0]][pos[1]][0] == playerTurn:
                            viewingMove = True
                            pieceSelected = pos
                            findLegalMoves()
                            filterLegalMoves()
            
        drawBoard()
        drawPieces()
        drawViewMoves()
        if promote:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                pos = ((pos[1]-25)//50-2, pos[0]//50-4)
                color = "d" if playerTurn == "l" else "l"
                promotion_pieces = {2: "q", 3: "r", 4: "b", 5: "h"}
                if pos[0] == -2 and pos[1] in promotion_pieces:
                    board[pieceSelected[0]][pieceSelected[1]] = color + promotion_pieces[pos[1]]
                    promote = False
                    checkMate()
                    
            screen.blit(pieceImages.get(color+"q"), (300,25))
            screen.blit(pieceImages.get(color+"r"), (350,25))
            screen.blit(pieceImages.get(color+"b"), (400,25))
            screen.blit(pieceImages.get(color+"h"), (450,25))

        if checkmated:
            pygame.draw.rect(screen, (120,120,120),pygame.Rect(0,0,800,50))
            font = pygame.font.Font(None, 50)
            name = font.render("CHECKMATE", True, (255,255,255))
            screen.blit(name, (400-name.get_width()//2, 15))
            
        if stalemated:
            pygame.draw.rect(screen, (120,120,220),pygame.Rect(0,0,800,50))
            font = pygame.font.Font(None, 50)
            name = font.render("STALEMATE", True, (255,255,255))
            screen.blit(name, (400-name.get_width()//2, 15))
        pygame.display.update()


pygame.quit()


