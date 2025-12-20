import random

# Điểm vật chất (Material)
pieceScore = {"K": 0, "Q": 900, "R": 500, "B": 330, "N": 320, "p": 100}

# --- BẢNG ĐIỂM VỊ TRÍ (Mới) ---
# Điểm thưởng cho từng vị trí trên bàn cờ (Góc nhìn của quân Trắng)
# Quân Đen sẽ dùng bảng này nhưng đảo ngược lại.

knightScores = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

bishopScores = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]
]

queenScores = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 1, 2, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1]
]

rookScores = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 2, 2, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4]
]

pawnScores = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 5, 5, 5, 5, 5, 5, 5],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [0, 0, 0, 2, 2, 0, 0, 0],
    [0, 0, 0, 1, 1, 0, 0, 0],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, -2, -2, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

# Tổng hợp các bảng điểm vào Dictionary
piecePositionScores = {"N": knightScores, "B": bishopScores, "Q": queenScores, "R": rookScores, "p": pawnScores}

CHECKMATE = 1000
STALEMATE = 0
# tim buoc di tot nhat
def findBestMove(gs, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves) # tron nuoc di tranh AI luon di giong nhau
    findMoveNegaMaxAlphaBeta(gs, validMoves, 2, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    return nextMove #tra ve nuoc di tot nhat tim duoc

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        gs.undoMove()
        
        if score > maxScore:
            maxScore = score
            if depth == 2:
                nextMove = move
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

def scoreBoard(gs):
    """
    Hàm đánh giá thông minh hơn: Vật chất + Vị trí
    """
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                pieceType = square[1]
                
                # 1. Tính điểm vật chất cơ bản
                pieceValue = pieceScore[pieceType]
                
                # 2. Tính điểm vị trí (Chỉ áp dụng cho các quân có trong bảng)
                if pieceType != 'K': # Vua chưa cần bảng điểm phức tạp ở level này
                    if square[0] == 'w': # Quân Trắng
                        positionValue = piecePositionScores[pieceType][row][col]
                        score += pieceValue + positionValue * 10 # Nhân 10 để ưu tiên vị trí
                    else: # Quân Đen (Đọc bảng ngược lại)
                        positionValue = piecePositionScores[pieceType][7-row][col]
                        score -= pieceValue + positionValue * 10
    return score

def findRandomMove(validMoves):
    if len(validMoves) > 0:
        return validMoves[random.randint(0, len(validMoves) - 1)]
    return None