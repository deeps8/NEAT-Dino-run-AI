import pygame
import os
import neat
import random
pygame.init()
pygame.font.init()

# getting all images : bird , cactus , dino , bg
# set up the game window
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1000

FONT = pygame. font. SysFont("Segoe UI", 35)

GEN = 0

GAP = 600
GAME_SPEED = 30

RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join(
                    "Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join(
                    "Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]


BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))


# Dino class with all neccessary functions.
class Dino():
    DINO_RUNNING = RUNNING
    DINO_JUMP = JUMPING
    DINO_DUCK = DUCKING

    X_POS = 100
    Y_POS = 320
    Y_DUCK_POS = 358
    DINO_VEL = 10

    def __init__(self):

        self.dino_status = {'run': True, 'jump': False, 'duck': False}

        self.tick_count = 0
        self.jump_vel = self.DINO_VEL
        self.image = self.DINO_RUNNING[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def duck(self):
        self.image = self.DINO_DUCK[self.tick_count // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_DUCK_POS
        self.tick_count += 1

    def run(self):
        self.image = self.DINO_RUNNING[self.tick_count // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.tick_count += 1

    def jump(self):
        self.image = self.DINO_JUMP
        if self.dino_status['jump']:
            self.dino_rect.y -= self.jump_vel * 3
            self.jump_vel -= 1
        if self.jump_vel < - self.DINO_VEL:
            self.dino_status['jump'] = False
            self.jump_vel = self.DINO_VEL

    def update(self, output):

        if self.tick_count >= 10:
            self.tick_count = 0

        if self.dino_status['jump']:
            self.jump()
        elif self.dino_status['duck']:
            self.duck()
        else:
            self.run()

                # elif not (self.dino_status['jump']):  # DEFAULT : RUN
        if output[0] > 0.5 and not self.dino_status['jump']:  # DEFAULT : RUN
            self.dino_status['duck'] = False
            self.dino_status['jump'] = False
            self.dino_status['run'] = True
        
        elif output[1] > 0.5 and not self.dino_status['jump']:  # JUMP
            self.dino_status['jump'] = True
            self.dino_status['run'] = False
            self.dino_status['duck'] = False

        elif output[2] > 0.6 and not self.dino_status['jump']:  # DUCK
            self.dino_status['duck'] = True
            self.dino_status['jump'] = False
            self.dino_status['run'] = False


    def draw(self, win):
        win.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Obstacle():
    def __init__(self, image, type, start, y):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = start
        self.y = y
        self.passed = False

    def update(self):
        self.rect.x -= GAME_SPEED
        return self.rect.x + self.rect.width < 0
        # obstacles.pop(x)

    def draw(self, win):
        win.blit(self.image[self.type], self.rect)

    def collide(self, dino):
        dino_mask = dino.get_mask()
        obstacle_mask = pygame.mask.from_surface(self.image[self.type])

        offset = (self.rect.x - dino.dino_rect.x,
                  self.y - round(dino.dino_rect.y))

        point = dino_mask.overlap(obstacle_mask, offset)

        if point:
            return True

        return False


class SmallCactus(Obstacle):
    def __init__(self, image, start):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type, start, 342)
        self.height = image[self.type].get_rect().height
        self.rect.y = 342


class LargeCactus(Obstacle):
    def __init__(self, image, start):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type, start, 342)
        self.height = image[self.type].get_rect().height
        self.rect.y = 315


class Bird(Obstacle):
    def __init__(self, image, start):
        self.type = 0
        super().__init__(image, self.type, start, 275)
        self.height = image[self.type].get_rect().height
        self.which_bird = random.randint(0, 2)
        if self.which_bird == 0:
            self.rect.y = 260
        else:
            self.rect.y = 220    
        self.index = 0

    def draw(self, win):
        if self.index >= 9:
            self.index = 0
        win.blit(self.image[self.index//5], self.rect)
        self.index += 1


def random_obstacles(obstacles):
    if len(obstacles) == 0:
        if random.randint(0, 2) == 0:
            obstacles.append(SmallCactus(SMALL_CACTUS, SCREEN_WIDTH))
            obstacles.append(Bird(BIRD, SCREEN_WIDTH + GAP))
        elif random.randint(0, 2) == 1:
            obstacles.append(LargeCactus(LARGE_CACTUS, SCREEN_WIDTH))
            obstacles.append(SmallCactus(SMALL_CACTUS, SCREEN_WIDTH + GAP))
        elif random.randint(0, 2) == 2:
            obstacles.append(Bird(BIRD, SCREEN_WIDTH))
            obstacles.append(SmallCactus(SMALL_CACTUS, SCREEN_WIDTH + GAP))

    return obstacles


def draw_window(win, dino, obstacles, score, gen):

    win.fill((255, 255, 255))
    win.blit(BG, (0, 400))

    text = FONT.render("Score : "+str(score), 1, (0, 0, 0))
    win.blit(text, (SCREEN_WIDTH-10-text.get_width(), 10))

    text_gen = FONT.render("Gen : "+str(gen), 1, (0, 0, 0))
    win.blit(text_gen, (10, 10))

    dino.draw(win)

    for obstacle in obstacles:
        obstacle.draw(win)

    pygame.display.update()


def main(genomes, config):

    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    global GEN
    GEN += 1

    nets = []
    ge = []
    dinos = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        dinos.append(Dino())
        g.fitness = 0
        ge.append(g)

    obstacles = []
    random_obstacles(obstacles)

    score = 0

    run = True
    clock = pygame.time.Clock()
    while run:
        add_obstacle = False
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # which obstacle index to select
        obs_ind = 0
        if len(dinos) > 0:
            if len(obstacles) > 1 and dinos[0].dino_rect.x > obstacles[0].rect.x + obstacles[0].rect.width:
                obs_ind = 1
        else:
            run = False
            break

        # activation function params
        for x, dino in enumerate(dinos):
            ge[x].fitness += 0.1

            # print(len(obstacles))
            if len(obstacles):
                from_ground = 400 - \
                    (obstacles[obs_ind].y + obstacles[obs_ind].height)
                # angle =
                # inputs : 1. dino y posi , 2. obstacle y posi , 3. distance between them
                outputs = nets[x].activate((dino.dino_rect.y,obstacles[obs_ind].rect.width, obstacles[obs_ind].height, obstacles[obs_ind].y, from_ground, abs(
                    (dino.dino_rect.x + dino.dino_rect.width) - obstacles[obs_ind].rect.x)))

                # ouput process according to it
                dino.update(outputs)

        # geting random obstacles
        random_obstacles(obstacles)

        rem = []
        for x, obstacle in enumerate(obstacles):
            for i, dino in enumerate(dinos):
                # if collide or not
                if dino.dino_rect.colliderect(obstacle.rect):
                    ge[i].fitness -= 1
                    nets.pop(i)
                    ge.pop(i)
                    dinos.pop(i)
                    # print("collided")
                    # run = False
                    # break

                # if obstacle crossed or not
                if not obstacle.passed and obstacle.rect.x < dino.dino_rect.x:
                    obstacle.passed = True
                    add_obstacle = True

            flag = obstacle.update()
            if flag:
                rem.append(obstacle)

        if add_obstacle:
            score += 2
            for g in ge:
                g.fitness += 5

        for r in rem:
            obstacles.remove(r)

        if score == 50:
            GAME_SPEED = 40

        for x, dino in enumerate(dinos):
            if dino.dino_rect.y < 120:
                ge.pop(x)
                nets.pop(x)
                dinos.pop(x)

        draw_window(win, dino, obstacles, score, GEN)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat_config_file.txt")
    run(config_path)
