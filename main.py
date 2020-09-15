import os
import time
import random
import pygame
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Loading images
SPACESHIP_RED = [pygame.image.load(os.path.join(
    "assets", "enemy_red0.png")), pygame.image.load(os.path.join("assets", "enemy_red1.png"))]
SPACESHIP_GREEN = [pygame.image.load(os.path.join("assets", "enemy_green_0.png")), pygame.image.load(
    os.path.join("assets", "enemy_green_1.png")), pygame.image.load(
    os.path.join("assets", "enemy_green_2.png")), pygame.image.load(
    os.path.join("assets", "enemy_green_3.png"))]
SPACESHIP_BLUE = [pygame.image.load(os.path.join("assets", "enemy_blue_0.png")), pygame.image.load(
    os.path.join("assets", "enemy_blue_1.png")), pygame.image.load(
    os.path.join("assets", "enemy_blue_2.png")), pygame.image.load(
    os.path.join("assets", "enemy_blue_3.png"))]


# Lasers

LASER_RED = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
LASER_GREEN = pygame.image.load(
    os.path.join("assets", "pixel_laser_green.png"))
LASER_BLUE = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))

# Player Laser
LASER_YELLOW = pygame.image.load(
    os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Player
PLAYER_IMG = pygame.image.load(os.path.join(
    "assets", "player_green_straight_1.png"))
moveLeft = [pygame.image.load(os.path.join("assets", "player_green_left_1.png")), pygame.image.load(
    os.path.join("assets", "player_green_left_2.png"))]
moveRight = [pygame.image.load(os.path.join("assets", "player_green_right_1.png")), pygame.image.load(
    os.path.join("assets", "player_green_right_2.png"))]
still = [pygame.image.load(os.path.join("assets", "player_green_straight_1.png")), pygame.image.load(
    os.path.join("assets", "player_green_straight_2.png"))]

PlayerMoveCount = 0
enemyMoveCount = 0
frameCount3 = 0
frameCount5 = 0
greenCount = 0


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y < height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def change_sprite(self, window, img):
        self.ship_img = img
        window.blit(self.ship_img, (self.x, self.y))

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_IMG
        self.laser_img = LASER_YELLOW
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15, self.y-50, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(-vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:

                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y +
                                               self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() +
                                               10, self.ship_img.get_width() * self.health/self.max_health, 10))


class Enemy(Ship):
    COLOUR_MAP = {
        "red": (SPACESHIP_RED[0], LASER_RED),
        "green": (SPACESHIP_GREEN[0], LASER_GREEN),
        "blue": (SPACESHIP_BLUE[0], LASER_BLUE)
    }

    def __init__(self, x, y, colour, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOUR_MAP[colour]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

# Background

# need to make stars already on screen at start of game but also make them only apwn above screen and despawn at bottom of screen


class Star:

    COLOUR_MAP = {
        "white": (255, 255, 255),
        "blue": (0, 0, 255)
    }

    def __init__(self, x, y, colour):
        self.x = x
        self.y = y
        self.colour = colour

    def draw(self, window):
        starRect = pygame.Rect(self.x, self.y, 2, 2)
        pygame.draw.rect(window, (255, 255, 255), starRect)

    def move(self, vel, window):
        self.y += vel

    def off_screen(self, height):
        return self.y > HEIGHT


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    player_vel = 5
    enemy_vel = 1
    laser_vel = 4

    main_menu = True

    player = Player(300, 600)

    aStar = Star(100, 100, random.choice(["white", "blue"]))
    aStar.draw(WIN)

    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont("Ariel", 50)
    lost_font = pygame.font.SysFont("Ariel", 100)

    enemies = []
    wave_length = 5

    stars = []
    stars2 = []
    starAmount = 30
    starVel1 = 1

    for i in range(starAmount):
        addStar = Star(random.randrange(
            0, WIDTH - 100), random.randrange(-500, HEIGHT), random.choice(["white", "blue"]))
        addStar2 = Star(random.randrange(
            0, WIDTH - 100), random.randrange(-500, HEIGHT), random.choice(["white", "blue"]))
        stars.append(addStar)
        stars2.append(addStar2)

    lost = False
    lost_count = 0

    left = False
    right = False

    def redraw_window():
        global PlayerMoveCount
        global enemyMoveCount
        global frameCount3
        global frameCount5
        global greenCount
        WIN.fill((0,0,0))

        # draw text
        if PlayerMoveCount + 1 >= 24:
            PlayerMoveCount = 0
        if frameCount3 > 2:
            frameCount3 = 0
            PlayerMoveCount += 1
            enemyMoveCount += 1
        if frameCount5 > 4:
            frameCount5 = 0
            greenCount += 1
        if greenCount == 3:
            greenCount = 0

        frameCount3 += 1
        frameCount5 += 1

        img1or2 = PlayerMoveCount % 2

        if left:
            PLAYER_IMG = moveLeft[img1or2]
        elif right:
            PLAYER_IMG = moveRight[img1or2]
        else:
            PLAYER_IMG = still[img1or2]

        if not(main_menu):
            level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
            WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

            if enemyMoveCount + 1 >= 24:
                enemyMoveCount = 0

            enemy1or2 = enemyMoveCount % 2
            enemy1to4 = enemyMoveCount % 4


            player.draw(WIN)

            if lost:
                lost_label = lost_font.render("YOU LOST", 1, (255, 255, 255))
                WIN.blit(
                    lost_label, (int(WIDTH/2 - lost_label.get_width()/2), int(HEIGHT/2)))
        else:
            enemy1or2 = 0
            enemy1to4 = 0
            title_font = pygame.font.SysFont("comicsans", 70)

            WIN.fill((0,0,0))
            title_label = title_font.render(
                "Click to begin...", 1, (255, 255, 255))
            WIN.blit(title_label, (int(WIDTH/2 - title_label.get_width()/2), 350))

        player.change_sprite(WIN, PLAYER_IMG)

        for star in stars[:]:
            if frameCount3 == 2:
                star.move(starVel1, WIN)
            star.draw(WIN)

        for star in stars2[:]:
            if frameCount5 == 2:
                star.move(starVel1, WIN)
            star.draw(WIN)

        for star in stars:
            if star.off_screen(HEIGHT):
                stars.remove(star)
                newStar = Star(random.randrange(
                    0, WIDTH - 100), random.randrange(-1500, -100), random.choice(["white", "blue"]))
                stars.append(newStar)
        for star in stars2:
            if star.off_screen(HEIGHT):
                stars2.remove(star)
                newStar = Star(random.randrange(
                    0, WIDTH - 100), random.randrange(-1500, -100), random.choice(["white", "blue"]))
                stars2.append(newStar)
                
        for enemy in enemies:
            if enemy.laser_img == LASER_RED:
                enemy.change_sprite(WIN, SPACESHIP_RED[enemy1or2])
            elif enemy.laser_img == LASER_GREEN:
                enemy.change_sprite(WIN, SPACESHIP_GREEN[greenCount])
            elif enemy.laser_img == LASER_BLUE:
                enemy.change_sprite(WIN,SPACESHIP_BLUE[greenCount])
            enemy.draw(WIN)

        player.draw(WIN)

        

        pygame.display.update()

    

    while run:
        clock.tick(FPS)
        redraw_window()
        print(main_menu)

        if main_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    main_menu = False
            enemies = []
            left = False
            right = False
            player = Player(300,600)

        else:
            if lives <= 0 or player.health <= 0:
                lost = True
                lost_count += 1

            if lost:
                if lost_count > FPS * 3:
                    main_menu = True
                else:
                    continue

            if len(enemies) == 0:
                level += 1
                wave_length += 5
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(
                        50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                    enemies.append(enemy)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    main_menu = True

            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] and player.x - player_vel > 0:  # left
                player.x -= player_vel
                left = True
                right = False
            elif keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
                player.x += player_vel
                right = True
                left = False
            else:
                left = False
                right = False

            if keys[pygame.K_w] and player.y - player_vel > 0:  # up
                player.y -= player_vel
            if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # down
                player.y += player_vel
            if keys[pygame.K_SPACE]:
                player.shoot()

            for enemy in enemies[:]:  # copy of enemies list
                enemy.move(enemy_vel)
                enemy.move_lasers(laser_vel, player)

                if random.randrange(0, 2*FPS) == 1:
                    enemy.shoot()

                if enemy.y + enemy.get_height() > HEIGHT:
                    enemies.remove(enemy)

                if collide(enemy, player):
                    player.health -= 10
                    enemies.remove(enemy)
            
            player.move_lasers(laser_vel, enemies)


main()
