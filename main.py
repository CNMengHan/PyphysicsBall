import pygame
import random
import sys
import math
import time

pygame.init()

WIDTH = 1200
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ciallo~(∠・ω< )⌒★")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
RED = (255, 50, 50)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(10, 40)
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.speed_y = 0
        self.speed_x = random.uniform(-3, 3)
        self.gravity = 0.5
        self.bounce_factor = 0.7
        self.dragging = False
        self.last_mouse_pos = None
        self.mass = self.radius * self.radius
        self.velocity_damping = 0.997
        self.min_speed = 0.1
        self.is_special = random.random() < 0.05  
        if self.is_special:
            self.color = GOLD
        self.merge_count = 0  
        
    def start_drag(self, pos):
        self.dragging = True
        self.last_mouse_pos = pos
        self.speed_x = 0
        self.speed_y = 0
    
    def update_drag(self, pos):
        if self.dragging:
            self.x, self.y = pos
            if self.last_mouse_pos:
                dx = pos[0] - self.last_mouse_pos[0]
                dy = pos[1] - self.last_mouse_pos[1]
                self.speed_x = dx * 0.3
                self.speed_y = dy * 0.3
            self.last_mouse_pos = pos
    
    def end_drag(self):
        self.dragging = False
        self.last_mouse_pos = None

    def collide_with(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance_sq = dx * dx + dy * dy
        min_distance = self.radius + other.radius
        
        if distance_sq < min_distance * min_distance:
            distance = (distance_sq) ** 0.5
            
            if distance < 0.01:
                self.x += random.uniform(-0.1, 0.1)
                self.y += random.uniform(-0.1, 0.1)
                return
            
            nx = dx / distance
            ny = dy / distance
            
            rel_vx = self.speed_x - other.speed_x
            rel_vy = self.speed_y - other.speed_y
            rel_v_normal = rel_vx * nx + rel_vy * ny
            
            if rel_v_normal > 0:
                return
            
            restitution = 0.8
            j = -(1 + restitution) * rel_v_normal
            j /= 1/self.mass + 1/other.mass
            
            if abs(j) < 0.01:
                return
            
            self.speed_x += (j * nx) / self.mass
            self.speed_y += (j * ny) / self.mass
            other.speed_x -= (j * nx) / other.mass
            other.speed_y -= (j * ny) / other.mass
            
            percent = 0.8
            slop = 0.01
            penetration = min_distance - distance
            if penetration > slop:
                correction = (penetration - slop) / distance * percent
                correction_x = nx * correction
                correction_y = ny * correction
                mass_ratio1 = self.mass / (self.mass + other.mass)
                mass_ratio2 = other.mass / (self.mass + other.mass)
                self.x += correction_x * mass_ratio2
                self.y += correction_y * mass_ratio2
                other.x -= correction_x * mass_ratio1
                other.y -= correction_y * mass_ratio1

    def update(self):
        if not self.dragging:
            self.speed_y += self.gravity
            self.speed_x *= self.velocity_damping
            self.speed_y *= self.velocity_damping
            if abs(self.speed_x) < self.min_speed:
                self.speed_x = 0
            if abs(self.speed_y) < self.min_speed and abs(self.y + self.radius - HEIGHT) < 1:
                self.speed_y = 0
            
            self.x += self.speed_x
            self.y += self.speed_y
            
            if self.y + self.radius > HEIGHT:
                self.y = HEIGHT - self.radius
                self.speed_y = -self.speed_y * self.bounce_factor
                self.speed_x *= 0.95
                
            if self.x - self.radius < 0:
                self.x = self.radius
                self.speed_x = -self.speed_x * self.bounce_factor
            elif self.x + self.radius > WIDTH:
                self.x = WIDTH - self.radius
                self.speed_x = -self.speed_x * self.bounce_factor

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def explode(self, balls):
        if not self.is_special:
            return

        for _ in range(8):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(5, 10)
            new_ball = Ball(self.x, self.y)
            new_ball.radius = self.radius * 0.5
            new_ball.speed_x = speed * math.cos(angle)
            new_ball.speed_y = speed * math.sin(angle)
            new_ball.color = RED
            balls.append(new_ball)
    
    def merge_with(self, other):

        if (abs(self.speed_x) < 1 and abs(self.speed_y) < 1 and
            abs(other.speed_x) < 1 and abs(other.speed_y) < 1):
            dx = self.x - other.x
            dy = self.y - other.y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < (self.radius + other.radius) * 0.5:
                return True
        return False

def apply_force_field(balls, mouse_pos, pushing):

    force_strength = 4.0 if pushing else -4.0  
    min_force = 0.5  
    
    for ball in balls:
        dx = ball.x - mouse_pos[0]
        dy = ball.y - mouse_pos[1]
        distance = max((dx * dx + dy * dy) ** 0.5, 1)  
        
        force = max(force_strength / (distance * 0.1), min_force)
        if pushing:
            force = min(force, 8.0)  
        else:
            force = max(-8.0, -force)  
        
        angle = math.atan2(dy, dx)
        mass_factor = (40 / ball.radius) ** 0.5  
        ball.speed_x += force * math.cos(angle) * mass_factor
        ball.speed_y += force * math.sin(angle) * mass_factor


def main():
    clock = pygame.time.Clock()
    balls = []
    selected_ball = None
    font = pygame.font.Font("msyh.ttf", 36)
    spawn_rate = 0.05
    min_spawn_rate = 0.02  
    spawn_rate_decrease = 0.0001  
    last_click_time = 0
    pushing = True  
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  
                    current_time = time.time()
                    if current_time - last_click_time < 0.3:
                        mouse_pos = pygame.mouse.get_pos()
                        clear_radius = 100
                        balls = [ball for ball in balls if 
                                ((ball.x - mouse_pos[0])**2 + 
                                 (ball.y - mouse_pos[1])**2) > clear_radius**2]
                    last_click_time = current_time
                    for ball in balls:
                        dx = mouse_pos[0] - ball.x
                        dy = mouse_pos[1] - ball.y
                        if (dx*dx + dy*dy) <= ball.radius*ball.radius:
                            selected_ball = ball
                            ball.start_drag(mouse_pos)
                            break
                    else:  
                        balls.append(Ball(mouse_pos[0], mouse_pos[1]))
                
                elif event.button == 3:  
                    pushing = not pushing  
            
            if event.type == pygame.MOUSEBUTTONUP and selected_ball:
                selected_ball.end_drag()
                selected_ball = None
        
        if selected_ball:
            selected_ball.update_drag(mouse_pos)
        
        if random.random() < spawn_rate:
            size_category = random.random()
            if size_category < 0.7:  
                radius = random.randint(10, 20)
            elif size_category < 0.9:  
                radius = random.randint(21, 30)
            else:  
                radius = random.randint(31, 40)
            
            spawn_x = random.randint(0, WIDTH)
            new_ball = Ball(spawn_x, -40)  
            new_ball.radius = radius
            new_ball.mass = radius * radius
            balls.append(new_ball)
            spawn_rate = max(min_spawn_rate, spawn_rate - spawn_rate_decrease)
        
        balls = [ball for ball in balls if ball.y < HEIGHT + 100]  
        for ball in balls:
            ball.update()
        
        for _ in range(3):
            for i in range(len(balls)):
                for j in range(i + 1, len(balls)):
                    balls[i].collide_with(balls[j])
        
        if pygame.mouse.get_pressed()[2]:  
            apply_force_field(balls, pygame.mouse.get_pos(), pushing)
        
        i = 0
        while i < len(balls):
            j = i + 1
            while j < len(balls):
                if balls[i].merge_with(balls[j]):
                    new_radius = (balls[i].radius**3 + balls[j].radius**3)**(1/3)
                    balls[i].radius = new_radius
                    balls[i].mass = new_radius * new_radius
                    balls[i].merge_count += balls[j].merge_count + 1
                    if balls[i].merge_count > 0:
                        balls[i].color = (
                            min(255, balls[i].color[0] + 20),
                            min(255, balls[i].color[1] + 20),
                            min(255, balls[i].color[2] + 20)
                        )
                    balls.pop(j)
                else:
                    j += 1
            i += 1
        
        for ball in balls[:]:
            if ball.is_special and ball.y + ball.radius > HEIGHT:
                ball.explode(balls)
                balls.remove(ball)
        
        screen.fill(BLACK)
        for ball in balls:
            ball.draw(screen)
            if ball.dragging:
                pygame.draw.line(screen, WHITE, (ball.x, ball.y), mouse_pos, 2)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
