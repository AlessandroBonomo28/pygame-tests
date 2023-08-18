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

# CREATING CANVAS
canvas = pygame.display.set_mode((width,height))

# TITLE OF CANVAS
pygame.display.set_caption("Dama 2023")


image = pygame.image.load("character.jpg")
exit = False


p1_red = Piece((0,2),PieceColor.RED,True)
p2_black = Piece((7,7),PieceColor.BLACK,True)

board = Board([p1_red,Piece((0,0),PieceColor.RED,False)],[p2_black])
print(board.getPieceByPosition((0,0)))
print(board.getPieceByPosition((7,7)))
#board.eatPiece(p1,p2)
print(board.getPieceByPosition((0,0)))
print(board.getPieceByPosition((7,7)))

board.printHashmap()
print("p1 red")
p1_red.printAviableMoves(board)
print("p2 black")
p2_black.printAviableMoves(board)


while not exit:	
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
				print(move)
				board.makeMove(move)
				selectedPiece = None
				suggestedMoves = None
				break

			selectedPiece = board.getPieceByPosition(cellPosition)
			if selectedPiece:
				suggestedMoves = selectedPiece.evaluateMovePositions(board)
			else:
				suggestedMoves = None
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
	pygame.display.update()

