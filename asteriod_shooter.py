import pygame
import random
import math
import os

# --- Constants ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
MAGENTA = (255, 0, 255)
FPS = 60
HIGH_SCORE_FILE = "highscore.txt"

# --- Game Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroid Shooter (Python Only)")
clock = pygame.time.Clock()
font_name = pygame.font.match_font('arial')

# --- Helper Functions ---
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'r') as f:
            try:
                return int(f.read())
            except ValueError:
                return 0
    return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, 'w') as f:
        f.write(str(score))

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(midtop=(x, y))
    surf.blit(text_surface, text_rect)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect(topleft=(x + 30 * i, y))
        surf.blit(img, img_rect)

# --- Game Object Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_orig = pygame.Surface((30, 20), pygame.SRCALPHA)
        pygame.draw.polygon(self.image_orig, GREEN, [(0, 0), (30, 10), (0, 20)])
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.radius = 12
        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.rotation_speed = 4.5
        self.thrust_power = 0.5
        self.brake_power = 0.1
        self.friction = -0.05
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.mini_img = pygame.transform.scale(self.image_orig, (15, 10))

    def update(self):
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1500:
            self.hidden = False
            self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            self.pos = pygame.math.Vector2(self.rect.center)
        if self.hidden: return

        # Start with default friction
        acc = self.vel * self.friction

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.rotate(-1)
        if keys[pygame.K_RIGHT]: self.rotate(1)
        if keys[pygame.K_UP]: self.thrust()
        
        # Add braking force if DOWN arrow is pressed
        if keys[pygame.K_DOWN]:
            if self.vel.length() > 0:
                brake_acc = -self.vel.normalize() * self.brake_power
                acc += brake_acc

        self.vel += acc
        self.pos += self.vel
        self.rect.center = self.pos
        self.wrap_around_screen()

    def rotate(self, direction):
        self.angle = (self.angle + self.rotation_speed * direction) % 360
        self.image = pygame.transform.rotate(self.image_orig, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def thrust(self):
        rad_angle = math.radians(self.angle)
        self.vel.x += self.thrust_power * math.cos(rad_angle)
        self.vel.y += self.thrust_power * math.sin(rad_angle)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            rad_angle = math.radians(self.angle)
            bullet = Bullet(self.rect.center, rad_angle)
            all_sprites.add(bullet)
            bullets.add(bullet)

    def wrap_around_screen(self):
        if self.pos.x > SCREEN_WIDTH + self.radius: self.pos.x = -self.radius
        if self.pos.x < -self.radius: self.pos.x = SCREEN_WIDTH + self.radius
        if self.pos.y > SCREEN_HEIGHT + self.radius: self.pos.y = -self.radius
        if self.pos.y < -self.radius: self.pos.y = SCREEN_HEIGHT + self.radius

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT * 2)
        self.vel = pygame.math.Vector2(0, 0)

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, size='large', position=None, speed_mult=1.0):
        super().__init__()
        self.size = size
        radii = {'large': 40, 'medium': 20, 'small': 10}
        self.radius = radii[self.size]
        
        self.image_orig = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image_orig, WHITE, (self.radius, self.radius), self.radius, 2)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        
        if position is None:
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            if edge == 'top': self.rect.center = (random.randint(0, SCREEN_WIDTH), -self.radius)
            if edge == 'bottom': self.rect.center = (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + self.radius)
            if edge == 'left': self.rect.center = (-self.radius, random.randint(0, SCREEN_HEIGHT))
            if edge == 'right': self.rect.center = (SCREEN_WIDTH + self.radius, random.randint(0, SCREEN_HEIGHT))
        else:
            self.rect.center = position
            
        self.speedx = random.uniform(-1.5, 1.5) * speed_mult
        self.speedy = random.uniform(-1.5, 1.5) * speed_mult
        self.rot = 0
        self.rot_speed = random.uniform(-2, 2)

    def update(self):
        self.rect.move_ip(self.speedx, self.speedy)
        old_center = self.rect.center
        self.rot = (self.rot + self.rot_speed) % 360
        self.image = pygame.transform.rotate(self.image_orig, self.rot)
        self.rect = self.image.get_rect(center=old_center)
        if self.rect.left > SCREEN_WIDTH: self.rect.right = 0
        if self.rect.right < 0: self.rect.left = SCREEN_WIDTH
        if self.rect.top > SCREEN_HEIGHT: self.rect.bottom = 0
        if self.rect.bottom < 0: self.rect.top = SCREEN_HEIGHT

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super().__init__()
        self.image = pygame.Surface((6, 6))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=pos)
        self.vel = pygame.math.Vector2(12 * math.cos(angle), 12 * math.sin(angle))
        
    def update(self):
        self.rect.center += self.vel
        if not screen.get_rect().contains(self.rect): self.kill()

class Powerup(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.type = 'gun'
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, MAGENTA, (10, 10), 10)
        self.rect = self.image.get_rect(center=center)
        
    def update(self):
        self.rect.y += 2
        if self.rect.top > SCREEN_HEIGHT: self.kill()

class UFO(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, RED, self.image.get_rect())
        self.rect = self.image.get_rect()
        self.radius = 20
        self.direction = random.choice([-1, 1])
        self.rect.centery = random.randint(50, SCREEN_HEIGHT - 50)
        self.rect.centerx = -self.radius if self.direction == 1 else SCREEN_WIDTH + self.radius
        self.speedx = 2 * self.direction
        self.shoot_delay = 1000
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speedx
        if (self.direction == 1 and self.rect.left > SCREEN_WIDTH) or \
           (self.direction == -1 and self.rect.right < 0): self.kill()
        self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            angle = math.atan2(player.rect.centery - self.rect.centery, player.rect.centerx - self.rect.centerx)
            bullet = Bullet(self.rect.center, angle)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

def show_screen(title, line1, line2, score_val=None, high_score_val=None):
    screen.fill(BLACK)
    draw_text(screen, title, 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
    draw_text(screen, line1, 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    if score_val is not None:
         draw_text(screen, f"Your Score: {score_val}", 30, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40)
    if high_score_val is not None:
        draw_text(screen, f"High Score: {high_score_val}", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)
    if score_val is not None and score_val > high_score_val:
        draw_text(screen, "NEW HIGH SCORE!", 22, SCREEN_WIDTH/2, SCREEN_HEIGHT/2+80)
    draw_text(screen, line2, 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYUP and event.key == pygame.K_RETURN: waiting = False

# --- Main Game Loop ---
high_score = load_high_score()
game_over = True
running = True

while running:
    if game_over:
        current_score = score if 'score' in locals() else None
        if current_score is not None:
            if current_score > high_score:
                high_score = current_score
                save_high_score(high_score)
            show_screen("GAME OVER", "", "Press ENTER to play again", current_score, high_score)
        else:
            show_screen("ASTEROID SHOOTER", "Arrow keys to move, SPACE to shoot", "Press ENTER to begin", high_score_val=high_score)
            
        # Reset the game
        game_over = False
        all_sprites = pygame.sprite.Group()
        asteroids = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        ufos = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        wave = 1
        for i in range(wave * 4):
            a = Asteroid(speed_mult=1)
            all_sprites.add(a)
            asteroids.add(a)
        score = 0
        ufo_timer = pygame.time.get_ticks()

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # --- Updates ---
    all_sprites.update()
    if pygame.time.get_ticks() - ufo_timer > 20000 and len(ufos) == 0:
        ufo = UFO()
        all_sprites.add(ufo)
        ufos.add(ufo)

    # --- Collision Checks ---
    # Asteroids vs. Bullets
    hits = pygame.sprite.groupcollide(asteroids, bullets, True, True)
    for hit in hits:
        if hit.size == 'large':
            score += 10
            sizes = ['medium'] * 2
        elif hit.size == 'medium':
            score += 20
            sizes = ['small'] * 2
        else:
            score += 50
            sizes = []
        for size in sizes:
            a = Asteroid(size, hit.rect.center, wave * 0.5 + 1)
            all_sprites.add(a)
            asteroids.add(a)
        if random.random() > 0.9:
            pow = Powerup(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
    
    # UFO vs. Bullets
    if pygame.sprite.groupcollide(ufos, bullets, True, True):
        score += 200
        
    # Player vs. Powerups
    for hit in pygame.sprite.spritecollide(player, powerups, True):
        if hit.type == 'gun':
            player.shoot_delay = 100
            player.powerup_time = pygame.time.get_ticks()
        
    if player.shoot_delay < 250 and pygame.time.get_ticks() - getattr(player, 'powerup_time', 0) > 7000:
        player.shoot_delay = 250
        
    # Player vs. Dangers
    if not player.hidden:
        player_hit = pygame.sprite.spritecollide(player, asteroids, True, pygame.sprite.collide_circle) or \
                     pygame.sprite.spritecollide(player, ufos, True, pygame.sprite.collide_circle) or \
                     pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_circle)
        if player_hit:
            player.hide()
            player.lives -= 1
            if player.lives <= 0:
                game_over = True
            
    # New Wave
    if len(asteroids) == 0 and not game_over:
        wave += 1
        for i in range(wave * 4):
            a = Asteroid(speed_mult=1 + wave * 0.1)
            all_sprites.add(a)
            asteroids.add(a)

    # --- Drawing ---
    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_text(screen, f"Score: {score}", 18, SCREEN_WIDTH / 2, 10)
    draw_text(screen, f"Wave: {wave}", 18, SCREEN_WIDTH - 50, 10)
    draw_lives(screen, 10, 10, player.lives, player.mini_img)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()