"""
ChessMain.py: Giao diện người dùng nâng cấp.
"""
import pygame as p
import ChessEngine
import ChessAI

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        try:
            IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        except FileNotFoundError:
            print(f"Lỗi: Thiếu ảnh 'images/{piece}.png'")

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Cờ Vua AI - Highlight Upgrade") # Đặt tên cửa sổ
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False 

    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    
    playerOne = True  # Trắng (Người)
    playerTwo = False # Đen (Máy)
    
    gameOver = False # Cờ hiệu kết thúc game

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            
            # --- XỬ LÝ CLICK CHUỘT ---
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn: # Chỉ click được khi chưa Game Over
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    
                    if sqSelected == (row, col): 
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 1 and gs.board[row][col] == "--":
                         sqSelected = ()
                         playerClicks = []

                    elif len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                sqSelected = () 
                                playerClicks = []
                                break
                        if not moveMade:
                            playerClicks = [sqSelected]
            
            # Phím tắt: Ấn 'z' để Undo (đi lại)
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    gameOver = False # Nếu undo thì game chưa kết thúc

        # --- XỬ LÝ AI ---
        if not gameOver and not humanTurn and not moveMade:
            aiMove = ChessAI.findBestMove(gs, validMoves)
            if aiMove is None:
                aiMove = ChessAI.findRandomMove(validMoves) # Fallback nếu Minimax lỗi
            
            if aiMove is not None: # Kiểm tra lại cho chắc
                gs.makeMove(aiMove)
                moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        # Vẽ giao diện
        drawGameState(screen, gs, validMoves, sqSelected)
        
        # Kiểm tra kết thúc game để hiện chữ
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Den Thang! (Black Wins)")
            else:
                drawText(screen, "Trang Thang! (White Wins)")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Hoa Co! (Stalemate)")

        p.display.flip()
        clock.tick(MAX_FPS)

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected) # <--- Hàm Highlight mới
    drawPieces(screen, gs.board)

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, gs, validMoves, sqSelected):
    """
    Tô màu ô đang chọn và các nước đi hợp lệ
    """
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): # Đảm bảo chọn đúng quân mình
            # 1. Tô màu ô đang chọn (Màu xanh dương nhạt)
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # Độ trong suốt (0-255)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            
            # 2. Tô màu các ô có thể đi tới (Màu vàng nhạt)
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
    
    # 3. Highlight nước đi cuối cùng (của Máy hoặc Người)
    if len(gs.moveLog) > 0:
        lastMove = gs.moveLog[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green')) # Màu xanh lá
        screen.blit(s, (lastMove.startCol*SQ_SIZE, lastMove.startRow*SQ_SIZE))
        screen.blit(s, (lastMove.endCol*SQ_SIZE, lastMove.endRow*SQ_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                if piece in IMAGES:
                    screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawText(screen, text):
    """Vẽ chữ thông báo kết quả ra giữa màn hình"""
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()