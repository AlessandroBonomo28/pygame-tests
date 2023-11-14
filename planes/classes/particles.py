import pygame
class ParticleHandler:
    # [loc, velocity, timer]
    particles : list[any]
    time_step : int

    def __init__(self) -> None:
        self.particles = []
        pass
    # [[px, py], [vx,vy], timer])
    def add_particle(self, loc, velocity, timer, image=None):
        self.particles.append([loc, velocity, timer,image])

    def update(self):
        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.1
            #particle[1][1] += 0.4 # gravity
            if particle[2] <= 0:
                self.particles.remove(particle)
    def draw(self,screen):
        for particle in self.particles:
            if particle[3]:
                screen.blit(particle[3], (particle[0][0]  - particle[3].get_height()//2, particle[0][1]- particle[3].get_height()//2))
            else:
                pygame.draw.circle(screen, (255, 255, 255), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))


