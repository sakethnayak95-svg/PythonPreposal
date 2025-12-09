import pygame
import random

pygame.init()
pygame.mixer.init()

timer = pygame.time.Clock()
fps = 60

white = (255, 255, 255)
black = (0, 0, 0)
gray = (128, 128, 128)
red = (255, 80, 80)
orange = (255, 160, 60)
green = (0, 255, 0)
blue = (120, 200, 255)
purple = (180, 120, 255)
yellow = (255, 255, 80)
colors = [red, orange, yellow, blue, purple]
POWERUP_SIZE = 20

sound_laser = pygame.mixer.Sound("laser.wav")
sound_laser.set_volume(0.6)
sound_paddle = pygame.mixer.Sound("paddle_hit.wav")
sound_brick = pygame.mixer.Sound("brick_hit.wav")
sound_powerup = pygame.mixer.Sound("powerup.wav")
sound_win = pygame.mixer.Sound("win.wav")
sound_gameover = pygame.mixer.Sound("gameover.wav")

powerup_images = {
    "extra_life": pygame.image.load("extra_life.png"),
    "slow_ball": pygame.image.load("slow_ball.png"),
    "expand_paddle": pygame.image.load("expand_paddle.png"),
    "multiball": pygame.image.load("multiball.png"),
    "laser": pygame.image.load("laser.png"),
    "sticky": pygame.image.load("sticky.png"),
    "shrink_paddle": pygame.image.load("shrink_paddle.png"),
    "speed_up": pygame.image.load("speed_up.png"),
}
for key in powerup_images:
    powerup_images[key] = pygame.transform.scale(powerup_images[key], (POWERUP_SIZE, POWERUP_SIZE))

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Breakout Clone with Powerups + Levels")
background = pygame.image.load("Breakout game background image.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

player_speed = 8
player_width = 150
player_height = 15
player_x = WIDTH // 2 - player_width // 2
player_direction = 0
paddle_expanded = False
expand_timer = 0

ball_radius = 10
ball_x_speed = 5
ball_y_speed = 5

balls = []

sticky_active = False         
laser_active = False
laser_start_time = 0
LASER_DURATION = 5000

lasers = []
LASER_SPEED = 10

score = 0
lives = 3

current_level = 1
max_level = 3
board = []
create_new = True

powerups = []
POWERUP_SPEED = 3
POWERUP_TYPES = [
    "extra_life",
    "slow_ball",
    "expand_paddle",
    "multiball",
    "laser",
    "sticky",
    "shrink_paddle",
    "speed_up"
]

font = pygame.font.Font('freesansbold.ttf', 30)

def create_level(level):
    board = []
    rows = 5
    cols = 8

    if level == 1:
        for _ in range(rows):
            row = [random.randint(1, 5) for _ in range(cols)]
            board.append(row)

    elif level == 2:
        for i in range(rows):
            row = [0] * cols
            for j in range(i, cols - i):
                row[j] = random.randint(1, 5)
            board.append(row)

    elif level == 3:
        for i in range(rows):
            row = []
            for j in range(cols):
                if (i + j) % 2 == 0:
                    row.append(random.randint(1, 5))
                else:
                    row.append(0)
            board.append(row)

    return board

def draw_board(board):
    board_squares = []
    brick_width = WIDTH // 8 - 4
    brick_height = 40

    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] > 0:
                piece = pygame.draw.rect(
                    screen,
                    colors[(board[i][j]) - 1],
                    [j * (brick_width + 4) + 2, i * (brick_height + 2) + 2, brick_width, brick_height],
                    0, 5
                )
                pygame.draw.rect(
                    screen, black,
                    [j * (brick_width + 4) + 2, i * (brick_height + 2) + 2, brick_width, brick_height],
                    3, 5
                )

                top = pygame.Rect(j * (brick_width + 4) + 2, i * (brick_height + 2) + 2, brick_width, 1)
                bot = pygame.Rect(j * (brick_width + 4) + 2, i * (brick_height + 2) + brick_height + 1, brick_width, 1)
                left = pygame.Rect(j * (brick_width + 4) + 2, i * (brick_height + 2) + 2, 1, brick_height)
                right = pygame.Rect(j * (brick_width + 4) + brick_width + 1, i * (brick_height + 2) + 2, 1, brick_height)

                board_squares.append([top, bot, left, right, (i, j)])

    return board_squares

def spawn_powerup(x, y):
    power_type = random.choice(POWERUP_TYPES)
    rect = pygame.Rect(x - POWERUP_SIZE//2, y - POWERUP_SIZE//2, POWERUP_SIZE, POWERUP_SIZE)
    return {"rect": rect, "type": power_type}

run = True


balls = [{"x": WIDTH/2, "y": HEIGHT-40, "dx": 0, "dy": 0, "stuck": False}]
active = False

while run:
    screen.blit(background, (0, 0))
    timer.tick(fps)

    
    if create_new:
        if current_level > max_level:
            sound_win.play()
            screen.fill(black)
            finish_text = font.render(f'You won! Final Score: {score}', True, white)
            screen.blit(finish_text, (WIDTH//2 - finish_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(5000)
            break

        board = create_level(current_level)
        create_new = False

    squares = draw_board(board)

    
    player = pygame.draw.rect(screen, black, [player_x, HEIGHT - 30, player_width, player_height], 0, 5)
    pygame.draw.rect(screen, white, [player_x + 5, HEIGHT - 28, player_width - 10, player_height - 4], 3, 5)

    
    for b in balls:
        pygame.draw.circle(screen, white, (int(b["x"]), int(b["y"])), ball_radius)
        pygame.draw.circle(screen, black, (int(b["x"]), int(b["y"])), ball_radius, 3)

    
    for p in powerups:
        img = powerup_images[p["type"]]
        screen.blit(img, (p["rect"].x, p["rect"].y))

    
    for laser in lasers:
        pygame.draw.rect(screen, red, (laser["x"], laser["y"], 4, 12))

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:

            
            if event.key == pygame.K_SPACE:
                if not active:
                    active = True
                    for b in balls:
                        b["dx"] = random.choice([-1, 1])
                        b["dy"] = -1

                
                released = False
                for b in balls:
                    if b["stuck"]:
                        b["stuck"] = False
                        b["dx"] = random.choice([-1, 1])
                        b["dy"] = -1
                        released = True

                if released:
                    sticky_active = False

            
            if event.key == pygame.K_RIGHT:
                player_direction = 1
            if event.key == pygame.K_LEFT:
                player_direction = -1

            
            if event.key == pygame.K_f and laser_active:
                lasers.append({"x": player_x + 10, "y": HEIGHT - 50})
                lasers.append({"x": player_x + player_width - 14, "y": HEIGHT - 50})
                sound_laser.play()

        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_RIGHT, pygame.K_LEFT]:
                player_direction = 0

    
    for p in powerups[:]:
        p["rect"].y += POWERUP_SPEED

        if p["rect"].colliderect(player):
            sound_powerup.play()

            if p["type"] == "extra_life":
                lives += 1

            elif p["type"] == "slow_ball":
                ball_x_speed = max(2, ball_x_speed * 0.7)
                ball_y_speed = max(2, ball_y_speed * 0.7)

            elif p["type"] == "expand_paddle":
                player_width = 250
                paddle_expanded = True
                expand_timer = 300

            elif p["type"] == "multiball":
                for _ in range(2):
                    balls.append({
                        "x": balls[0]["x"],
                        "y": balls[0]["y"],
                        "dx": random.choice([-1, 1]),
                        "dy": -1,
                        "stuck": False   
                    })

            elif p["type"] == "laser":
                laser_active = True
                laser_start_time = pygame.time.get_ticks()   


            elif p["type"] == "sticky":
                sticky_active = True

            elif p["type"] == "shrink_paddle":
                player_width = max(80, player_width - 40)

            elif p["type"] == "speed_up":
                ball_x_speed *= 1.3
                ball_y_speed *= 1.3

            powerups.remove(p)

        elif p["rect"].top > HEIGHT:
            powerups.remove(p)

    
    if laser_active:
        if pygame.time.get_ticks() - laser_start_time >= LASER_DURATION:
            laser_active = False


    
    for laser in lasers[:]:
        laser["y"] -= LASER_SPEED

        if laser["y"] < 0:
            lasers.remove(laser)
            continue

        for sq in squares:
            i, j = sq[4]
            brick_width = WIDTH // 8 - 4
            brick_height = 40

            brick_rect = pygame.Rect(
                j * (brick_width + 4) + 2,
                i * (brick_height + 2) + 2,
                brick_width,
                brick_height
            )

            laser_rect = pygame.Rect(laser["x"], laser["y"], 4, 12)

            if laser_rect.colliderect(brick_rect):
                if board[i][j] > 1:
                    board[i][j] -= 1
                else:
                    board[i][j] = 0
                    score += 1
                lasers.remove(laser)
                break

    
    if paddle_expanded:
        expand_timer -= 1
        if expand_timer <= 0:
            paddle_expanded = False
            player_width = 150

    
    player_x += player_direction * player_speed
    if player_x < 0:
        player_x = 0
    if player_x + player_width > WIDTH:
        player_x = WIDTH - player_width

    
    for b in balls[:]:

        
        if b["stuck"]:
            b["x"] = player_x + player_width//2
            b["y"] = HEIGHT - 50
            continue

        b["x"] += b["dx"] * ball_x_speed
        b["y"] += b["dy"] * ball_y_speed

        ball_rect = pygame.Rect(b["x"] - ball_radius, b["y"] - ball_radius,
                                ball_radius*2, ball_radius*2)

        
        if b["x"] <= ball_radius or b["x"] >= WIDTH - ball_radius:
            b["dx"] *= -1

        if b["y"] <= ball_radius:
            b["dy"] *= -1

        
        if ball_rect.colliderect(player):
            sound_paddle.play()

            if sticky_active:
                b["stuck"] = True   
                b["dx"] = 0
                b["dy"] = 0
            else:
                b["dy"] *= -1

        
        for sq in squares:
            if ball_rect.colliderect(sq[0]) or ball_rect.colliderect(sq[1]):
                sound_brick.play()
                b["dy"] *= -1
                board[sq[4][0]][sq[4][1]] -= 1
                score += 1

                if random.random() < 0.25:
                    powerups.append(spawn_powerup(sq[0].x, sq[0].y))
                break

            if ball_rect.colliderect(sq[2]) or ball_rect.colliderect(sq[3]):
                sound_brick.play()
                b["dx"] *= -1
                board[sq[4][0]][sq[4][1]] -= 1
                score += 1
                break

        
        if b["y"] > HEIGHT:
            balls.remove(b)

    
    if len(balls) == 0:
        lives -= 1
        if lives <= 0:
            sound_gameover.play()
            screen.fill(black)
            over_text = font.render(f'Game Over! Final Score: {score}', True, white)
            screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(5000)
            break

        balls = [{"x": WIDTH/2, "y": HEIGHT-40, "dx": 0, "dy": 0, "stuck": False}]
        active = False
        powerups.clear()
        sticky_active = False
        ball_x_speed = 5
        ball_y_speed = 5

    
    if all(all(cell <= 0 for cell in row) for row in board):
        current_level += 1
        create_new = True
        balls = [{"x": WIDTH/2, "y": HEIGHT-40, "dx": 0, "dy": 0, "stuck": False}]
        active = False
        powerups.clear()

    
    screen.blit(font.render(f'Score: {score}', True, white), (10, 5))
    screen.blit(font.render(f'Lives: {lives}', True, white), (WIDTH - 140, 5))
    screen.blit(font.render(f'Level: {current_level}', True, white), (WIDTH//2 - 60, 5))

    if not active:
        start_text = font.render('Press SPACE to start', True, white)
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))

    pygame.display.flip()

pygame.quit()
