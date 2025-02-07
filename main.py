import pygame, random, math, os

pygame.init()

# Game constants
SCREEN_WIDTH = int(os.getenv("SCREEN_WIDTH", 800))
SCREEN_HEIGHT = int(os.getenv("SCREEN_HEIGHT", 600))
PLAYER_SIZE = int(os.getenv("PLAYER_SIZE", 50))
GERM_SIZE = int(os.getenv("GERM_SIZE", 30))
PROJECTILE_SIZE = int(os.getenv("PROJECTILE_SIZE", 10))
GERM_PROJECTILE_SIZE = int(os.getenv("GERM_PROJECTILE_SIZE", 10))
GERM_SPEED = int(os.getenv("GERM_SPEED", 2))
PROJECTILE_SPEED = int(os.getenv("PROJECTILE_SPEED", 10))
PLAYER_SPEED = int(os.getenv("PLAYER_SPEED", 5))
GERM_DAMAGE = int(os.getenv("GERM_DAMAGE", 20))
GERM_PROJECTILE_SPEED = int(os.getenv("GERM_PROJECTILE_SPEED", 5))
SONIC_BOOM_DURATION = 5000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PLAYER_PROJECTILE_COLOR = WHITE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("No Germs Left!")

def generate_level(difficulty):
    level = []
    num_enemies = random.randint(5, 10) + (difficulty == "Hard") * 15
    for _ in range(num_enemies):
        germ_x = random.randint(0, SCREEN_WIDTH - GERM_SIZE)
        germ_y = random.randint(0, SCREEN_HEIGHT - GERM_SIZE)
        germ_type = random.choice(['virus', 'bacteria', 'fungus', 'germ'])
        level.append([germ_x, germ_y, germ_type])
    return level

def draw_player(screen, x, y, health):
    pygame.draw.rect(screen, WHITE, (x, y, PLAYER_SIZE, PLAYER_SIZE))
    font = pygame.font.Font(None, 36)
    health_text = font.render(f"Health: {health}", True, WHITE)
    screen.blit(health_text, (10, 10))

def draw_germs(screen, germs):
    for germ in germs:
        color = RED if germ[2] == 'virus' else YELLOW if germ[2] == 'bacteria' else BLUE if germ[2] == 'fungus' else GREEN
        pygame.draw.rect(screen, color, (germ[0], germ[1], GERM_SIZE, GERM_SIZE))

def draw_projectiles(screen, projectiles, is_germ_projectile=False):
    for projectile in projectiles:
        if is_germ_projectile:
            germ_type = projectile[4]
            color = RED if germ_type == 'virus' else YELLOW if germ_type == 'bacteria' else BLUE if germ_type == 'fungus' else GREEN
        else:
            color = PLAYER_PROJECTILE_COLOR
        pygame.draw.circle(screen, color, (int(projectile[0]), int(projectile[1])), PROJECTILE_SIZE)

def get_projectile_direction(start_pos, target_pos):
    dx = target_pos[0] - start_pos[0]
    dy = target_pos[1] - start_pos[1]
    distance = math.sqrt(dx ** 2 + dy ** 2)
    if distance == 0:
        return 0, 0
    return dx / distance, dy / distance

def check_collision(obj1, obj2, size1, size2):
    return (obj1[0] < obj2[0] + size2 and
            obj1[0] + size1 > obj2[0] and
            obj1[1] < obj2[1] + size2 and
            obj1[1] + size1 > obj2[1])

def display_message(message, size=74):
    screen.fill(BLACK)
    font = pygame.font.Font(None, size)
    text = font.render(message, True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - size // 4))
    pygame.display.flip()
    pygame.time.delay(1500)

def draw_menu():
    screen.fill(BLACK)
    font_title = pygame.font.Font(None, 74)
    title_text = font_title.render("No Germs Left!", True, WHITE)
    font_start = pygame.font.Font(None, 36)
    start_text = font_start.render("Press Enter to Start", True, WHITE)
    font_quit = pygame.font.Font(None, 36)
    font_credits = pygame.font.Font(None, 24)
    credits_text = font_credits.render("A game made by: Delta Studios", True, WHITE)
    
    screen.blit(title_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
    screen.blit(credits_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 150))

    pygame.display.flip()

def show_difficulty_menu():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    title_text = font.render("Select Difficulty", True, WHITE)
    easy_text = pygame.font.Font(None, 36).render("1. Easy", True, WHITE)
    medium_text = pygame.font.Font(None, 36).render("2. Medium", True, WHITE)
    hard_text = pygame.font.Font(None, 36).render("3. Hard", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100))
    screen.blit(easy_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
    screen.blit(medium_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))
    screen.blit(hard_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100))
    pygame.display.flip()

def game_loop(difficulty):
    running = True
    clock = pygame.time.Clock()
    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_HEIGHT // 2
    level = generate_level(difficulty)
    projectiles = []
    germ_projectiles = []
    germs = [[x, y, t] for x, y, t in level]
    player_health = 100
    game_won = False
    paused = False
    sonic_boom_mode = False
    sonic_boom_end_time = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    direction = get_projectile_direction((player_x + PLAYER_SIZE // 2, player_y + PLAYER_SIZE // 2), (mouse_x, mouse_y))
                    projectiles.append([player_x + PLAYER_SIZE // 2, player_y + PLAYER_SIZE // 2, direction[0], direction[1]])
                elif event.button == 3:
                    sonic_boom_mode = True
                    sonic_boom_end_time = pygame.time.get_ticks() + SONIC_BOOM_DURATION

        if paused:
            display_message("Paused", 74)
            continue

        if sonic_boom_mode and pygame.time.get_ticks() > sonic_boom_end_time:
            sonic_boom_mode = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player_x -= PLAYER_SPEED
        if keys[pygame.K_d]:
            player_x += PLAYER_SPEED
        if keys[pygame.K_w]:
            player_y -= PLAYER_SPEED
        if keys[pygame.K_s]:
            player_y += PLAYER_SPEED

        for projectile in projectiles[:]:
            projectile[0] += projectile[2] * PROJECTILE_SPEED
            projectile[1] += projectile[3] * PROJECTILE_SPEED
            if (projectile[0] < 0 or projectile[0] > SCREEN_WIDTH or
                projectile[1] < 0 or projectile[1] > SCREEN_HEIGHT):
                projectiles.remove(projectile)
            else:
                for germ in germs[:]:
                    if check_collision([projectile[0], projectile[1]], germ, PROJECTILE_SIZE, GERM_SIZE):
                        germs.remove(germ)
                        projectiles.remove(projectile)
                        break

        new_germs = []
        for germ in germs:
            if sonic_boom_mode:
                direction = get_projectile_direction((player_x + PLAYER_SIZE // 2, player_y + PLAYER_SIZE // 2), (germ[0] + GERM_SIZE // 2, germ[1] + GERM_SIZE // 2))
                germ[0] -= direction[0] * GERM_SPEED * 5
                germ[1] -= direction[1] * GERM_SPEED * 5
            else:
                if germ[2] == 'virus':
                    if player_x < germ[0]:
                        germ[0] -= GERM_SPEED
                    elif player_x > germ[0]:
                        germ[0] += GERM_SPEED
                    if player_y < germ[1]:
                        germ[1] -= GERM_SPEED
                    elif player_y > germ[1]:
                        germ[1] += GERM_SPEED
            new_germs.append(germ)

        germs = new_germs

        for germ in germs:
            if random.random() < 0.01:
                direction = get_projectile_direction((germ[0] + GERM_SIZE // 2, germ[1] + GERM_SIZE // 2), (player_x + PLAYER_SIZE // 2, player_y + PLAYER_SIZE // 2))
                germ_projectiles.append([germ[0] + GERM_SIZE // 2, germ[1] + GERM_SIZE // 2, direction[0], direction[1], germ[2]])

        for germ_projectile in germ_projectiles[:]:
            germ_projectile[0] += germ_projectile[2] * GERM_PROJECTILE_SPEED
            germ_projectile[1] += germ_projectile[3] * GERM_PROJECTILE_SPEED
            if (germ_projectile[0] < 0 or germ_projectile[0] > SCREEN_WIDTH or
                germ_projectile[1] < 0 or germ_projectile[1] > SCREEN_HEIGHT):
                germ_projectiles.remove(germ_projectile)
            elif check_collision([germ_projectile[0], germ_projectile[1]], [player_x, player_y], GERM_PROJECTILE_SIZE, PLAYER_SIZE):
                germ_projectiles.remove(germ_projectile)
                player_health -= GERM_DAMAGE
                if player_health <= 0:
                    running = False
                    game_won = False
                    display_message("Game Over")

        if not germs:
            game_won = True
            running = False
            display_message("You Win!")

        screen.fill(BLACK)
        draw_player(screen, player_x, player_y, player_health)
        draw_germs(screen, germs)
        draw_projectiles(screen, projectiles)
        draw_projectiles(screen, germ_projectiles, is_germ_projectile=True)
        
        pygame.display.flip()
        clock.tick(60)

    return game_won

def main():
    while True:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    show_difficulty_menu()
                    selecting_difficulty = True
                    while selecting_difficulty:
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_1:
                                    selecting_difficulty = False
                                    difficulty = "Easy"
                                elif event.key == pygame.K_2:
                                    selecting_difficulty = False
                                    difficulty = "Medium"
                                elif event.key == pygame.K_3:
                                    selecting_difficulty = False
                                    difficulty = "Hard"
                                    break
                    game_won = game_loop(difficulty)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

if __name__ == "__main__":
	main()
