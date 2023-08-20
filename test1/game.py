import pygame

from model.dama import *
width = 800
height = 500

cell_width = height/8
start_x_board = 0
start_y_board = 0
text_spacing = cell_width//2

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

msBlinkSelector = 500
ticksLastBlinkSelector = 0

selectedPiece = None
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

textColor = (255,255,255)
def drawTextGameStatus():
	text_x, text_y = 8*cell_width + (width -8*cell_width)//2, 35
	textTurnColor = (255,0,0) if board.whoMoves() == PieceColor.RED else (0,255,0)
	textTurn = f"Turn {board.turn_count+1}: {board.whoMoves().lower()} moves"
	if board.status != GameStatus.IN_PROGRESS:
		textTurn = "Game Over !"
		textTurnColor = (255,255,255)
	text = fontTurn.render(textTurn, True, textTurnColor, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y)
	canvas.blit(text, textRect)

	
	time_elapsed_s = (time_elapsed_ms//1000) 
	time_elapsed_m = (time_elapsed_s//60)
	time_elapsed_h = time_elapsed_m//60
	timer_txt = f"Time elapsed: {time_elapsed_h} h {time_elapsed_m%60} m {time_elapsed_s%60} s"

	text = normalText.render(timer_txt, True, textColor, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing)
	canvas.blit(text, textRect)

	if board.status == GameStatus.IN_PROGRESS or board.status == GameStatus.DRAW:
		status_text_color = (255,255,255)
	else:
		status_text_color = (255,0,0) if board.status == GameStatus.RED_WINS else (0,255,0)
	text = normalText.render(f"Game status: {board.status.lower()}!", True, status_text_color, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*2)
	canvas.blit(text, textRect)

	text = normalText.render(f"Red score: {board.red_score}", True, textColor, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*3)
	canvas.blit(text, textRect)

	text = normalText.render(f"Black score: {board.black_score}", True, textColor, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*4)
	canvas.blit(text, textRect)

	reset_color = (255,255,255) if board.status == GameStatus.IN_PROGRESS else (0,255,0)
	text = normalText.render(f"Press R to reset", True, reset_color, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*5)
	canvas.blit(text, textRect)

	text = normalText.render(f"Press M to toggle music", True, textColor, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*6)
	canvas.blit(text, textRect)

def drawPreviousMove():
	previous_move = board.moves[-1] if len(board.moves) > 0 else None
	if previous_move:
		# draw arrow
		pygame.draw.line(canvas,(0,0,255),((previous_move.position_from[0]+0.5)*cell_width,(previous_move.position_from[1]+0.5)*cell_width),((previous_move.position_to[0]+0.5)*cell_width,(previous_move.position_to[1]+0.5)*cell_width),5)
	
def clickedAnyAviableMove(position):
	global suggestedMoves
	if suggestedMoves:
		for move in suggestedMoves:
			if move.position_to == position:
				return move
	return None

pygame.init()

audio_enabled = True
pygame.mixer.init()
pygame.mixer.music.load('loop.mp3')
pygame.mixer.music.play(-1)

fontTurn = pygame.font.SysFont('Comic Sans MS', 25)
normalText = pygame.font.SysFont('Comic Sans MS', 20)
# CREATING CANVAS
# resizable window

#canvas = pygame.display.set_mode((width,height))
canvas = pygame.display.set_mode((width,height),pygame.RESIZABLE)

# TITLE OF CANVAS
pygame.display.set_caption("Dama 2023")

exit = False
RED_AI_enabled = True
BLACK_AI_enabled = True
auto_reset = True
AI_delay_ms = 500

black_pieces = []
red_pieces = []
for i in range(3):
	for j in range(8):
		if (i+j)%2 == 0:
			red_pieces.append(Piece((j,i),PieceColor.RED,False))
			black_pieces.append(Piece((7-j,7-i),PieceColor.BLACK,False))

board = Board(red_pieces,black_pieces)
"""
# draw configuration
board = Board([
	       	  Piece((5,5),PieceColor.RED,False),
			  Piece((6,6),PieceColor.RED,False),],
			  
			  [
      		   Piece((7,7),PieceColor.BLACK,False),
	  ])
"""
while not exit:	
	if board.status == GameStatus.IN_PROGRESS:
		time_elapsed_ms += pygame.time.Clock().tick(60)
	canvas.fill(bgColor)

	if board.status == GameStatus.IN_PROGRESS:
		if board.whoMoves() == PieceColor.RED and RED_AI_enabled:
			# AI RED
			board.makeMoveRedAI()
			selectedPiece = None
			suggestedMoves = None
			pygame.time.delay(AI_delay_ms)
			time_elapsed_ms += AI_delay_ms
			
		elif board.whoMoves() == PieceColor.BLACK and BLACK_AI_enabled:
			# AI BLACK
			board.makeMoveBlackAI()
			selectedPiece = None
			suggestedMoves = None
			pygame.time.delay(AI_delay_ms)
			time_elapsed_ms += AI_delay_ms
	elif auto_reset:
		pygame.time.delay(5000)
		board.reset()
		time_elapsed_ms = 0
		selectedPiece = None
		suggestedMoves = None
	
	for event in pygame.event.get():
		# if resized window
		if event.type == pygame.VIDEORESIZE:
			width = event.w
			height = event.h
			cell_width = height/8
			start_x_board = 0
			start_y_board = 0
			text_spacing = cell_width*0.7
			fontTurn = pygame.font.SysFont('Comic Sans MS', int(cell_width*0.5))
			normalText = pygame.font.SysFont('Comic Sans MS', int(cell_width*0.35))
			piecesRadius = cell_width//2 -10
			selectedPieceRadius = piecesRadius +2.5
			canvas = pygame.display.set_mode((width,height),pygame.RESIZABLE)
		
		if event.type == pygame.QUIT:
			exit = True
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				exit = True
			if event.key == pygame.K_r:
				print("Reset game")
				board.reset()
				time_elapsed_ms = 0
				selectedPiece = None
				suggestedMoves = None
				break
			if event.key == pygame.K_m:
				audio_enabled = not audio_enabled
				if audio_enabled:
					pygame.mixer.music.unpause()
				else:
					pygame.mixer.music.pause()
		if event.type == pygame.MOUSEBUTTONUP and board.whoMoves() == PieceColor.BLACK and not BLACK_AI_enabled:
			pos = pygame.mouse.get_pos()

			if board.status != GameStatus.IN_PROGRESS:
				break
			
			ticksLastBlinkSelector = pygame.time.get_ticks() - msBlinkSelector
			cellPosition = mousePositionToCell(pos)
			move = clickedAnyAviableMove(cellPosition)
			
			if selectedPiece and move != None:
				board.makeMove(move)
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
	drawPreviousMove()
	if selectedPiece:
		drawCircleAroundSelectedPiece()
		drawMovesForSelectedPiece()
	pygame.draw.rect(canvas,bgLogColor,(height,0,width-height,height))

	drawTextGameStatus()

	pygame.display.update()

