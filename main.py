
import pygame
import random
import sys
import os
import math
from array import array

# ==================================================
# 1. INITIALIZATION
# ==================================================

pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()

WIDTH, HEIGHT = 900, 650
FPS = 60
ENEMY_SPEED = 75

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GALAXY WAR - Space Shooter")

clock = pygame.time.Clock()

# ==================================================
# 2. COLORS
# ==================================================

BLACK = (5, 7, 22)
WHITE = (245, 250, 255)
BLUE = (30, 170, 255)
CYAN = (0, 240, 255)
RED = (255, 65, 85)
ORANGE = (255, 150, 35)
YELLOW = (255, 225, 80)
PURPLE = (170, 80, 255)
GREEN = (70, 255, 150)
DARK_BLUE = (10, 30, 65)

# ==================================================
# 3. FONTS
# ==================================================

font = pygame.font.Font(None, 30)
medium_font = pygame.font.Font(None, 44)
large_font = pygame.font.Font(None, 76)
small_font = pygame.font.Font(None, 22)

# ==================================================
# 4. OPTIONAL GENERATED SOUND EFFECTS
# ==================================================

sound_enabled = False
sounds = {}

try:
    pygame.mixer.init()

    def make_tone(frequency, duration, volume=0.2):
        sample_rate = 22050
        samples = int(sample_rate * duration)
        audio = array("h")

        for i in range(samples):
            t = i / sample_rate
            envelope = max(0, 1 - t / duration)
            value = int(
                32767 * volume * envelope *
                math.sin(2 * math.pi * frequency * t)
            )
            audio.append(value)

        return pygame.mixer.Sound(buffer=audio.tobytes())

    sounds["shoot"] = make_tone(850, 0.08, 0.12)
    sounds["hit"] = make_tone(180, 0.18, 0.2)
    sounds["explosion"] = make_tone(90, 0.35, 0.25)
    sounds["menu"] = make_tone(550, 0.12, 0.12)

    sound_enabled = True

except pygame.error:
    print("Audio unavailable. Game will run without sound.")


def play_sound(name):
    if sound_enabled and name in sounds:
        sounds[name].play()


# ==================================================
# 5. HIGH SCORE STORAGE
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIGH_SCORE_FILE = os.path.join(BASE_DIR, "highscore.txt")


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            return int(file.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def save_high_score(value):
    try:
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(value))
    except OSError:
        print("Could not save high score.")


high_score = load_high_score()


# ==================================================
# 6. STARFIELD
# ==================================================

stars = []

for _ in range(130):
    stars.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "speed": random.uniform(0.6, 4),
        "size": random.randint(1, 3)
    })


def update_stars():
    for star in stars:
        star["y"] += star["speed"]

        if star["y"] > HEIGHT:
            star["y"] = 0
            star["x"] = random.randint(0, WIDTH)


def draw_stars(surface):
    for star in stars:
        pygame.draw.circle(
            surface,
            (125, 155, 200),
            (int(star["x"]), int(star["y"])),
            star["size"]
        )


# ==================================================
# 7. GRAPHICS
# ==================================================

def draw_player(surface, x, y, invulnerable=False):

    if invulnerable and pygame.time.get_ticks() // 100 % 2 == 0:
        return

    flame = random.randint(12, 24)

    # Engine flame
    pygame.draw.polygon(
        surface,
        ORANGE,
        [
            (x - 8, y + 15),
            (x, y + 18 + flame),
            (x + 8, y + 15)
        ]
    )

    pygame.draw.polygon(
        surface,
        CYAN,
        [
            (x - 4, y + 15),
            (x, y + flame),
            (x + 4, y + 15)
        ]
    )

    # Wings
    pygame.draw.polygon(
        surface,
        DARK_BLUE,
        [
            (x, y - 32),
            (x - 31, y + 19),
            (x - 12, y + 14),
            (x + 12, y + 14),
            (x + 31, y + 19)
        ]
    )

    # Main body
    pygame.draw.polygon(
        surface,
        BLUE,
        [
            (x, y - 32),
            (x - 15, y + 18),
            (x, y + 11),
            (x + 15, y + 18)
        ]
    )

    pygame.draw.polygon(
        surface,
        CYAN,
        [
            (x, y - 32),
            (x - 15, y + 18),
            (x, y + 11),
            (x + 15, y + 18)
        ],
        2
    )

    # Cockpit
    pygame.draw.ellipse(
        surface,
        WHITE,
        (x - 6, y - 17, 12, 22)
    )

    pygame.draw.ellipse(
        surface,
        CYAN,
        (x - 4, y - 14, 8, 15)
    )


def draw_enemy(surface, enemy):

    x = enemy["rect"].centerx
    y = enemy["rect"].centery

    if enemy["type"] == "heavy":

        pygame.draw.polygon(
            surface,
            PURPLE,
            [
                (x - 25, y - 10),
                (x - 12, y - 22),
                (x + 12, y - 22),
                (x + 25, y - 10),
                (x + 30, y + 15),
                (x, y + 24),
                (x - 30, y + 15)
            ]
        )

        pygame.draw.polygon(
            surface,
            CYAN,
            [
                (x - 25, y - 10),
                (x - 12, y - 22),
                (x + 12, y - 22),
                (x + 25, y - 10),
                (x + 30, y + 15),
                (x, y + 24),
                (x - 30, y + 15)
            ],
            2
        )

        pygame.draw.circle(surface, YELLOW, (x, y), 7)

    else:

        pygame.draw.polygon(
            surface,
            RED,
            [
                (x - 20, y - 5),
                (x - 12, y - 19),
                (x, y - 12),
                (x + 12, y - 19),
                (x + 20, y - 5),
                (x + 16, y + 13),
                (x, y + 18),
                (x - 16, y + 13)
            ]
        )

        pygame.draw.circle(surface, YELLOW, (x - 8, y), 4)
        pygame.draw.circle(surface, YELLOW, (x + 8, y), 4)


# ==================================================
# 8. PARTICLE EFFECTS
# ==================================================

particles = []


def create_explosion(x, y, color=ORANGE, amount=22):

    for _ in range(amount):

        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 5)

        particles.append({
            "x": float(x),
            "y": float(y),
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(20, 40),
            "size": random.randint(2, 5),
            "color": color
        })


def update_particles():

    for particle in particles[:]:

        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["life"] -= 1

        if particle["life"] <= 0:
            particles.remove(particle)


def draw_particles(surface):

    for particle in particles:

        pygame.draw.circle(
            surface,
            particle["color"],
            (int(particle["x"]), int(particle["y"])),
            max(1, particle["size"] * particle["life"] // 40)
        )


# ==================================================
# 9. GAME VARIABLES
# ==================================================

def reset_game():

    global player_x, player_y
    global bullets, enemies, enemy_bullets
    global score, lives, game_over
    global game_start_time, last_shot
    global last_enemy_spawn, last_enemy_shot
    global invulnerable_until, shake

    player_x = WIDTH // 2
    player_y = HEIGHT - 85

    bullets = []
    enemies = []
    enemy_bullets = []

    particles.clear()

    score = 0
    lives = 5

    game_over = False

    game_start_time = pygame.time.get_ticks()

    last_shot = 0
    last_enemy_spawn = pygame.time.get_ticks()
    last_enemy_shot = pygame.time.get_ticks()

    invulnerable_until = 0
    shake = 0


# ==================================================
# 10. GAME STATE
# ==================================================

MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"

game_state = MENU

start_button = pygame.Rect(WIDTH // 2 - 110, 340, 220, 55)
restart_button = pygame.Rect(WIDTH // 2 - 110, 395, 220, 55)
menu_button = pygame.Rect(WIDTH // 2 - 110, 470, 220, 55)
resume_button = pygame.Rect(WIDTH // 2 - 100, 375, 200, 55)

reset_game()


# ==================================================
# 11. HELPER FUNCTIONS
# ==================================================

def draw_text(surface, text, current_font, color, x, y, center=True):

    image = current_font.render(text, True, color)
    rect = image.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    surface.blit(image, rect)


def draw_button(surface, text, x, y, width, height):

    rect = pygame.Rect(x, y, width, height)

    mouse_pos = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse_pos)

    color = (20, 110, 160) if hovered else (12, 45, 85)

    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=12
    )

    pygame.draw.rect(
        surface,
        CYAN,
        rect,
        2,
        border_radius=12
    )

    draw_text(
        surface,
        text,
        font,
        WHITE,
        rect.centerx,
        rect.centery
    )

    return rect


def start_game():
    global game_state
    reset_game()
    game_state = PLAYING
    play_sound("menu")


# ==================================================
# 12. MAIN LOOP
# ==================================================

running = True

while running:

    dt = clock.tick(FPS) / 1000
    now = pygame.time.get_ticks()

    update_stars()
    update_particles()

    # ==============================================
    # 13. EVENTS
    # ==============================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                if game_state == PLAYING:
                    game_state = PAUSED

                elif game_state == PAUSED:
                    game_state = PLAYING

                elif game_state == MENU:
                    running = False

            if game_state == MENU:

                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    start_game()

            elif game_state == PAUSED:

                if event.key in (pygame.K_p, pygame.K_RETURN):
                    game_state = PLAYING

            elif game_state == GAME_OVER:

                if event.key == pygame.K_r:
                    start_game()

                if event.key == pygame.K_ESCAPE:
                    game_state = MENU

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if game_state == MENU:

                    if start_button.collidepoint(event.pos):
                        start_game()

                elif game_state == GAME_OVER:

                    if restart_button.collidepoint(event.pos):
                        start_game()

                    elif menu_button.collidepoint(event.pos):
                        game_state = MENU

                elif game_state == PAUSED:

                    if resume_button.collidepoint(event.pos):
                        game_state = PLAYING

    # ==============================================
    # 14. PLAYING STATE
    # ==============================================

    if game_state == PLAYING:

        elapsed = (now - game_start_time) / 1000

        difficulty = min(1.0, elapsed / 300)

        current_enemy_speed = ENEMY_SPEED + difficulty * 20

        spawn_delay = max(1400, 2200 - int(elapsed * 2))

        # Player movement
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        player_x += dx * 350 * dt
        player_y += dy * 350 * dt

        player_x = max(30, min(WIDTH - 30, player_x))
        player_y = max(40, min(HEIGHT - 40, player_y))

        # Continuous shooting
        if keys[pygame.K_SPACE] and now - last_shot > 220:

            bullets.append(
                pygame.Rect(
                    int(player_x - 4),
                    int(player_y - 30),
                    8,
                    20
                )
            )

            last_shot = now
            play_sound("shoot")

        # Enemy spawning
        if now - last_enemy_spawn > spawn_delay:

            enemy_type = "heavy" if random.random() < 0.2 else "normal"

            size = 54 if enemy_type == "heavy" else 40

            enemies.append({
                "rect": pygame.Rect(
                    random.randint(35, WIDTH - 35 - size),
                    -size,
                    size,
                    size
                ),
                "type": enemy_type,
                "health": 3 if enemy_type == "heavy" else 1,
                "speed": current_enemy_speed * (
                    0.7 if enemy_type == "heavy" else 1
                )
            })

            last_enemy_spawn = now

        # Move player bullets
        for bullet in bullets:
            bullet.y -= 650 * dt

        bullets = [
            bullet for bullet in bullets
            if bullet.bottom > 0
        ]

        # Enemy firing
        if now - last_enemy_shot > 2200:

            if enemies:

                enemy = random.choice(enemies)

                enemy_bullets.append(
                    pygame.Rect(
                        enemy["rect"].centerx - 4,
                        enemy["rect"].bottom,
                        8,
                        16
                    )
                )

            last_enemy_shot = now

        # Move enemy ships
        for enemy in enemies:
            enemy["rect"].y += enemy["speed"] * dt

        # Move enemy bullets
        for bullet in enemy_bullets:
            bullet.y += 180 * dt

        enemy_bullets = [
            bullet for bullet in enemy_bullets
            if bullet.top < HEIGHT
        ]

        # Bullet vs enemy collision
        for bullet in bullets[:]:

            for enemy in enemies[:]:

                if bullet.colliderect(enemy["rect"]):

                    if bullet in bullets:
                        bullets.remove(bullet)

                    enemy["health"] -= 1

                    if enemy["health"] <= 0:

                        ex = enemy["rect"].centerx
                        ey = enemy["rect"].centery

                        color = PURPLE if enemy["type"] == "heavy" else ORANGE

                        create_explosion(ex, ey, color)

                        enemies.remove(enemy)

                        score += 30 if enemy["type"] == "heavy" else 10

                        play_sound("explosion")
                        shake = 7

                    else:
                        play_sound("hit")

                    break

        # Player collision rectangle
        player_rect = pygame.Rect(
            int(player_x - 18),
            int(player_y - 22),
            36,
            42
        )

        # Enemy vs player collision
        if now >= invulnerable_until:

            for enemy in enemies[:]:

                if player_rect.colliderect(enemy["rect"]):

                    create_explosion(
                        enemy["rect"].centerx,
                        enemy["rect"].centery,
                        RED
                    )

                    enemies.remove(enemy)
                    lives -= 1

                    invulnerable_until = now + 2000
                    shake = 15

                    play_sound("hit")

                    break

            # Enemy bullets vs player
            if now >= invulnerable_until:

                for bullet in enemy_bullets[:]:

                    if player_rect.colliderect(bullet):

                        enemy_bullets.remove(bullet)
                        lives -= 1

                        invulnerable_until = now + 2000
                        shake = 15

                        play_sound("hit")

                        create_explosion(
                            player_x,
                            player_y,
                            BLUE,
                            12
                        )

                        break

        # Enemies passing the player
        for enemy in enemies[:]:

            if enemy["rect"].top > HEIGHT:

                enemies.remove(enemy)
                lives -= 1
                shake = 8

        # High score
        if score > high_score:
            high_score = score
            save_high_score(high_score)

        # Game over
        if lives <= 0:

            lives = 0
            game_state = GAME_OVER

            create_explosion(
                player_x,
                player_y,
                BLUE,
                45
            )

            play_sound("explosion")

    # ==============================================
    # 15. DRAW BACKGROUND
    # ==============================================

    screen.fill(BLACK)
    draw_stars(screen)

    # ==============================================
    # 16. GAMEPLAY DRAWING
    # ==============================================

    if game_state in (PLAYING, PAUSED, GAME_OVER):

        offset_x = random.randint(-shake, shake) if shake > 0 else 0
        offset_y = random.randint(-shake, shake) if shake > 0 else 0

        shake = max(0, shake - 1)

        # Draw player
        if game_state != GAME_OVER:

            invulnerable = now < invulnerable_until

            draw_player(
                screen,
                int(player_x + offset_x),
                int(player_y + offset_y),
                invulnerable
            )

        # Player bullets
        for bullet in bullets:

            shifted = bullet.move(offset_x, offset_y)

            pygame.draw.rect(
                screen,
                CYAN,
                shifted,
                border_radius=4
            )

            pygame.draw.rect(
                screen,
                WHITE,
                (shifted.x + 2, shifted.y, 3, shifted.height),
                border_radius=2
            )

        # Enemies
        for enemy in enemies:

            shifted_enemy = enemy["rect"].move(offset_x, offset_y)

            temp_enemy = enemy.copy()
            temp_enemy["rect"] = shifted_enemy

            draw_enemy(screen, temp_enemy)

            if enemy["type"] == "heavy":

                pygame.draw.rect(
                    screen,
                    DARK_BLUE,
                    (shifted_enemy.x, shifted_enemy.y - 9, shifted_enemy.width, 5)
                )

                pygame.draw.rect(
                    screen,
                    GREEN,
                    (shifted_enemy.x, shifted_enemy.y - 9,
                     shifted_enemy.width * enemy["health"] / 3, 5)
                )

        # Enemy bullets
        for bullet in enemy_bullets:

            pygame.draw.rect(
                screen,
                RED,
                bullet.move(offset_x, offset_y),
                border_radius=4
            )

        # Particles
        draw_particles(screen)

        # HUD
        pygame.draw.rect(
            screen,
            (10, 20, 45),
            (10, 10, WIDTH - 20, 45),
            border_radius=10
        )

        draw_text(screen, f"SCORE: {score}", font, WHITE, 105, 32)
        draw_text(screen, f"LIVES: {lives}", font, CYAN, 450, 32)
        draw_text(screen, f"BEST: {high_score}", font, YELLOW, 770, 32)

        if game_state == PLAYING:
            draw_text(
                screen,
                "ESC: PAUSE",
                small_font,
                WHITE,
                WIDTH - 80,
                HEIGHT - 20
            )

    # ==============================================
    # 17. MAIN MENU
    # ==============================================

    if game_state == MENU:

        draw_text(
            screen,
            "GALAXY WAR",
            large_font,
            CYAN,
            WIDTH // 2,
            170
        )

        draw_text(
            screen,
            "SPACE SHOOTER",
            medium_font,
            WHITE,
            WIDTH // 2,
            225
        )

        draw_text(
            screen,
            "Defend the galaxy. Survive the invasion.",
            small_font,
            (170, 195, 225),
            WIDTH // 2,
            285
        )

        start_button = draw_button(
            screen,
            "START GAME",
            WIDTH // 2 - 110,
            340,
            220,
            55
        )

        draw_text(
            screen,
            f"HIGH SCORE: {high_score}",
            font,
            YELLOW,
            WIDTH // 2,
            445
        )

        draw_text(
            screen,
            "ARROWS / WASD: MOVE     SPACE: SHOOT",
            small_font,
            WHITE,
            WIDTH // 2,
            515
        )

        draw_text(
            screen,
            "ESC: QUIT",
            small_font,
            (140, 160, 190),
            WIDTH // 2,
            550
        )

    # ==============================================
    # 18. PAUSE SCREEN
    # ==============================================

    if game_state == PAUSED:

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        screen.blit(overlay, (0, 0))

        draw_text(
            screen,
            "PAUSED",
            large_font,
            CYAN,
            WIDTH // 2,
            245
        )

        draw_text(
            screen,
            "Press P or ESC to Resume",
            font,
            WHITE,
            WIDTH // 2,
            325
        )

        resume_button = draw_button(
            screen,
            "RESUME",
            WIDTH // 2 - 100,
            375,
            200,
            55
        )

    # ==============================================
    # 19. GAME OVER SCREEN
    # ==============================================

    if game_state == GAME_OVER:

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        draw_text(
            screen,
            "GAME OVER",
            large_font,
            RED,
            WIDTH // 2,
            215
        )

        draw_text(
            screen,
            f"YOUR SCORE: {score}",
            medium_font,
            WHITE,
            WIDTH // 2,
            290
        )

        draw_text(
            screen,
            f"BEST SCORE: {high_score}",
            font,
            YELLOW,
            WIDTH // 2,
            340
        )

        restart_button = draw_button(
            screen,
            "PLAY AGAIN",
            WIDTH // 2 - 110,
            395,
            220,
            55
        )

        menu_button = draw_button(
            screen,
            "MAIN MENU",
            WIDTH // 2 - 110,
            470,
            220,
            55
        )

        draw_text(
            screen,
            "Press R to Restart",
            small_font,
            WHITE,
            WIDTH // 2,
            555
        )

    # ==============================================
    # 20. DISPLAY UPDATE
    # ==============================================

    pygame.display.flip()

# ==================================================
# 21. EXIT
# ==================================================

pygame.quit()
sys.exit()
