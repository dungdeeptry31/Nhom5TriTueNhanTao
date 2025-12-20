"""
ChessMain.py: Giao diện người dùng (GUI) và Vòng lặp chính.
Chịu trách nhiệm: Hiển thị hình ảnh, bắt sự kiện chuột/phím, gọi AI.
"""
import pygame as p
import ChessEngine
import ChessAI

# Cấu hình cửa sổ game
WIDTH = HEIGHT = 512
DIMENSION = 8 # Bàn cờ 8x8
SQ_SIZE = HEIGHT // DIMENSION # Kích thước 1 ô cờ
MAX_FPS = 15
IMAGES = {}

def loadImages():
    """Tải ảnh quân cờ từ thư mục 'images/' vào bộ nhớ"""
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        try:
            # Load ảnh và scale cho vừa kích thước ô cờ
            IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        except FileNotFoundError:
            print(f"Lỗi: Thiếu ảnh 'images/{piece}.png'")

def main():
    """Hàm Main: Vòng lặp chính của trò chơi"""
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Cờ Vua AI")
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    
    # Khởi tạo trạng thái bàn cờ
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # Biến cờ: Đánh dấu đã có nước đi mới được thực hiện

    loadImages() # Tải ảnh một lần duy nhất
    
    running = True
    sqSelected = ()     # Lưu ô cờ người chơi click lần cuối (row, col)
    playerClicks = []   # Lưu danh sách 2 lần click (đi từ đâu -> đến đâu)
    
    # Cấu hình người chơi
    playerOne = True  # Trắng = Người chơi
    playerTwo = False # Đen = Máy (AI)
    
    gameOver = False # Trạng thái kết thúc game

    while running:
        # Xác định xem hiện tại có phải lượt người chơi không
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            
            # --- XỬ LÝ CLICK CHUỘT CỦA NGƯỜI CHƠI ---
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn: # Chỉ cho click khi chưa Game Over và đến lượt người
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    
                    if sqSelected == (row, col): # Nếu click lại vào ô đã chọn -> Hủy chọn
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    # Logic xử lý click:
                    # 1. Nếu mới click 1 lần vào ô trống -> Bỏ qua
                    if len(playerClicks) == 1 and gs.board[row][col] == "--":
                         sqSelected = ()
                         playerClicks = []

                    # 2. Nếu đã click đủ 2 lần (Chọn quân -> Chọn đích đến)
                    elif len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        
                        # Kiểm tra xem nước đi có hợp lệ không
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i]) # Thực hiện nước đi trên bàn cờ ảo
                                moveMade = True
                                sqSelected = () # Reset click
                                playerClicks = []
                                break
                        if not moveMade:
                            # Nếu nước đi không hợp lệ, coi như chọn lại quân mới
                            playerClicks = [sqSelected]
            
            # --- XỬ LÝ PHÍM TẮT ---
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # Phím 'z' để Undo
                    gs.undoMove()
                    moveMade = True
                    gameOver = False

        # --- XỬ LÝ AI (MÁY TÍNH) ---
        if not gameOver and not humanTurn and not moveMade:
            # Gọi hàm tìm nước đi tốt nhất từ ChessAI
            aiMove = ChessAI.findBestMove(gs, validMoves)
            if aiMove is None:
                aiMove = ChessAI.findRandomMove(validMoves) # Fallback: Đi ngẫu nhiên nếu AI lỗi
            
            if aiMove is not None:
                gs.makeMove(aiMove)
                moveMade = True

        # Nếu có nước đi mới, cần tính lại danh sách nước đi hợp lệ cho lượt sau
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        # --- VẼ GIAO DIỆN ---
        drawGameState(screen, gs, validMoves, sqSelected)
        
        # Kiểm tra kết thúc game để hiện thông báo
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
    """Hàm vẽ toàn bộ trạng thái game (Bàn cờ -> Highlight -> Quân cờ)"""
    drawBoard(screen) # Vẽ ô trắng đen
    highlightSquares(screen, gs, validMoves, sqSelected) # Vẽ màu đánh dấu
    drawPieces(screen, gs.board) # Vẽ quân cờ lên trên cùng

def drawBoard(screen):
    """Vẽ bàn cờ vua"""
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, gs, validMoves, sqSelected):
    """
    Tô màu các ô đặc biệt:
    1. Ô đang được chọn (Xanh dương).
    2. Các ô có thể đi tới (Vàng).
    3. Nước đi vừa thực hiện (Xanh lá).
    """
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): # Chỉ highlight nếu chọn đúng quân mình
            # 1. Tô màu ô đang chọn
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # Độ trong suốt (0-255)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            
            # 2. Tô màu các ô có thể đi tới
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
    
    # 3. Highlight nước đi cuối cùng (Last Move)
    if len(gs.moveLog) > 0:
        lastMove = gs.moveLog[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green')) 
        screen.blit(s, (lastMove.startCol*SQ_SIZE, lastMove.startRow*SQ_SIZE))
        screen.blit(s, (lastMove.endCol*SQ_SIZE, lastMove.endRow*SQ_SIZE))

def drawPieces(screen, board):
    """Vẽ quân cờ lên bàn cờ dựa trên trạng thái hiện tại"""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # Nếu không phải ô trống
                if piece in IMAGES:
                    screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawText(screen, text):
    """Vẽ chữ thông báo kết quả ra giữa màn hình"""
    font = p.font.SysFont("Helvitca", 32, True, False)
    # Vẽ bóng của chữ (màu xám)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    # Vẽ chữ chính (màu đen) lệch một chút để tạo hiệu ứng nổi
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()