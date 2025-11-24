import pygame
import random
from enum import Enum
from collections import namedtuple
pygame.init()
try:
    font = pygame.font.Font('arial.ttf',25)
except FileNotFoundError:
    font = pygame.font.SysFont('arial', 25)

# Reset 
# Reward
# Play(action) -> Direction
# Game_Iteration
# is_collision


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
 
Point = namedtuple('Point','x , y')

BLOCK_SIZE=20
SPEED = 20
WHITE = (255,255,255)
RED = (200,0,0)
BLUE1 = (0,0,255)
BLUE2 = (0,100,255)
BLACK = (0,0,0)

class SnakeGame:
    def __init__(self,w=640,h=480):
        self.w=w
        self.h=h
        #init display
        self.display = pygame.display.set_mode((self.w,self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        
        #init game state
        self.direction = Direction.RIGHT
        self.head = Point(self.w/2,self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE,self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE),self.head.y)]
        self.score = 0
        self.food = None
        self._place__food()

    def _place__food(self):
        x = random.randint(0,(self.w-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randint(0,(self.h-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        self.food = Point(x,y)
        if(self.food in self.snake):
            self._place__food()


    def play_step(self):
        # 1. Collect the user input
        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                pygame.quit()
                quit()
            if(event.type == pygame.KEYDOWN):
                if(event.key == pygame.K_LEFT):
                    self.direction = Direction.LEFT
                elif(event.key == pygame.K_RIGHT):
                    self.direction = Direction.RIGHT
                elif(event.key == pygame.K_UP):
                    self.direction = Direction.UP
                elif(event.key == pygame.K_DOWN):
                    self.direction = Direction.DOWN
        # 2. Move
        self._move(self.direction)
        self.snake.insert(0,self.head)

        # 3. Check if game Over
        game_over = False 
        if(self._is_collision()):
            game_over=True
            return game_over,self.score
        # 4. Place new Food or just move
        if(self.head == self.food):
            self.score+=1
            self._place__food()
        else:
            self.snake.pop()
        # 5. Update UI and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. Return game Over and Display Score
        
        return game_over,self.score

    def _update_ui(self):
        self.display.fill(BLACK)

        # Draw background "ANUJ" watermark
        bg_font = pygame.font.SysFont('arial', 72, bold=True)
        bg_text = bg_font.render("ANUJ", True, (50, 50, 50))  # Dark gray, semi-transparent effect
        text_rect = bg_text.get_rect(center=(self.w//2, self.h//2))
        self.display.blit(bg_text, text_rect)

        # Draw some alcohol glass icons on background
        self._draw_background_alcohol()

        for pt in self.snake:
            pygame.draw.rect(self.display,BLUE1,pygame.Rect(pt.x,pt.y,BLOCK_SIZE,BLOCK_SIZE))
            pygame.draw.rect(self.display,BLUE2,pygame.Rect(pt.x+4,pt.y+4,12,12))

        # Draw food as alcohol bottle with "anuj" text
        pygame.draw.rect(self.display,RED,pygame.Rect(self.food.x,self.food.y,BLOCK_SIZE,BLOCK_SIZE))

        # Draw alcohol bottle icon (simple bottle shape)
        bottle_x = self.food.x + 2
        bottle_y = self.food.y + 2
        bottle_w = BLOCK_SIZE - 4
        bottle_h = BLOCK_SIZE - 4

        # Bottle neck
        pygame.draw.rect(self.display,BLACK,pygame.Rect(bottle_x + 6, bottle_y, 8, 4))
        # Bottle body
        pygame.draw.rect(self.display,BLACK,pygame.Rect(bottle_x + 4, bottle_y + 4, 12, 10))
        # Bottle base
        pygame.draw.rect(self.display,BLACK,pygame.Rect(bottle_x + 2, bottle_y + 13, 16, 3))

        # "anuj" text in center
        food_text = font.render("anuj",True,BLACK)
        text_rect = food_text.get_rect(center=(self.food.x + BLOCK_SIZE//2, self.food.y + BLOCK_SIZE//2))
        self.display.blit(food_text, text_rect)

        text = font.render("Score: "+str(self.score),True,WHITE)
        self.display.blit(text,[0,0])
        pygame.display.flip()

    def _draw_background_alcohol(self):
        """Draw alcohol-themed background decorations"""
        # Draw some wine glasses in corners
        glass_positions = [(50, 50), (550, 50), (50, 400), (550, 400)]
        glass_color = (100, 100, 100)  # Dark gray

        for gx, gy in glass_positions:
            # Wine glass stem
            pygame.draw.rect(self.display, glass_color, pygame.Rect(gx, gy+12, 2, 8))
            # Wine glass base
            pygame.draw.rect(self.display, glass_color, pygame.Rect(gx-4, gy+18, 10, 2))
            # Wine glass bowl
            pygame.draw.circle(self.display, glass_color, (gx+1, gy+8), 6, 1)

        # Draw beer mugs in other areas
        mug_positions = [(200, 100), (400, 350), (150, 300), (450, 150)]
        mug_color = (120, 120, 120)  # Medium gray

        for mx, my in mug_positions:
            # Mug body
            pygame.draw.rect(self.display, mug_color, pygame.Rect(mx, my, 12, 15), 1)
            # Mug handle
            pygame.draw.circle(self.display, mug_color, (mx+12, my+7), 3, 1)
            # Mug foam top
            pygame.draw.line(self.display, mug_color, (mx+1, my+1), (mx+11, my+1))

    def _move(self,direction):
        x = self.head.x
        y = self.head.y
        if(direction == Direction.RIGHT):
            x+=BLOCK_SIZE
        elif(direction == Direction.LEFT):
            x-=BLOCK_SIZE
        elif(direction == Direction.DOWN):
            y+=BLOCK_SIZE
        elif(direction == Direction.UP):
            y-=BLOCK_SIZE
        self.head = Point(x,y)
    def _is_collision(self):
        #hit boundary
        if(self.head.x>self.w-BLOCK_SIZE or self.head.x<0 or self.head.y>self.h - BLOCK_SIZE or self.head.y<0):
            return True
        if(self.head in self.snake[1:]):
            return True
        return False

if __name__=="__main__":
    game = SnakeGame()

    #Game loop
    #game_over=False
    while True:
        game_over,score=game.play_step()
        if(game_over == True):
            break
    print('Final Score',score)

    pygame.quit()
