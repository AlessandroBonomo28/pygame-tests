import pygame,random,math
from classes.particles import ParticleHandler
class Plane:
    
    particle_handler : ParticleHandler = None
    @staticmethod
    def set_particle_handler(handler):
        Plane.particle_handler = handler

    def __init__(self,pos,sprite,name,health=100,velocity=[0,0]):
        self.sprite = sprite
        self.velocity = velocity
        self.is_dead = False
        self.health = health
        self.pos = pos
        self.name = name
        
    
    def update(self):
        dy = pygame.mouse.get_pos()[1] - self.pos[1]
        off = 150
        if abs(dy) < 250:
            self.pos[1] -= (dy/25 ) +  math.cos(pygame.time.get_ticks()*0.2)
        else:
            self.pos[1] += ( math.cos(pygame.time.get_ticks()*0.002))
        
        self.pos[1] +=  math.sin(pygame.time.get_ticks()*0.01)
        
        self.pos[1] = max(off,self.pos[1])
        height = pygame.display.get_surface().get_height()
        self.pos[1] = min(height- off,self.pos[1])

    def damage(self,amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        self.is_dead = True
        self.health = 0

    def draw(self,screen):
        screen.blit(self.sprite, [ self.pos[0] - self.sprite.get_width()//2, self.pos[1] - self.sprite.get_width()//2])
        px = self.pos[0]
        py = self.pos[1]
        Plane.particle_handler.add_particle( [px, py+ self.sprite.get_width()//6], self.velocity, random.randint(4, 8))
        Plane.particle_handler.add_particle( [px, py- self.sprite.get_width()//6], self.velocity, random.randint(4, 8))
        