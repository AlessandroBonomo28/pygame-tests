import pygame

from model.dama import *
width = 800
height = 500

cell_width = height/8
start_x_board = 0
start_y_board = 0

bgColor = (255,255,255)
evenCellColor = (128,128,128)
oddCellColor = (255,255,255)
bgLogColor = (0,0,0,128)
redPiecesColor = (255,0,0)
blackPiecesColor = (0,0,0)
colorSelectedPiece = (0,255,0)
suggestedMoveColor = (255,128,128)

piecesRadius = cell_width//2 -10
selectedPieceRadius = piecesRadius +2.5
selectedPieceStroke = 5
selectedPiece = None
msBlinkSelector = 500
ticksLastBlinkSelector = 0

suggestedMoves = None

time_elapsed_ms = 0

def mousePositionToCell(position):
	return (position[0]//cell_width, position[1]//cell_width)


def drawPieces(board : Board): # draw red circle or black circle
	for piece in board.hashMapPieces.values():
		if piece is None:
			continue
		if piece.color == PieceColor.RED:
			pygame.draw.circle(canvas,redPiecesColor,((piece.position[0]+0.5)*cell_width,(piece.position[1]+0.5)*cell_width), piecesRadius)
		else:
			pygame.draw.circle(canvas,blackPiecesColor,((piece.position[0]+0.5)*cell_width,(piece.position[1]+0.5)*cell_width), piecesRadius)		
		if piece.is_dama:
			pygame.draw.circle(canvas,(255,255,0),((piece.position[0]+0.5)*cell_width,(piece.position[1]+0.5)*cell_width), piecesRadius//2)

def drawCircleAroundSelectedPiece():
	global selectedPiece, ticksLastBlinkSelector
	if selectedPiece != None and (pygame.time.get_ticks() - ticksLastBlinkSelector) > msBlinkSelector:
		pygame.draw.circle(canvas,colorSelectedPiece,((selectedPiece.position[0]+0.5)*cell_width,(selectedPiece.position[1]+0.5)*cell_width), selectedPieceRadius,selectedPieceStroke)
		if (pygame.time.get_ticks() - ticksLastBlinkSelector) > 2*msBlinkSelector:
			ticksLastBlinkSelector = pygame.time.get_ticks()

def drawMovesForSelectedPiece():
	if selectedPiece and suggestedMoves:
		for move in suggestedMoves:
			pygame.draw.circle(canvas,suggestedMoveColor,((move.position_to[0]+0.5)*cell_width,(move.position_to[1]+0.5)*cell_width), selectedPieceRadius,selectedPieceStroke)

def clickedAnyAviableMove(position):
	global suggestedMoves
	if suggestedMoves:
		for move in suggestedMoves:
			if move.position_to == position:
				return move
	return None

pygame.init()
font = pygame.font.SysFont('Comic Sans MS', 30)
# CREATING CANVAS
canvas = pygame.display.set_mode((width,height))

# TITLE OF CANVAS
pygame.display.set_caption("Dama 2023")

text_x, text_y = 8*cell_width + (width -8*cell_width)//2, 25
text = font.render('Testing', True, colorSelectedPiece, bgLogColor)
 

textRect = text.get_rect()
#textRect.x = text_x
#textRect.y = text_y
textRect.center = (text_x, text_y)

exit = False


p1_red = Piece((1,1),PieceColor.RED,False)
p2_black = Piece((4,4),PieceColor.BLACK,False)
"""
board = Board([p1_red,
	       	  Piece((2,1),PieceColor.RED,False),
			  Piece((3,3),PieceColor.RED,False),],
			  
			  [p2_black,
      		   Piece((7,7),PieceColor.BLACK,False),
	  ])

"""

board = Board([
	       	  Piece((5,5),PieceColor.RED,False),
			  Piece((6,6),PieceColor.RED,False),],
			  
			  [
      		   Piece((7,7),PieceColor.BLACK,False),
	  ])

while not exit:	
	time_elapsed_ms += pygame.time.Clock().tick(60)
	canvas.fill(bgColor)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			exit = True
		if event.type == pygame.MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()
			ticksLastBlinkSelector = pygame.time.get_ticks() - msBlinkSelector
			cellPosition = mousePositionToCell(pos)
			move = clickedAnyAviableMove(cellPosition)
			
			if selectedPiece and move!= None:
				board.makeMove(move)
				print(f"Turn count: {board.turn_count}")
				print(f"Game status: {board.status}")
				time_elapsed_s = time_elapsed_ms//1000
				time_elapsed_m = time_elapsed_s//60
				time_elapsed_h = time_elapsed_m//60
				print(f"Time elapsed: {time_elapsed_h} h {time_elapsed_m} m {time_elapsed_s} s")
				selectedPiece = None
				suggestedMoves = None
			else:
				selectedPiece = board.getPieceByPosition(cellPosition)
				if selectedPiece and selectedPiece.color == board.whoMoves():
					suggestedMoves = selectedPiece.evaluateMovePositions(board)
				else:
					selectedPiece = None
					suggestedMoves = None
			
			try:
				last_move = board.moves[len(board.moves)-1]
				if last_move.does_eat and last_move.piece.color == board.whoMoves():
					selectedPiece = last_move.piece
					suggestedMoves = selectedPiece.evaluateMovePositions(board)
					# filtra mosse che mangiano
					suggestedMoves = list(filter(lambda move: move.does_eat, suggestedMoves))
			except:
				pass
			
	for i in range(board.width):
		for j in range(board.height):
			if (i+j)%2 == 0:
				pygame.draw.rect(canvas,oddCellColor,((start_x_board+i)*cell_width,j*cell_width,cell_width,cell_width))
			else:
				pygame.draw.rect(canvas,evenCellColor,((i+start_x_board)*cell_width,j*cell_width,cell_width,cell_width))
	drawPieces(board)
	if selectedPiece:
		drawCircleAroundSelectedPiece()
		drawMovesForSelectedPiece()
	pygame.draw.rect(canvas,bgLogColor,(height,0,width-height,height))
	canvas.blit(text, textRect)
	pygame.display.update()

