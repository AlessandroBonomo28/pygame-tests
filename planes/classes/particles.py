import pygame
class ParticleHandler:
    # [loc, velocity, timer]
    particles : list[any]
    time_step : int

    def __init__(self) -> None:
        self.particles = []
        pass
    # [[px, py], [vx,vy], timer])
    def add_particle(self, loc, velocity, timer, image=None,tag=0,gravity=True,gravity_dir=[0,0],color=(255,255,255)):
        self.particles.append([loc, velocity, timer,image,tag,gravity,gravity_dir,color])

    def update(self):
        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.1
            if particle[5]: # if gravity is enabled
                particle[1][1] += particle[6][1]
                particle[1][0] += particle[6][0]
            if particle[2] <= 0:
                self.particles.remove(particle)
    def draw(self,screen):
        for particle in self.particles:
            if particle[3]:
                screen.blit(particle[3], (particle[0][0]  - particle[3].get_height()//2, particle[0][1]- particle[3].get_height()//2))
            else:
                pygame.draw.circle(screen, particle[7], [int(particle[0][0]), int(particle[0][1])], int(particle[2]))


