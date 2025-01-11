import pygame
import random
import sys
import math
import time

pygame.init()

infoObject = pygame.display.Info()
WIDTH = infoObject.current_w - 100  
HEIGHT = infoObject.current_h - 100  
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.NOFRAME)
pygame.display.set_caption("Ciallo~(∠・ω< )⌒★")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
RED = (255, 50, 50)

def safe_operation(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {str(e)}")
            return None
    return wrapper

class Ball:
    gravity_scale = 1.0
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(10, 40)
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.speed_y = 0
        self.speed_x = random.uniform(-3, 3)
        self.base_gravity = 0.5
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

    @safe_operation
    def collide_with(self, other):
        if not other or not isinstance(other, Ball):
            return
            
        try:
            dx = self.x - other.x
            dy = self.y - other.y
            distance_sq = dx * dx + dy * dy
            min_distance = self.radius + other.radius
            if distance_sq < min_distance * min_distance:
                distance = max(0.0001, (distance_sq) ** 0.5)  
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
                j /= max(0.0001, 1/self.mass + 1/other.mass)  
                
                if abs(j) < 0.01:
                    return
                
                self.speed_x = max(min(self.speed_x + (j * nx) / self.mass, 1000), -1000)  
                self.speed_y = max(min(self.speed_y + (j * ny) / self.mass, 1000), -1000)
                other.speed_x = max(min(other.speed_x - (j * nx) / other.mass, 1000), -1000)
                other.speed_y = max(min(other.speed_y - (j * ny) / other.mass, 1000), -1000)
                percent = 0.8
                slop = 0.01
                penetration = min_distance - distance
                if penetration > slop:
                    correction = (penetration - slop) / distance * percent
                    correction_x = nx * correction
                    correction_y = ny * correction
                    mass_sum = self.mass + other.mass
                    mass_ratio1 = self.mass / mass_sum if mass_sum > 0 else 0.5
                    mass_ratio2 = other.mass / mass_sum if mass_sum > 0 else 0.5
                    self.x += correction_x * mass_ratio2
                    self.y += correction_y * mass_ratio2
                    other.x -= correction_x * mass_ratio1
                    other.y -= correction_y * mass_ratio1
        except Exception as e:
            print(f"Collision error: {str(e)}")

    @safe_operation
    def update(self, time_scale=1.0):
        try:
            time_scale = max(0.1, min(time_scale, 2.0))  
            if not self.dragging:
                self.speed_y += self.base_gravity * Ball.gravity_scale * time_scale
                self.speed_x *= self.velocity_damping
                self.speed_y *= self.velocity_damping
                self.speed_x = max(min(self.speed_x, 1000), -1000)
                self.speed_y = max(min(self.speed_y, 1000), -1000)
                if abs(self.speed_x) < self.min_speed:
                    self.speed_x = 0
                if abs(self.speed_y) < self.min_speed and abs(self.y + self.radius - HEIGHT) < 1:
                    self.speed_y = 0
                
                self.x += self.speed_x * time_scale
                self.y += self.speed_y * time_scale
                
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
        except Exception as e:
            print(f"Update error: {str(e)}")

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

class Slider:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_rect = pygame.Rect(x, y, 10, height + 4)  
        self.dragging = False
        self.value = 0.5  
        self.update_handle()
    
    def update_handle(self):
        self.handle_rect.centerx = self.rect.x + self.rect.width * self.value
        self.handle_rect.centery = self.rect.centery  
    
    @safe_operation
    def handle_event(self, event):
        try:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.handle_rect.collidepoint(event.pos):
                    self.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.width))
                self.value = rel_x / self.rect.width
                self.update_handle()
        except Exception as e:
            print(f"Slider error: {str(e)}")
    
    def draw(self, screen):
        pygame.draw.rect(screen, (70, 70, 70), self.rect)  
        pygame.draw.rect(screen, (180, 180, 180), self.handle_rect)  


class CloseButton:
    def __init__(self):
        self.size = 20  
        self.padding = 10  
        self.rect = pygame.Rect(WIDTH - self.size - self.padding, self.padding, self.size, self.size)
        self.is_hovered = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()
    
    def draw(self, screen):
        if self.is_hovered:
            color = (255, 255, 255)  
            width = 2  
        else:
            color = (150, 150, 150)  
            width = 1  
        
        x, y = self.rect.topleft
        size = self.size
        margin = size * 0.3  
        start_pos1 = (x + margin, y + margin)
        end_pos1 = (x + size - margin, y + size - margin)
        start_pos2 = (x + size - margin, y + margin)
        end_pos2 = (x + margin, y + size - margin)
        pygame.draw.line(screen, color, start_pos1, end_pos1, width)
        pygame.draw.line(screen, color, start_pos2, end_pos2, width)

def main():
    try:
        clock = pygame.time.Clock()
        balls = []
        selected_ball = None
        font = pygame.font.Font("msyh.ttf", 36)
        spawn_rate = 0.05
        min_spawn_rate = 0.02  
        spawn_rate_decrease = 0.0001  
        last_click_time = 0
        pushing = True  
        time_slider = Slider(20, 20, 150, 3)  
        gravity_slider = Slider(20, 40, 150, 3)  
        gravity_slider.value = 0.2  
        base_time_scale = 1.0
        close_button = CloseButton()
        while True:
            try:
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
                    
                    time_slider.handle_event(event)  
                    gravity_slider.handle_event(event)  
                    close_button.handle_event(event)
                
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
                
                max_balls = 200
                if len(balls) > max_balls:
                    balls = balls[:max_balls]
                
                time_scale = 0.1 + (time_slider.value * 1.9)
                time_scale = max(0.1, min(time_scale, 2.0))
                Ball.gravity_scale = gravity_slider.value * 5.0
                balls = [ball for ball in balls if ball.y < HEIGHT + 100]
                for ball in balls:
                    if ball and isinstance(ball, Ball):
                        ball.update(time_scale)
                

                if len(balls) < 100:  
                    iterations = 3
                else:
                    iterations = 1
                    
                for _ in range(iterations):
                    for i in range(len(balls)):
                        for j in range(i + 1, len(balls)):
                            if balls[i] and balls[j]:
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
                
                time_slider.draw(screen)  
                gravity_slider.draw(screen)  
                close_button.draw(screen)
                
                pygame.display.flip()
                clock.tick(60)
            except Exception as e:
                print(f"Main loop error: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Program error: {str(e)}")
        pygame.quit()
        sys.exit(1)
