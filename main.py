import pygame
import random
import serial
import re
from serial import Serial
pygame.init()

sw = 800
sh = 800
ser = serial.Serial("COM3", 9600)

bg = pygame.image.load('starsbg.png')
win = pygame.display.set_mode((sw, sh))
pygame.display.set_caption("NeuroArkanoid")

brickHitSound = pygame.mixer.Sound("bullet.wav")
bounceSound = pygame.mixer.Sound("hitGameSound.wav")
bounceSound.set_volume(.2)

clock = pygame.time.Clock()

gameover = False

class Paddle(object):
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.xx = self.x + self.w
        self.yy = self.y + self.h

    def draw(self, win):
        pygame.draw.rect(win, self.color, [self.x, self.y, self.w, self.h])


class Ball(object):
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.xv = random.choice([2, 3, 4, -2, -3, -4])
        self.yv = random.randint(3, 4)
        self.xx = self.x + self.w
        self.yy = self.y + self.h

    def draw(self, win):
        pygame.draw.rect(win, self.color, [self.x, self.y, self.w, self.h])

    def move(self):
        self.x += self.xv
        self.y += self.yv

class Brick(object):
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.visible = True
        self.xx = self.x + self.w
        self.yy = self.y + self.h

        self.ranNum = random.randint(0,10)
        if self.ranNum < 3:
            self.pregnant = True
        else:
            self.pregnant = False


    def draw(self, win):
        pygame.draw.rect(win, self.color, [self.x, self.y, self.w, self.h])




bricks = []
def init():
    global bricks
    bricks = []
    for i in range(6):
        for j in range(10):
            bricks.append(Brick(10 + j * 79, 50 + i * 35, 70, 25, (120, 205, 250)))

def redrawGameWindow():
    win.blit(bg, (0,0))
    player.draw(win)
    for ball in balls:
        ball.draw(win)
    for b in bricks:
        b.draw(win)

    font = pygame.font.SysFont('comicsans', 50)

    if gameover:
        if len(bricks) == 0:
            resText = font.render("Congrats!", 1, (255, 255, 255))
        else:
            resText = font.render("That's rough!", 1, (255, 255, 255))
        win.blit(resText, ((sw//2 - resText.get_width()//2), sh//2 - resText.get_height()//2))
        playAgainText = font.render("Press Space to Play Again", 1, (255, 255, 255))
        win.blit(playAgainText, ((sw//2 - playAgainText.get_width()//2), sh//2 + 30 ))

    pygame.display.update()



player = Paddle(sw/2 - 50, sh -100, 140, 20, (0, 255, 100))
ball = Ball(sw/2 - 10, sh - 400, 20, 20, (255, 255, 255))
balls = [ball]
init()
run = True
while run:
    data = ser.readline()
    print(data);
    clock.tick(100)
    if not gameover:
        for ball in balls:
            ball.move()
            #MOUSE PART
        #if pygame.mouse.get_pos()[0] - player.w // 2 < 0:
            #player.x = 0
        #elif pygame.mouse.get_pos()[0] + player.w // 2 > sw:
            #player.x = sw - player.w
        #else:
            #player.x = pygame.mouse.get_pos()[0] - player.w // 2
            #MUSCLE SENSOR
        if int(data) >= 650 and player.x < 600 :
            player.x += 10
        elif int(data) < 650 and player.x >= 0:
            player.x -= 10


        for ball in balls:
            if (ball.x >= player.x and ball.x <= player.x + player.w) or (ball.x + ball.w >= player.x and ball.x + ball.w <= player.x + player.w):
                if ball.y + ball.h >= player.y and ball.y + ball.h <= player.y + player.h:
                    ball.yv *= -1
                    ball.y = player.y -ball.h -1
                    bounceSound.play()

            if ball.x + ball.w >= sw:
                bounceSound.play()
                ball.xv *= -1
            if ball.x < 0:
                bounceSound.play()
                ball.xv *= -1
            if ball.y <= 0:
                bounceSound.play()
                ball.yv *= -1

            if ball.y > sh:
                balls.pop(balls.index(ball))

        for brick in bricks:
            for ball in balls:
                if (ball.x >= brick.x and ball.x <= brick.x + brick.w) or ball.x + ball.w >= brick.x and ball.x + ball.w <= brick.x + brick.w:
                    if (ball.y >= brick.y and ball.y <= brick.y + brick.h) or ball.y + ball.h >= brick.y and ball.y + ball.h <= brick.y + brick.h:
                        brick.visible = False
                        if brick.pregnant:
                            balls.append(Ball(brick.x, brick.y, 20, 20, (255, 255, 255)))
                        # bricks.pop(bricks.index(brick))
                        ball.yv *= -1
                        brickHitSound.play()
                        break

        for brick in bricks:
            if brick.visible == False:
                bricks.pop(bricks.index(brick))

        if len(balls) == 0:
            gameover = True


    keys = pygame.key.get_pressed()
    if len(bricks) == 0:
        won = True
        gameover = True
    if gameover:
        if keys[pygame.K_SPACE]:
            gameover = False
            won = False
            ball = Ball(sw/2 - 10, sh - 400, 20, 20, (255, 255, 255))
            if len(balls) == 0:
                balls.append(ball)

            bricks.clear()
            for i in range(6):
                for j in range(10):
                    bricks.append(Brick(10 + j * 79, 50 + i * 35, 70, 25, (120, 205, 250)))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    redrawGameWindow()

pygame.quit()