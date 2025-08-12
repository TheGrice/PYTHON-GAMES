import pygame
import sys
import random
import os

pygame.init()

WIDTH, HEIGHT = 1280, 720
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("game")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PURPLE = (150, 0, 150)

font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 25)

player_size = 50
player_speed = 15
enemy_size = 50
base_enemy_speed = 3
power_up_size = 30

HIGH_SCORE_FILE = "highscore.txt"

def load_high_score():
    if not os.path.isfile(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write("0")
        return 0
    with open(HIGH_SCORE_FILE, "r") as f:
        try:
            return int(f.read())
        except:
            return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))

def draw_text(surface, text, font, color, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

def main_menu(high_score):
    selected = 0
    options = ["Single Player", "Two Player", "Quit"]

    while True:
        window.fill(BLACK)

        draw_text(window, "MAIN MENU", font, YELLOW, WIDTH // 2, HEIGHT // 5)
        draw_text(window, f"High Score: {high_score}", small_font, WHITE, WIDTH // 2, HEIGHT // 5 + 50)

        for i, option in enumerate(options):
            color = GREEN if i == selected else WHITE
            draw_text(window, option, font, color, WIDTH // 2, HEIGHT // 2 + i * 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if options[selected] == "Single Player":
                        score = game_loop(high_score, two_player=False)
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
                    elif options[selected] == "Two Player":
                        score = game_loop(high_score, two_player=True)
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
                    elif options[selected] == "Quit":
                        pygame.quit()
                        sys.exit()

def draw_boss(surface, pos, health, max_health):
    boss_rect = pygame.Rect(pos[0], pos[1], boss_size, boss_size)
    pygame.draw.rect(surface, PURPLE, boss_rect)
    # Health bar
    health_bar_width = boss_size
    health_bar_height = 10
    health_ratio = health / max_health
    pygame.draw.rect(surface, RED, (pos[0], pos[1] - 15, health_bar_width, health_bar_height))
    pygame.draw.rect(surface, GREEN, (pos[0], pos[1] - 15, health_bar_width * health_ratio, health_bar_height))

def game_loop(high_score, two_player=False):
    
    player1_pos = [WIDTH // 4, HEIGHT // 2]
    player2_pos = [WIDTH * 3 // 4, HEIGHT // 2]

    powered_up1 = False
    powered_up2 = False
    power_up_duration = 5000  
    power_up_end_time1 = 0
    power_up_end_time2 = 0

    enemies = []
    num_enemies = 5
    enemy_speed = base_enemy_speed
    max_enemies = 15

    for _ in range(num_enemies):
        x = random.randint(0, WIDTH - enemy_size)
        y = random.randint(0, HEIGHT - enemy_size)
        direction = random.choice(['left', 'right', 'up', 'down'])
        enemies.append({'pos': [x, y], 'dir': direction})

    power_up_pos = [random.randint(0, WIDTH - power_up_size), random.randint(0, HEIGHT - power_up_size)]
    power_up_visible = True
    power_up_respawn_time = 7000  
    power_up_last_collected = 0

    score = 0
    level = 1
    level_up_interval = 30000 
    last_level_up_time = pygame.time.get_ticks()

    global boss_size
    boss_active = False
    boss_health = 20
    boss_size = 100
    boss_pos = [WIDTH // 2 - boss_size // 2, 50]
    boss_speed = 2
    boss_direction = 1  

    boss_projectiles = []
    projectile_size = 10
    projectile_speed = 7

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(30)

        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
      
        if keys[pygame.K_LEFT]:
            player1_pos[0] -= player_speed
        if keys[pygame.K_RIGHT]:
            player1_pos[0] += player_speed
        if keys[pygame.K_UP]:
            player1_pos[1] -= player_speed
        if keys[pygame.K_DOWN]:
            player1_pos[1] += player_speed

      
        if two_player:
            if keys[pygame.K_a]:
                player2_pos[0] -= player_speed
            if keys[pygame.K_d]:
                player2_pos[0] += player_speed
            if keys[pygame.K_w]:
                player2_pos[1] -= player_speed
            if keys[pygame.K_s]:
                player2_pos[1] += player_speed

       
        player1_pos[0] = max(0, min(WIDTH - player_size, player1_pos[0]))
        player1_pos[1] = max(0, min(HEIGHT - player_size, player1_pos[1]))
        player2_pos[0] = max(0, min(WIDTH - player_size, player2_pos[0]))
        player2_pos[1] = max(0, min(HEIGHT - player_size, player2_pos[1]))

    
        if current_time - last_level_up_time > level_up_interval:
            level += 1
            last_level_up_time = current_time
            enemy_speed += 1 
            if len(enemies) < max_enemies:
                x = random.randint(0, WIDTH - enemy_size)
                y = random.randint(0, HEIGHT - enemy_size)
                direction = random.choice(['left', 'right', 'up', 'down'])
                enemies.append({'pos': [x, y], 'dir': direction})

        
        if level >= 5 and not boss_active:
            boss_active = True
            boss_health = 20
            boss_pos = [WIDTH // 2 - boss_size // 2, 50]
            boss_projectiles.clear()

      
        for enemy in enemies:
            x, y = enemy['pos']
            d = enemy['dir']

            if d == 'left':
                x -= enemy_speed
                if x < 0:
                    x = 0
                    enemy['dir'] = 'right'
            elif d == 'right':
                x += enemy_speed
                if x > WIDTH - enemy_size:
                    x = WIDTH - enemy_size
                    enemy['dir'] = 'left'
            elif d == 'up':
                y -= enemy_speed
                if y < 0:
                    y = 0
                    enemy['dir'] = 'down'
            elif d == 'down':
                y += enemy_speed
                if y > HEIGHT - enemy_size:
                    y = HEIGHT - enemy_size
                    enemy['dir'] = 'up'

            enemy['pos'] = [x, y]

        player1_rect = pygame.Rect(player1_pos[0], player1_pos[1], player_size, player_size)
        player2_rect = pygame.Rect(player2_pos[0], player2_pos[1], player_size, player_size)

   
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy['pos'][0], enemy['pos'][1], enemy_size, enemy_size)
            if player1_rect.colliderect(enemy_rect):
                if not powered_up1:
                    show_game_over(score, high_score)
                    return score
            if two_player and player2_rect.colliderect(enemy_rect):
                if not powered_up2:
                    show_game_over(score, high_score)
                    return score

        power_up_rect = pygame.Rect(power_up_pos[0], power_up_pos[1], power_up_size, power_up_size)

     
        if power_up_visible and (player1_rect.colliderect(power_up_rect) or (two_player and player2_rect.colliderect(power_up_rect))):
            powered_up1 = True
            powered_up2 = True
            power_up_visible = False
            power_up_last_collected = current_time
            power_up_end_time1 = power_up_last_collected + power_up_duration
            power_up_end_time2 = power_up_last_collected + power_up_duration

        # Power-up timers
        if powered_up1 and current_time > power_up_end_time1:
            powered_up1 = False
        if powered_up2 and current_time > power_up_end_time2:
            powered_up2 = False

        if not power_up_visible and current_time > power_up_last_collected + power_up_respawn_time:
            power_up_pos = [random.randint(0, WIDTH - power_up_size), random.randint(0, HEIGHT - power_up_size)]
            power_up_visible = True

        score += 1

        window.fill(BLACK)

        # Draw players
        player1_color = GREEN if powered_up1 else WHITE
        pygame.draw.rect(window, player1_color, player1_rect)
        if two_player:
            player2_color = CYAN if powered_up2 else MAGENTA
            pygame.draw.rect(window, player2_color, player2_rect)

        # Draw enemies
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy['pos'][0], enemy['pos'][1], enemy_size, enemy_size)
            pygame.draw.rect(window, RED, enemy_rect)

        # Draw power-up
        if power_up_visible:
            pygame.draw.rect(window, BLUE, power_up_rect)

        # Boss fight logic and drawing
        if boss_active:
            # Move boss left and right
            boss_pos[0] += boss_speed * boss_direction
            if boss_pos[0] <= 0 or boss_pos[0] >= WIDTH - boss_size:
                boss_direction *= -1

            # Boss shoots projectiles occasionally
            if random.randint(0, 50) == 0:
                proj_x = boss_pos[0] + boss_size // 2 - projectile_size // 2
                proj_y = boss_pos[1] + boss_size
                boss_projectiles.append([proj_x, proj_y])

            # Move projectiles
            for proj in boss_projectiles[:]:
                proj[1] += projectile_speed
                if proj[1] > HEIGHT:
                    boss_projectiles.remove(proj)

            # Draw boss and projectiles
            draw_boss(window, boss_pos, boss_health, 20)
            for proj in boss_projectiles:
                pygame.draw.rect(window, CYAN, (*proj, projectile_size, projectile_size))

            # Boss collision with players' powered-up hit to damage boss
            if powered_up1:
                if player1_rect.colliderect(pygame.Rect(boss_pos[0], boss_pos[1], boss_size, boss_size)):
                    boss_health -= 1
                    powered_up1 = False  # Lose power-up on hit
            if two_player and powered_up2:
                if player2_rect.colliderect(pygame.Rect(boss_pos[0], boss_pos[1], boss_size, boss_size)):
                    boss_health -= 1
                    powered_up2 = False

            # If boss defeated
            if boss_health <= 0:
                boss_active = False
                score += 1000  # big bonus
                # Brief power-up for players after boss
                powered_up1 = True
                powered_up2 = True
                power_up_end_time1 = current_time + power_up_duration
                power_up_end_time2 = current_time + power_up_duration
                boss_projectiles.clear()

            # Boss projectiles collide with players (cause game over if not powered up)
            for proj in boss_projectiles[:]:
                proj_rect = pygame.Rect(proj[0], proj[1], projectile_size, projectile_size)
                if player1_rect.colliderect(proj_rect):
                    if not powered_up1:
                        show_game_over(score, high_score)
                        return score
                    else:
                        boss_projectiles.remove(proj)
                if two_player and player2_rect.colliderect(proj_rect):
                    if not powered_up2:
                        show_game_over(score, high_score)
                        return score
                    else:
                        boss_projectiles.remove(proj)

        # Draw score and level
        draw_text(window, f"Score: {score}", small_font, WHITE, 70, 20)
        draw_text(window, f"Level: {level}", small_font, WHITE, WIDTH - 70, 20)

        pygame.display.flip()

def show_game_over(score, high_score):
    window.fill(BLACK)
    draw_text(window, "GAME OVER", font, RED, WIDTH // 2, HEIGHT // 3)
    draw_text(window, f"Your Score: {score}", font, WHITE, WIDTH // 2, HEIGHT // 3 + 50)
    draw_text(window, f"High Score: {high_score}", font, WHITE, WIDTH // 2, HEIGHT // 3 + 100)
    draw_text(window, "Press ENTER to return to main menu", small_font, YELLOW, WIDTH // 2, HEIGHT * 2 // 3)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    waiting = False

if __name__ == "__main__":
    high_score = load_high_score()
    main_menu(high_score)

