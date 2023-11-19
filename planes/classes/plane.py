import pygame,random,math
from classes.particles import ParticleHandler
from classes.animation import Animation
class Plane:
    heavy = [
        "UK Lancaster",
        "US b17",
    ]
    light = [
        "GER bf109",
        "GER FW190",
        "JAP a6m",
        "JAP Ki61",
        "UK Spitfire",
        "UK typhoon",
        "US p40",
        "US p51",
        "USSR La5",
        "USSR Lagg3",
        "US p38",
        "JAP Ki51",
    ]
    @staticmethod
    def is_heavy(name):
        return name in Plane.heavy

    def is_light(name):
        return name in Plane.light

    particle_handler : ParticleHandler = None
    explosion_sprite_group : pygame.sprite.Group = None
    damage_sound : pygame.mixer.Sound = None
    final_explosion_sound : pygame.mixer.Sound = None
    font = None
    def __init__(self,pos,sprite,name,health=100,velocity=[0,0],erraticness=0.015,damage_stages = 3):
        self.max_health = health
        self.damage_stages = damage_stages
        self.disturb_timer = 0
        self.sign = 1
        self.sprite = sprite
        self.velocity = velocity
        self.is_dead = False
        self.health = health
        self.pos = pos
        self.name = name
        self.erraticness = erraticness
        self.oscillation_offset = random.randint(0,1000)
        
    

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
        
        
        self.pos[1] +=  math.sin(pygame.time.get_ticks()*self.erraticness + self.oscillation_offset)*(self.velocity[1]*0.6)

        if self.disturb_timer > 0:
            self.pos[0] += math.cos(pygame.time.get_ticks()*self.erraticness*3)*(self.velocity[0]/2)
            self.disturb_timer -= 0.1

    def damage(self,amount):
        if self.is_dead:
            return
        level = self.get_damage_level()
        self.health -= amount
        new_level = self.get_damage_level()
        if level != new_level and new_level < self.damage_stages:
            self.__apply_level_damage()
        if self.health <= 0:
            self.die()

    def die(self):
        if self.is_dead:
            return
        self.is_dead = True
        self.health = 0
        # explosion animation
        Plane.explosion_sprite_group.add(Animation(self.pos[0],self.pos[1],"data/images/explosion",3,200))
        pygame.mixer.Sound.play(Plane.final_explosion_sound)
    
    
    def draw_plane_name(self,screen):
        text = Plane.font.render(self.name, True, (255,0,0))
        screen.blit(text, [ self.pos[0] - text.get_width() -20, self.pos[1] - text.get_width()])
    
    def draw(self,screen):
        if self.is_dead:
            return
        
        screen.blit(self.sprite, [ self.pos[0] - self.sprite.get_width()//2, self.pos[1] - self.sprite.get_width()//2])
        px = self.pos[0]
        py = self.pos[1]
        vel = [ self.velocity[0],0]
        Plane.particle_handler.add_particle( [px, py+ self.sprite.get_width()//6], vel, random.randint(4, 8))
        Plane.particle_handler.add_particle( [px, py- self.sprite.get_width()//6], vel, random.randint(4, 8))
        self.__draw_smoke()
        self.draw_plane_name(screen)
    
    

    v_smoke_speed = -0.5
    h_smoke_speed = -0.5
    offsets = [
        [-50,0],
        [0,30],
        [0,-30],
    ]
    def get_damage_level(self):
        return int((self.health/self.max_health)*(self.damage_stages+1))
    
    def __apply_level_damage(self):
        index = min(self.get_damage_level(),2)
        explosion_pos = [self.pos[0] + Plane.offsets[index][0], self.pos[1]+ Plane.offsets[index][1]]
         # explosion animation
        Plane.explosion_sprite_group.add(Animation(explosion_pos[0],explosion_pos[1],"data/images/explosion",3,120))
        pygame.mixer.Sound.play(Plane.damage_sound)
        self.disturb_timer = 2

    def __draw_smoke(self):
        for i in range(self.damage_stages-self.get_damage_level()):
            smoke_pos = [self.pos[0] + Plane.offsets[i][0], self.pos[1]+ Plane.offsets[i][1]]
            Plane.particle_handler.add_particle( smoke_pos, [Plane.h_smoke_speed, Plane.v_smoke_speed], random.randint(6, 9),color=(50,50,50))
            Plane.particle_handler.add_particle( smoke_pos,[Plane.h_smoke_speed, Plane.v_smoke_speed], random.randint(3, 7),color=(255,100,0))
            Plane.particle_handler.add_particle( smoke_pos, [Plane.h_smoke_speed, Plane.v_smoke_speed], random.randint(2, 6),color=(255,200,0))