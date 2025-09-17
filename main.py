import math
import random

import pygame
from pygame import mixer

# Initialize the pygame
pygame.init()

# Constants for better configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 3
BULLET_SPEED = 15
ENEMY_SPEED = 0.5
ENEMY_DROP_SPEED = 40
FPS = 60

# create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Background
background = pygame.image.load('background.jpg')
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Background Sound
mixer.music.load('background.wav')
mixer.music.play(-1)

# Title and icon
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load('player.png')
playerX = 370
playerY = 480
playerX_change = 0

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('enemy.png'))
    enemyX.append(random.randint(0, SCREEN_WIDTH - 65))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(ENEMY_SPEED)
    enemyY_change.append(ENEMY_DROP_SPEED)

# Bullet
bulletImg = pygame.image.load('bullet.png')
bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = BULLET_SPEED
bullet_state = "ready"

# Score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
textX = 10
textY = 10

# Game Over text
over_font = pygame.font.Font('freesansbold.ttf', 64)

# Sound effects
bullet_sound = mixer.Sound('laser.wav')
explosion_sound = mixer.Sound('explosion.wav')


def show_score(x, y):
    score = font.render("Score: " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(over_text, (200, 250))
    restart_text = font.render("Press R to restart or ESC to quit", True, (255, 255, 255))
    screen.blit(restart_text, (220, 320))


def player(x, y):
    screen.blit(playerImg, (x, y))


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))


def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((math.pow(enemyX - bulletX, 2)) + (math.pow(enemyY - bulletY, 2)))
    return distance < 27


def reset_game():
    global score_value, playerX, playerY, bulletX, bulletY, bullet_state
    global enemyX, enemyY, enemyX_change, enemyY_change

    score_value = 0
    playerX = 370
    playerY = 480
    bulletX = 0
    bulletY = 480
    bullet_state = "ready"

    for i in range(num_of_enemies):
        enemyX[i] = random.randint(0, SCREEN_WIDTH - 65)
        enemyY[i] = random.randint(50, 150)
        enemyX_change[i] = ENEMY_SPEED
        enemyY_change[i] = ENEMY_DROP_SPEED


# Game state
game_over = False

# Game Loop
running = True
while running:
    clock.tick(FPS)

    # RGB
    screen.fill((0, 0, 0))
    # Background Image
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # if keystroke is pressed check whether its right or left
        if event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_LEFT:
                    playerX_change = -PLAYER_SPEED
                if event.key == pygame.K_RIGHT:
                    playerX_change = PLAYER_SPEED
                if event.key == pygame.K_SPACE:
                    if bullet_state == "ready":
                        bullet_sound.play()
                        bulletX = playerX
                        fire_bullet(bulletX, bulletY)
            else:
                if event.key == pygame.K_r:
                    game_over = False
                    reset_game()
                if event.key == pygame.K_ESCAPE:
                    running = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0

    if not game_over:
        # Checking for boundaries of spaceship so it doesn't go out of bounds
        playerX += playerX_change
        if playerX <= 0:
            playerX = 0
        elif playerX >= SCREEN_WIDTH - 64:
            playerX = SCREEN_WIDTH - 64

        # Enemy movement
        for i in range(num_of_enemies):
            # Game Over
            if enemyY[i] > 440:
                game_over = True
                break

            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0:
                enemyX_change[i] = ENEMY_SPEED
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= SCREEN_WIDTH - 64:
                enemyX_change[i] = -ENEMY_SPEED
                enemyY[i] += enemyY_change[i]

            # Collision
            collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
            if collision:
                explosion_sound.play()
                bulletY = 480
                bullet_state = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, SCREEN_WIDTH - 65)
                enemyY[i] = random.randint(50, 150)

            enemy(enemyX[i], enemyY[i], i)

        # Bullet movement
        if bulletY <= 0:
            bulletY = 480
            bullet_state = "ready"

        if bullet_state == "fire":
            fire_bullet(bulletX, bulletY)
            bulletY -= bulletY_change

        player(playerX, playerY)
    else:
        game_over_text()

    show_score(textX, textY)
    pygame.display.update()

pygame.quit()
