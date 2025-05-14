import pygame
import random
import sys
import time
import os
import math
import json

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# High score file path
HIGH_SCORE_FILE = 'high_score.json'

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
LIME = (0, 255, 0)
BROWN = (165, 42, 42)

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

# Create images directory if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# Food colors and shapes
FOOD_TYPES = [
    {'color': RED, 'shape': 'circle'},
    {'color': BLUE, 'shape': 'square'},
    {'color': YELLOW, 'shape': 'triangle'},
    {'color': PURPLE, 'shape': 'diamond'},
    {'color': ORANGE, 'shape': 'star'},
    {'color': PINK, 'shape': 'circle'},
    {'color': CYAN, 'shape': 'square'},
    {'color': MAGENTA, 'shape': 'triangle'},
    {'color': LIME, 'shape': 'diamond'},
    {'color': BROWN, 'shape': 'star'},
    {'color': RED, 'shape': 'circle'},
    {'color': BLUE, 'shape': 'square'}
]

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Border
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class PauseButton:
    def __init__(self):
        self.rect = pygame.Rect(WINDOW_WIDTH - 50, 10, 40, 40)
        self.is_paused = False
        self.color = GRAY
        self.hover_color = LIGHT_GRAY
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Draw pause/play symbol
        if self.is_paused:
            # Play symbol (triangle)
            points = [
                (self.rect.x + 15, self.rect.y + 10),
                (self.rect.x + 15, self.rect.y + 30),
                (self.rect.x + 30, self.rect.y + 20)
            ]
            pygame.draw.polygon(surface, BLACK, points)
        else:
            # Pause symbol (two rectangles)
            pygame.draw.rect(surface, BLACK, (self.rect.x + 12, self.rect.y + 10, 6, 20))
            pygame.draw.rect(surface, BLACK, (self.rect.x + 22, self.rect.y + 10, 6, 20))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                self.is_paused = not self.is_paused
                return True
        return False

class Snake:
    def __init__(self):
        self.reset()

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        if new in self.positions[3:]:
            return False
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True

    def reset(self):
        self.length = 1
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = GREEN
        self.score = 0
        self.last_color_change = time.time()
        self.colors = [GREEN, BLUE, YELLOW, PURPLE, ORANGE]
        self.current_color_index = 0

    def change_color(self, new_color=None):
        if new_color is not None:
            self.color = new_color
        else:
            current_time = time.time()
            if current_time - self.last_color_change >= 30:
                self.current_color_index = (self.current_color_index + 1) % len(self.colors)
                self.color = self.colors[self.current_color_index]
                self.last_color_change = current_time

    def render(self, surface):
        for i, p in enumerate(self.positions):
            if i == 0:  # Head
                pygame.draw.rect(surface, self.color,
                               (p[0] * GRID_SIZE, p[1] * GRID_SIZE,
                                GRID_SIZE, GRID_SIZE))
                
                eye_size = GRID_SIZE // 4
                eye_offset = GRID_SIZE // 4
                
                if self.direction == UP:
                    left_eye = (p[0] * GRID_SIZE + eye_offset, p[1] * GRID_SIZE + eye_offset)
                    right_eye = (p[0] * GRID_SIZE + GRID_SIZE - eye_offset - eye_size, p[1] * GRID_SIZE + eye_offset)
                elif self.direction == DOWN:
                    left_eye = (p[0] * GRID_SIZE + eye_offset, p[1] * GRID_SIZE + GRID_SIZE - eye_offset - eye_size)
                    right_eye = (p[0] * GRID_SIZE + GRID_SIZE - eye_offset - eye_size, p[1] * GRID_SIZE + GRID_SIZE - eye_offset - eye_size)
                elif self.direction == LEFT:
                    left_eye = (p[0] * GRID_SIZE + eye_offset, p[1] * GRID_SIZE + eye_offset)
                    right_eye = (p[0] * GRID_SIZE + eye_offset, p[1] * GRID_SIZE + GRID_SIZE - eye_offset - eye_size)
                else:  # RIGHT
                    left_eye = (p[0] * GRID_SIZE + GRID_SIZE - eye_offset - eye_size, p[1] * GRID_SIZE + eye_offset)
                    right_eye = (p[0] * GRID_SIZE + GRID_SIZE - eye_offset - eye_size, p[1] * GRID_SIZE + GRID_SIZE - eye_offset - eye_size)
                
                pygame.draw.rect(surface, WHITE, (*left_eye, eye_size, eye_size))
                pygame.draw.rect(surface, WHITE, (*right_eye, eye_size, eye_size))
                
                pupil_size = eye_size // 2
                pygame.draw.rect(surface, BLACK, (left_eye[0] + pupil_size//2, left_eye[1] + pupil_size//2, pupil_size, pupil_size))
                pygame.draw.rect(surface, BLACK, (right_eye[0] + pupil_size//2, right_eye[1] + pupil_size//2, pupil_size, pupil_size))
            else:  # Body
                pygame.draw.rect(surface, self.color,
                               (p[0] * GRID_SIZE, p[1] * GRID_SIZE,
                                GRID_SIZE, GRID_SIZE))

class FoodManager:
    def __init__(self):
        self.foods = []
        self.max_foods = 50
        self.min_foods = 40
        self.initialize_foods()

    def initialize_foods(self):
        # Create initial set of foods
        for _ in range(self.max_foods):
            self.add_new_food()

    def add_new_food(self):
        # Create new food at random position
        new_food = Food()
        # Make sure new food doesn't overlap with existing foods
        while any(food.position == new_food.position for food in self.foods):
            new_food.randomize_position()
        self.foods.append(new_food)

    def update(self):
        # Update all foods
        for food in self.foods:
            food.update()

        # Check if we need to replenish foods
        if len(self.foods) <= self.min_foods:
            # Add new foods until we reach max_foods
            while len(self.foods) < self.max_foods:
                self.add_new_food()

    def render(self, surface):
        for food in self.foods:
            food.render(surface)

    def remove_food(self, position):
        # Remove food at given position
        self.foods = [food for food in self.foods if food.position != position]

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.current_food = random.choice(FOOD_TYPES)
        self.randomize_position()
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.move_counter = 0
        self.animation_frame = 0
        self.animation_speed = 10

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH-1),
                        random.randint(0, GRID_HEIGHT-1))
        self.current_food = random.choice(FOOD_TYPES)
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    def update(self):
        # Move every 30 frames
        self.move_counter += 1
        if self.move_counter >= 30:
            self.move_counter = 0
            x, y = self.direction
            new_x = (self.position[0] + x) % GRID_WIDTH
            new_y = (self.position[1] + y) % GRID_HEIGHT
            self.position = (new_x, new_y)
            
            # Randomly change direction
            if random.random() < 0.1:  # 10% chance to change direction
                self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

        # Update animation frame
        self.animation_frame = (self.animation_frame + 1) % self.animation_speed

    def render(self, surface):
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE
        color = self.current_food['color']
        shape = self.current_food['shape']

        # Add slight movement animation
        wiggle_offset = math.sin(self.animation_frame * 0.5) * 2

        if shape == 'circle':  # Ant
            # Body
            pygame.draw.circle(surface, color, (x + GRID_SIZE//2, y + GRID_SIZE//2 + wiggle_offset), GRID_SIZE//3)
            # Head
            pygame.draw.circle(surface, color, (x + GRID_SIZE//2 + GRID_SIZE//4, y + GRID_SIZE//2 + wiggle_offset), GRID_SIZE//4)
            # Antennae
            pygame.draw.line(surface, color, 
                           (x + GRID_SIZE//2 + GRID_SIZE//4, y + GRID_SIZE//2 + wiggle_offset),
                           (x + GRID_SIZE//2 + GRID_SIZE//2, y + GRID_SIZE//4 + wiggle_offset), 2)
            pygame.draw.line(surface, color,
                           (x + GRID_SIZE//2 + GRID_SIZE//4, y + GRID_SIZE//2 + wiggle_offset),
                           (x + GRID_SIZE//2 + GRID_SIZE//2, y + GRID_SIZE//2 + wiggle_offset), 2)

        elif shape == 'square':  # Mouse
            # Body
            pygame.draw.ellipse(surface, color, (x + GRID_SIZE//4, y + GRID_SIZE//4 + wiggle_offset, GRID_SIZE//2, GRID_SIZE//2))
            # Ears
            pygame.draw.circle(surface, color, (x + GRID_SIZE//4, y + GRID_SIZE//4 + wiggle_offset), GRID_SIZE//6)
            pygame.draw.circle(surface, color, (x + GRID_SIZE*3//4, y + GRID_SIZE//4 + wiggle_offset), GRID_SIZE//6)
            # Tail
            pygame.draw.line(surface, color,
                           (x + GRID_SIZE//4, y + GRID_SIZE//2 + wiggle_offset),
                           (x, y + GRID_SIZE//2 + wiggle_offset), 3)

        elif shape == 'triangle':  # Bird
            # Body
            points = [
                (x + GRID_SIZE//2, y + GRID_SIZE//4 + wiggle_offset),
                (x + GRID_SIZE//4, y + GRID_SIZE*3//4 + wiggle_offset),
                (x + GRID_SIZE*3//4, y + GRID_SIZE*3//4 + wiggle_offset)
            ]
            pygame.draw.polygon(surface, color, points)
            # Wing
            wing_points = [
                (x + GRID_SIZE//2, y + GRID_SIZE//2 + wiggle_offset),
                (x + GRID_SIZE//4, y + GRID_SIZE//2 + wiggle_offset),
                (x + GRID_SIZE//2, y + GRID_SIZE*3//4 + wiggle_offset)
            ]
            pygame.draw.polygon(surface, color, wing_points)

        elif shape == 'diamond':  # Butterfly
            # Body
            pygame.draw.line(surface, color,
                           (x + GRID_SIZE//2, y + GRID_SIZE//4 + wiggle_offset),
                           (x + GRID_SIZE//2, y + GRID_SIZE*3//4 + wiggle_offset), 2)
            # Wings
            wing_offset = math.sin(self.animation_frame * 0.5) * 3
            pygame.draw.ellipse(surface, color, (x + GRID_SIZE//4, y + GRID_SIZE//4 + wing_offset, GRID_SIZE//2, GRID_SIZE//3))
            pygame.draw.ellipse(surface, color, (x + GRID_SIZE//4, y + GRID_SIZE*5//12 + wing_offset, GRID_SIZE//2, GRID_SIZE//3))

        elif shape == 'star':  # Spider
            # Body
            pygame.draw.circle(surface, color, (x + GRID_SIZE//2, y + GRID_SIZE//2 + wiggle_offset), GRID_SIZE//3)
            # Legs
            for i in range(8):
                angle = i * math.pi / 4
                start_x = x + GRID_SIZE//2 + math.cos(angle) * GRID_SIZE//3
                start_y = y + GRID_SIZE//2 + math.sin(angle) * GRID_SIZE//3 + wiggle_offset
                end_x = start_x + math.cos(angle) * GRID_SIZE//2
                end_y = start_y + math.sin(angle) * GRID_SIZE//2
                pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), 2)

# Directional constants
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

def show_welcome_screen():
    # Create buttons
    start_button = Button(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 50, 120, 50, "Start", GREEN, LIGHT_GRAY)
    exit_button = Button(WINDOW_WIDTH//2 + 30, WINDOW_HEIGHT//2 + 50, 120, 50, "Exit", RED, LIGHT_GRAY)
    
    # Welcome text
    font = pygame.font.Font(None, 74)
    welcome_text = font.render("Welcome to Snake Game!", True, WHITE)
    welcome_rect = welcome_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if start_button.handle_event(event):
                return True
            if exit_button.handle_event(event):
                return False
        
        # Draw everything
        screen.fill(BLACK)
        screen.blit(welcome_text, welcome_rect)
        start_button.draw(screen)
        exit_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def load_high_score():
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as f:
                return json.load(f)['high_score']
    except:
        pass
    return 0

def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump({'high_score': score}, f)
    except:
        pass

def show_game_over(screen, score, high_score):
    # Create buttons
    restart_button = Button(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 50, 120, 50, "Restart", GREEN, LIGHT_GRAY)
    quit_button = Button(WINDOW_WIDTH//2 + 30, WINDOW_HEIGHT//2 + 50, 120, 50, "Quit", RED, LIGHT_GRAY)
    
    # Game over text
    font = pygame.font.Font(None, 74)
    game_over_text = font.render("Game Over!", True, WHITE)
    game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100))
    
    # Score text
    score_font = pygame.font.Font(None, 48)
    score_text = score_font.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 30))
    
    # High score text
    high_score_text = score_font.render(f"High Score: {high_score}", True, WHITE)
    high_score_rect = high_score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if restart_button.handle_event(event):
                return True
            if quit_button.handle_event(event):
                return False
        
        # Draw everything
        screen.fill(BLACK)
        screen.blit(game_over_text, game_over_rect)
        screen.blit(score_text, score_rect)
        screen.blit(high_score_text, high_score_rect)
        restart_button.draw(screen)
        quit_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def show_pause_screen():
    # Create buttons
    continue_button = Button(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 50, 120, 50, "Continue", GREEN, LIGHT_GRAY)
    exit_button = Button(WINDOW_WIDTH//2 + 30, WINDOW_HEIGHT//2 + 50, 120, 50, "Exit", RED, LIGHT_GRAY)
    
    # Pause text
    font = pygame.font.Font(None, 74)
    pause_text = font.render("Game Paused", True, WHITE)
    pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
    
    # Continue text
    continue_font = pygame.font.Font(None, 36)
    continue_text = continue_font.render("Please continue playing the game", True, WHITE)
    continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if continue_button.handle_event(event):
                return True
            if exit_button.handle_event(event):
                pygame.quit()
                sys.exit()
        
        # Draw everything
        screen.fill(BLACK)
        screen.blit(pause_text, pause_rect)
        screen.blit(continue_text, continue_rect)
        continue_button.draw(screen)
        exit_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def main():
    # Show welcome screen first
    if not show_welcome_screen():
        pygame.quit()
        sys.exit()

    # Load high score
    high_score = load_high_score()

    while True:
        snake = Snake()
        food_manager = FoodManager()
        font = pygame.font.Font(None, 36)
        game_running = True
        pause_button = PauseButton()

        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and snake.direction != DOWN:
                        snake.direction = UP
                    elif event.key == pygame.K_DOWN and snake.direction != UP:
                        snake.direction = DOWN
                    elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                        snake.direction = LEFT
                    elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                        snake.direction = RIGHT
                
                # Handle pause button
                if pause_button.handle_event(event):
                    if pause_button.is_paused:
                        show_pause_screen()
                        pause_button.is_paused = False

            if not pause_button.is_paused:
                # Update snake
                if not snake.update():
                    game_running = False
                    # Update high score if current score is higher
                    if snake.score > high_score:
                        high_score = snake.score
                        save_high_score(high_score)
                    continue

                # Update foods
                food_manager.update()

                # Check if snake ate any food
                head_pos = snake.get_head_position()
                for food in food_manager.foods[:]:  # Create a copy of the list to avoid modification during iteration
                    if food.position == head_pos:
                        snake.length += 1
                        snake.score += 10
                        snake.change_color(food.current_food['color'])
                        food_manager.remove_food(head_pos)
                        break

                # Change snake color every 30 seconds (only if not changed by eating)
                snake.change_color()

            # Draw everything
            screen.fill(BLACK)
            snake.render(screen)
            food_manager.render(screen)
            
            # Draw score, high score and food count
            score_text = font.render(f'Score: {snake.score}', True, WHITE)
            high_score_text = font.render(f'High Score: {high_score}', True, WHITE)
            food_count_text = font.render(f'Food: {len(food_manager.foods)}', True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(high_score_text, (10, 50))
            screen.blit(food_count_text, (10, 90))

            # Draw pause button
            pause_button.draw(screen)

            pygame.display.update()
            clock.tick(8)

        # Show game over screen
        if not show_game_over(screen, snake.score, high_score):
            break

if __name__ == '__main__':
    main() 
