"""
ChessAI.py: Chứa trí tuệ nhân tạo sử dụng Minimax & Alpha-Beta Pruning.
"""
import random

# Điểm số quân cờ
pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000 
STALEMATE = 0

def findBestMove(gs, validMoves):
    """Hàm chính gọi từ Main"""
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    
    # Độ sâu = 2 (Có thể tăng lên 3 nếu máy mạnh)
    findMoveNegaMaxAlphaBeta(gs, validMoves, 2, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    return nextMove

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        
        # Đệ quy
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        
        gs.undoMove()
        
        if score > maxScore:
            maxScore = score
            if depth == 2: # Lưu nước đi ở tầng ngoài cùng
                nextMove = move
        
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
            
    return maxScore

def scoreBoard(gs):
    """Đánh giá bàn cờ: Dương là Trắng lợi, Âm là Đen lợi"""
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE # Trắng bị chiếu hết -> Đen thắng
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score