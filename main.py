import math
import random
import pygame
from pygame import mixer

# Initialize the pygame
pygame.init()

# Constants for better configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 4
BULLET_SPEED = 10
ENEMY_SPEED = 0.3
ENEMY_DROP_SPEED = 25
FPS = 60
MAX_BULLETS = 5

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)

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
pygame.display.set_caption("Space Invaders Enhanced")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load('player.png')
playerX = 370
playerY = 480
playerX_change = 0
player_lives = 3
invulnerable_time = 0

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
enemy_types = []  # 0: normal, 1: fast, 2: strong
num_of_enemies = 6
level = 1

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('enemy.png'))
    enemyX.append(random.randint(0, SCREEN_WIDTH - 65))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(ENEMY_SPEED)
    enemyY_change.append(ENEMY_DROP_SPEED)
    enemy_types.append(0)  # All normal enemies initially

# Multiple Bullets
bullets = []
bullet_cooldown = 0

# Power-ups
powerups = []
powerup_spawn_time = 0
active_powerups = {'rapid_fire': 0, 'shield': 0, 'multi_shot': 0, 'laser': 0, 'freeze': 0}
freeze_timer = 0

# Particles for explosions
particles = []

# Score and stats
score_value = 0
high_score = 0
enemies_killed = 0
font = pygame.font.Font('freesansbold.ttf', 24)
big_font = pygame.font.Font('freesansbold.ttf', 48)
small_font = pygame.font.Font('freesansbold.ttf', 18)

# Game states
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3
game_state = MENU

# Sound effects
bullet_sound = mixer.Sound('laser.wav')
explosion_sound = mixer.Sound('explosion.wav')


# --- Variables globales para enemigos y jefe ---
enemy_bullets = []
boss_bullets = []
boss_active = False
boss = None


class Bullet:
    def __init__(self, x, y, speed=BULLET_SPEED, angle=0):
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle  # Angle in radians for triangle shots
        self.active = True

    def update(self):
        if self.angle == 0:  # Normal straight bullet
            self.y -= self.speed
        else:  # Angled bullet for triangle formation
            self.x += math.sin(self.angle) * self.speed * 0.5
            self.y -= math.cos(self.angle) * self.speed

        if self.y < 0 or self.x < 0 or self.x > SCREEN_WIDTH:
            self.active = False

    def draw(self):
        pygame.draw.rect(screen, YELLOW, (int(self.x), int(self.y), 4, 10))


class PowerUp:
    def __init__(self, x, y, type_):
        self.x = x
        self.y = y
        self.type = type_  # 'rapid_fire', 'shield', 'multi_shot', 'extra_life', 'laser', 'freeze'
        self.speed = 2
        self.active = True
        self.colors = {
            'rapid_fire': RED,
            'shield': BLUE,
            'multi_shot': GREEN,
            'extra_life': PURPLE,
            'laser': CYAN,
            'freeze': PINK
        }
        self.pulse = 0  # For pulsing effect

    def update(self):
        self.y += self.speed
        self.pulse += 0.2
        if self.y > SCREEN_HEIGHT:
            self.active = False

    def draw(self):
        color = self.colors.get(self.type, WHITE)
        pulse_size = 15 + int(3 * math.sin(self.pulse))
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), pulse_size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), pulse_size, 2)

        # Add type indicator
        if self.type == 'rapid_fire':
            symbol = "R"
        elif self.type == 'shield':
            symbol = "S"
        elif self.type == 'multi_shot':
            symbol = "M"
        elif self.type == 'extra_life':
            symbol = "+"
        elif self.type == 'laser':
            symbol = "L"
        elif self.type == 'freeze':
            symbol = "F"
        else:
            symbol = "?"

        text_surface = small_font.render(symbol, True, WHITE)
        text_rect = text_surface.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text_surface, text_rect)


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-3, 3)
        self.life = 30
        self.max_life = 30
        self.color = random.choice([RED, ORANGE, YELLOW])

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 1

    def draw(self):
        alpha = int(255 * (self.life / self.max_life))
        size = int(4 * (self.life / self.max_life))
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)


def create_explosion(x, y):
    for _ in range(15):
        particles.append(Particle(x + 32, y + 32))


def spawn_powerup(x, y):
    if random.random() < 0.4:  # 40% chance (increased)
        powerup_types = ['rapid_fire', 'shield', 'multi_shot', 'extra_life', 'laser', 'freeze']
        powerup_type = random.choice(powerup_types)
        powerups.append(PowerUp(x, y, powerup_type))


def show_hud():
    # Score
    score_text = font.render(f"Puntuación: {score_value}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # High Score
    high_score_text = font.render(f"Récord: {high_score}", True, WHITE)
    screen.blit(high_score_text, (10, 40))

    # Lives
    lives_text = font.render(f"Vidas: {player_lives}", True, WHITE)
    screen.blit(lives_text, (10, 70))

    # Level
    level_text = font.render(f"Nivel: {level}", True, WHITE)
    screen.blit(level_text, (10, 100))

    # Active power-ups
    y_offset = 130
    for powerup, time_left in active_powerups.items():
        if time_left > 0:
            powerup_names = {
                'rapid_fire': 'Disparo Rápido',
                'shield': 'Escudo',
                'multi_shot': 'Multi-Disparo',
                'laser': 'Láser',
                'freeze': 'Congelamiento'
            }
            name = powerup_names.get(powerup, powerup)
            powerup_text = small_font.render(f"{name}: {time_left//60}s", True, GREEN)
            screen.blit(powerup_text, (10, y_offset))
            y_offset += 20

    # Freeze effect indicator
    if freeze_timer > 0:
        freeze_text = font.render("¡ENEMIGOS CONGELADOS!", True, CYAN)
        screen.blit(freeze_text, (SCREEN_WIDTH//2 - 150, 150))

def show_menu():
    screen.fill((0, 0, 50))

    title_text = big_font.render("INVASORES ESPACIALES", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
    screen.blit(title_text, title_rect)

    subtitle_text = font.render("Edición Mejorada", True, YELLOW)
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 170))
    screen.blit(subtitle_text, subtitle_rect)

    start_text = font.render("Presiona ESPACIO para Empezar", True, WHITE)
    start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
    screen.blit(start_text, start_rect)

    controls_text = [
        "Controles:",
        "Flechas - Mover",
        "ESPACIO - Disparar",
        "P - Pausar",
        "ESC - Salir"
    ]

    for i, text in enumerate(controls_text):
        color = WHITE if i == 0 else (200, 200, 200)
        control_text = small_font.render(text, True, color)
        control_rect = control_text.get_rect(center=(SCREEN_WIDTH // 2, 320 + i * 25))
        screen.blit(control_text, control_rect)

    # Power-ups info
    powerup_info = [
        "Power-ups:",
        "R - Disparo Rápido",
        "S - Escudo Protector",
        "M - Multi-Disparo Triangular",
        "+ - Vida Extra",
        "L - Láser Penetrante",
        "F - Congelar Enemigos"
    ]

    for i, text in enumerate(powerup_info):
        color = YELLOW if i == 0 else (180, 180, 180)
        info_text = small_font.render(text, True, color)
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, 450 + i * 20))
        screen.blit(info_text, info_rect)

def show_pause():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    pause_text = big_font.render("PAUSADO", True, WHITE)
    pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(pause_text, pause_rect)

    resume_text = font.render("Presiona P para Continuar", True, WHITE)
    resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
    screen.blit(resume_text, resume_rect)

def show_game_over():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    game_over_text = big_font.render("JUEGO TERMINADO", True, RED)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
    screen.blit(game_over_text, game_over_rect)

    final_score_text = font.render(f"Puntuación Final: {score_value}", True, WHITE)
    final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
    screen.blit(final_score_text, final_score_rect)

    if score_value == high_score:
        new_record_text = font.render("¡NUEVO RÉCORD!", True, YELLOW)
        new_record_rect = new_record_text.get_rect(center=(SCREEN_WIDTH // 2, 320))
        screen.blit(new_record_text, new_record_rect)

    restart_text = font.render("Presiona R para Reiniciar o ESC para Menú", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 380))
    screen.blit(restart_text, restart_rect)


def player_draw(x, y):
    # Draw shield effect if active
    if active_powerups['shield'] > 0:
        pygame.draw.circle(screen, BLUE, (int(x + 32), int(y + 32)), 40, 3)

    # Blinking effect when invulnerable
    if invulnerable_time > 0 and invulnerable_time % 10 < 5:
        return

    screen.blit(playerImg, (x, y))


def enemy_draw(x, y, i):
    # Different colors for different enemy types
    if i < len(enemy_types):
        if enemy_types[i] == 1:  # Fast enemy
            pygame.draw.circle(screen, RED, (int(x + 32), int(y + 32)), 35, 3)
        elif enemy_types[i] == 2:  # Strong enemy
            pygame.draw.circle(screen, PURPLE, (int(x + 32), int(y + 32)), 35, 3)

    screen.blit(enemyImg[i], (x, y))


def fire_bullet(x, y):
    global bullet_cooldown
    if bullet_cooldown <= 0 and len(bullets) < MAX_BULLETS:
        bullet_sound.play()

        if active_powerups['multi_shot'] > 0:
            bullets.append(Bullet(x + 16, y, BULLET_SPEED, 0.0))        # Center straight
            bullets.append(Bullet(x + 16, y, BULLET_SPEED, -0.3))     # Left angled
            bullets.append(Bullet(x + 16, y, BULLET_SPEED, 0.3))      # Right angled
        elif active_powerups['laser'] > 0:
            bullets.append(Bullet(x + 16, y, int(BULLET_SPEED * 1.5)))
        else:
            bullets.append(Bullet(x + 16, y))

        # Rapid fire power-up
        if active_powerups['rapid_fire'] > 0:
            bullet_cooldown = 3
        else:
            bullet_cooldown = 10


def isCollision(x1, y1, x2, y2, distance=50):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) < distance


def check_level_complete():
    global level, num_of_enemies, ENEMY_SPEED
    if enemies_killed >= num_of_enemies:
        level += 1
        num_of_enemies = min(6 + level, 12)  # Max 12 enemies
        ENEMY_SPEED += 0.1

        # Reset enemies for new level
        reset_enemies()
        return True
    return False


def reset_enemies():
    global enemyX, enemyY, enemyX_change, enemyY_change, enemy_types, enemies_killed, enemyImg
    enemyX.clear()
    enemyY.clear()
    enemyX_change.clear()
    enemyY_change.clear()
    enemy_types.clear()
    enemyImg.clear()
    enemies_killed = 0

    for i in range(num_of_enemies):
        enemyImg.append(pygame.image.load('enemy.png'))
        enemyX.append(random.randint(0, SCREEN_WIDTH - 65))
        enemyY.append(random.randint(50, 150))
        enemyX_change.append(ENEMY_SPEED)
        enemyY_change.append(ENEMY_DROP_SPEED)

        # Add special enemies in higher levels
        if level > 2 and random.random() < 0.3:
            enemy_types.append(random.choice([1, 2]))  # Fast or strong
        else:
            enemy_types.append(0)  # Normal


def reset_game():
    global score_value, playerX, playerY, player_lives, level, num_of_enemies
    global bullets, powerups, particles, active_powerups, enemies_killed
    global invulnerable_time, bullet_cooldown, powerup_spawn_time, ENEMY_SPEED, freeze_timer

    score_value = 0
    playerX = 370
    playerY = 480
    player_lives = 3
    level = 1
    num_of_enemies = 6
    enemies_killed = 0
    invulnerable_time = 0
    bullet_cooldown = 0
    powerup_spawn_time = 0
    freeze_timer = 0
    ENEMY_SPEED = 0.3

    bullets.clear()
    powerups.clear()
    particles.clear()
    active_powerups = {'rapid_fire': 0, 'shield': 0, 'multi_shot': 0, 'laser': 0, 'freeze': 0}

    reset_enemies()


# --- Clase EnemyBullet ---
class EnemyBullet:
    def __init__(self, x, y, speed=5, angle=0.0):
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = float(angle)
        self.active = True
    def update(self):
        self.x += math.sin(self.angle) * self.speed
        self.y += math.cos(self.angle) * self.speed
        if self.y > SCREEN_HEIGHT or self.x < 0 or self.x > SCREEN_WIDTH:
            self.active = False
    def draw(self):
        pygame.draw.rect(screen, RED, (int(self.x), int(self.y), 4, 10))


# Game Loop
running = True
while running:
    clock.tick(FPS)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_state == MENU:
                if event.key == pygame.K_SPACE:
                    game_state = PLAYING
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False

            elif game_state == PLAYING:
                if event.key == pygame.K_LEFT:
                    playerX_change = -PLAYER_SPEED
                elif event.key == pygame.K_RIGHT:
                    playerX_change = PLAYER_SPEED
                elif event.key == pygame.K_SPACE:
                    fire_bullet(playerX, playerY)
                elif event.key == pygame.K_p:
                    game_state = PAUSED
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU

            elif game_state == PAUSED:
                if event.key == pygame.K_p:
                    game_state = PLAYING
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU

            elif game_state == GAME_OVER:
                if event.key == pygame.K_r:
                    game_state = PLAYING
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0

    # Clear screen
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    if game_state == MENU:
        show_menu()

    elif game_state == PLAYING:
        # Update timers
        if bullet_cooldown > 0:
            bullet_cooldown -= 1
        if invulnerable_time > 0:
            invulnerable_time -= 1
        if freeze_timer > 0:
            freeze_timer -= 1

        # Update power-ups timers
        for powerup in active_powerups:
            if active_powerups[powerup] > 0:
                active_powerups[powerup] -= 1

        # Player movement
        playerX += playerX_change
        playerX = max(0, min(playerX, SCREEN_WIDTH - 64))

        # Update bullets
        for bullet in bullets[:]:
            bullet.update()
            if not bullet.active:
                bullets.remove(bullet)

        # Update powerups
        powerup_spawn_time += 1
        if powerup_spawn_time > 1200:  # Spawn every 20 seconds (more frequent)
            spawn_powerup(random.randint(50, SCREEN_WIDTH - 50), 0)
            powerup_spawn_time = 0

        for powerup in powerups[:]:
            powerup.update()
            if not powerup.active:
                powerups.remove(powerup)
            elif isCollision(playerX + 32, playerY + 32, powerup.x, powerup.y, 30):
                # Collect powerup
                if powerup.type == 'extra_life':
                    player_lives += 1
                elif powerup.type == 'freeze':
                    freeze_timer = 300  # 5 seconds
                else:
                    active_powerups[powerup.type] = 600  # 10 seconds
                powerups.remove(powerup)

        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)

        # Enemy movement and collision
        for i in range(len(enemyX)):
            # Enemy movement (affected by freeze)
            if freeze_timer <= 0:  # Only move if not frozen
                enemyX[i] += enemyX_change[i]

                if enemyX[i] <= 0:
                    enemyX_change[i] = ENEMY_SPEED * (2 if i < len(enemy_types) and enemy_types[i] == 1 else 1)
                    enemyY[i] += enemyY_change[i]
                elif enemyX[i] >= SCREEN_WIDTH - 64:
                    enemyX_change[i] = -ENEMY_SPEED * (2 if i < len(enemy_types) and enemy_types[i] == 1 else 1)
            # Enemy disparo aleatorio
            if boss_active == False and freeze_timer <= 0 and random.random() < 0.005:
                # Disparo recto hacia abajo
                enemy_bullets.append(EnemyBullet(enemyX[i] + 32, enemyY[i] + 64, 5, 0))
                enemyY[i] += enemyY_change[i]

                # Check if enemy reached player
                if enemyY[i] > 400:
                    if invulnerable_time <= 0 and active_powerups['shield'] <= 0:
                        player_lives -= 1
                        invulnerable_time = 120  # 2 seconds of invulnerability
                        if player_lives <= 0:
                            high_score = max(high_score, score_value)
                            game_state = GAME_OVER
                            continue

            # Bullet-enemy collision
            for bullet in bullets[:]:
                if isCollision(enemyX[i] + 32, enemyY[i] + 32, bullet.x, bullet.y, 30):
                    explosion_sound.play()
                    create_explosion(enemyX[i], enemyY[i])

                    # Laser bullets don't get removed (penetrate through enemies)
                    if active_powerups['laser'] <= 0:
                        bullets.remove(bullet)

                    # Handle different enemy types
                    if i < len(enemy_types) and enemy_types[i] == 2:  # Strong enemy
                        enemy_types[i] = 0  # Becomes normal
                        score_value += 3
                    else:
                        score_value += 10 if i < len(enemy_types) and enemy_types[i] == 1 else 2
                        enemies_killed += 1
                        spawn_powerup(enemyX[i], enemyY[i])

                        # Respawn enemy
                        enemyX[i] = random.randint(0, SCREEN_WIDTH - 65)
                        enemyY[i] = random.randint(50, 150)

                        # Check level completion
                        if check_level_complete():
                            break

                    # Remove bullet if not laser
                    if active_powerups['laser'] > 0:
                        continue
                    else:
                        break

        # Draw everything
        for bullet in bullets:
            # Draw laser bullets differently
            if active_powerups['laser'] > 0:
                pygame.draw.rect(screen, CYAN, (int(bullet.x), int(bullet.y), 6, 15))
            else:
                bullet.draw()


        # Actualizar y dibujar balas enemigas
        for bullet in enemy_bullets[:]:
            bullet.update()
            bullet.draw()
            # Colisión con el jugador
            if isCollision(playerX + 32, playerY + 32, bullet.x, bullet.y, 25):
                if invulnerable_time <= 0 and active_powerups['shield'] <= 0:
                    player_lives -= 1
                    invulnerable_time = 120
                    if player_lives <= 0:
                        high_score = max(high_score, score_value)
                        game_state = GAME_OVER
                enemy_bullets.remove(bullet)
            elif not bullet.active:
                enemy_bullets.remove(bullet)

        # Daño al jefe por balas del jugador
        if boss_active and boss is not None:
            for bullet in bullets[:]:
                if isCollision(boss.x + 60, boss.y + 40, bullet.x, bullet.y, 60):
                    boss.hp -= 1 if active_powerups['laser'] <= 0 else 3
                    if active_powerups['laser'] <= 0:
                        bullets.remove(bullet)
                    if boss.hp <= 0:
                        score_value += 100
                        boss_active = False
                        boss = None
                        create_explosion(playerX, boss.y)
                        break
        for powerup in powerups:
            powerup.draw()

        for particle in particles:
            particle.draw()

        # Draw enemies with freeze effect
        for i in range(len(enemyX)):
            if freeze_timer > 0:
                # Draw frozen effect
                pygame.draw.circle(screen, CYAN, (int(enemyX[i] + 32), int(enemyY[i] + 32)), 40, 2)
            enemy_draw(enemyX[i], enemyY[i], i)

        player_draw(playerX, playerY)
        show_hud()

    elif game_state == PAUSED:
        # Draw game state first, then overlay
        for i in range(len(enemyX)):
            enemy_draw(enemyX[i], enemyY[i], i)
        player_draw(playerX, playerY)
        show_hud()
        show_pause()

    elif game_state == GAME_OVER:
        show_game_over()

    pygame.display.update()

pygame.quit()
