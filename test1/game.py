import pygame

from model.dama import *

pygame.init()

evenCellColor = (128,128,128)
oddCellColor = (255,255,255)

# CREATING CANVAS
canvas = pygame.display.set_mode((500,500))

# TITLE OF CANVAS
pygame.display.set_caption("Dama 2023")

# get width and height of canvas
width = canvas.get_width()
height = canvas.get_height()

image = pygame.image.load("character.jpg")
exit = False


p1_red = Piece((0,0),PieceColor.RED)
p2_black = Piece((7,7),PieceColor.BLACK)

board = Board([p1_red],[p2_black])
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
	canvas.fill((255,255,255))
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			exit = True
	for i in range(board.width):
		for j in range(board.height):
			if (i+j)%2 == 0:
				pygame.draw.rect(canvas,oddCellColor,(i*50,j*50,50,50))
			else:
				pygame.draw.rect(canvas,evenCellColor,(i*50,j*50,50,50))
	
	pygame.display.update()
