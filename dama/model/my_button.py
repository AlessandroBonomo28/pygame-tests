import pygame
class myButton:
    text : str
    position : tuple
    width : int
    height : int
    color : tuple
    text_color : tuple
    font : pygame.font
    __blink : bool
    __timer_blink : float
    __timer_blink_max : float = 500
    __timer_blink_color : tuple 
    __text_blink_color : tuple
    __original_text_color : tuple
    __original_color : tuple
    __border_stroke : int 
    __border_color : tuple 
    def __init__(self, text, position_center, color, text_color, font,blink = False, border_stroke = 2, border_color = (0,0,0), timer_blink_color = (0,255,0), text_blink_color = (0,0,0)):
        self.text = text
        self.position = position_center
        self.width = font.size(text)[0] + 20
        self.height = font.get_height() + 5
        self.__timer_blink_color = timer_blink_color
        self.__text_blink_color = text_blink_color
        self.__border_stroke = border_stroke
        self.__border_color = border_color
        self.color = color
        self.font = font
        self.text_color = text_color
        self.__original_text_color = text_color
        self.__blink = blink
        self.__original_color = color
        self.__timer_blink = 0

    def set_new_color(self, color):
        self.__original_color = color

    def draw(self, screen):
        if self.__blink and self.__timer_blink < self.__timer_blink_max:
            self.__timer_blink += pygame.time.Clock().tick(60)
        elif self.__blink and self.__timer_blink >= self.__timer_blink_max:
            self.__timer_blink = 0
            if self.color == self.__timer_blink_color:
                self.set_original_color()
            else:
                self.set_blink_color()
        else:
            self.color = self.__original_color
        pygame.draw.rect(screen, self.color, pygame.Rect(self.position[0] - self.width // 2, self.position[1] - self.height // 2, self.width, self.height))
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect()
        text_rect.center = self.position
        screen.blit(text_surface, text_rect)
        self.__draw_border(screen)

    def __draw_border(self, screen):
        pygame.draw.rect(screen, self.__border_color, pygame.Rect(self.position[0] - self.width // 2, self.position[1] - self.height // 2, self.width, self.height), self.__border_stroke)

    def set_blink_color(self):
        self.color = self.__timer_blink_color
        self.text_color = self.__text_blink_color

    def set_original_color(self):
        self.color = self.__original_color
        self.text_color = self.__original_text_color

    def set_blink(self, blink):
        self.__blink = blink
    
    def is_blinking(self):
        return self.__blink
    
    def mouse_over(self,mouse_position) -> bool:
        return self.position[0] - self.width // 2 <= mouse_position[0] <= self.position[0] + self.width // 2 and self.position[1] - self.height // 2 <= mouse_position[1] <= self.position[1] + self.height // 2
    
        

