import pygame,random,math
from classes.particles import ParticleHandler
from classes.animation import Animation
class Plane:
    
    particle_handler : ParticleHandler = None
    explosion_sprite_group : pygame.sprite.Group = None
    explosion_sound : pygame.mixer.Sound = None
    @staticmethod
    def set_particle_handler(handler):
        Plane.particle_handler = handler

    @staticmethod
    def set_explosion_group(group):
        Plane.explosion_sprite_group = group

    @staticmethod
    def set_explosion_sound(sound):
        Plane.explosion_sound = sound
    
    def __init__(self,pos,sprite,name,health=100,velocity=[0,0],erraticness=0.015):
        self.sign = 1
        self.sprite = sprite
        self.velocity = velocity
        self.is_dead = False
        self.health = health
        self.pos = pos
        self.name = name
        self.erraticness = erraticness
        
    
    def update(self):
        if self.is_dead:
            return
        off = 100
        
        height = pygame.display.get_surface().get_height()
        if self.pos[1] > height - off:
            self.sign = -self.sign
            self.pos[1] = height - off

        if self.pos[1] < off:
            self.sign = -self.sign
            self.pos[1] = off
        
        self.pos[1] += self.velocity[1]*self.sign
        
        self.pos[1] +=  math.sin(pygame.time.get_ticks()*self.erraticness)*(self.velocity[1]*0.6)

    def damage(self,amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        if self.is_dead:
            return
        self.is_dead = True
        self.health = 0
        # explosion animation
        Plane.explosion_sprite_group.add(Animation(self.pos[0],self.pos[1],"data/images/explosion",3,200))
        Plane.explosion_sound.play()

    def draw(self,screen):
        if self.is_dead:
            return
        screen.blit(self.sprite, [ self.pos[0] - self.sprite.get_width()//2, self.pos[1] - self.sprite.get_width()//2])
        px = self.pos[0]
        py = self.pos[1]
        vel = [ self.velocity[0],0]
        Plane.particle_handler.add_particle( [px, py+ self.sprite.get_width()//6], vel, random.randint(4, 8))
        Plane.particle_handler.add_particle( [px, py- self.sprite.get_width()//6], vel, random.randint(4, 8))
        