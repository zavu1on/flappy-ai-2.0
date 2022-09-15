import random
import pygame
import numpy as np

pygame.init()

W = 550
H = 800

# загружаем картинки у увеличиваем их в 2 раза
BIRD_SPRITES = [
    pygame.transform.scale2x(pygame.image.load('sprites/bird1.png')),
    pygame.transform.scale2x(pygame.image.load('sprites/bird2.png')),
    pygame.transform.scale2x(pygame.image.load('sprites/bird3.png')),
]
PIPE_SPRITE = pygame.transform.scale2x(pygame.image.load('sprites/pipe.png'))
BASE_SPRITE = pygame.transform.scale2x(pygame.image.load('sprites/base.png'))
BG_SPRITE = pygame.transform.scale2x(pygame.image.load('sprites/bg.png'))
font = pygame.font.SysFont('Arial', 32)

POPULATION_NUM = 25
MUTATION_RATE = 0


# функции для работы с нейронной сетью
def sigmoid(x, derivative=False):
    """ сигмоида """
    if derivative:
        return sigmoid(x) * (1 - sigmoid(x))
    return 1 / (1 + np.exp(-x))


def generate_weights(size):
    return 2 * np.random.random(size) - 1


class Bird:
    MAX_ROTATION = 25
    ROT_VELOCITY = 20
    ANIM_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.deg = 0
        self.time = 0
        self.vel = 0
        self.height = self.y
        self.anim_count = 0
        self.img = BIRD_SPRITES[0]
        self.genes = generate_weights(3)
        self.fitness = 0

    def jump(self):
        self.vel = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        self.time += 1

        s = self.vel * self.time + 1.5 * self.time ** 2

        if s >= 16:  # ограничиваем бесконечное ускорение при падении
            s = 16
        elif s < 0:
            s -= 2

        self.y += s

        # ограничиваем бесконечный поворот птички
        if s < 0 or self.y < self.height + 50:
            self.deg = self.MAX_ROTATION
        elif self.deg > -90:
            self.deg -= self.ROT_VELOCITY

    def draw(self, win):
        self.anim_count += 1

        # анимируем птичку
        if self.anim_count <= self.ANIM_TIME:
            self.img = BIRD_SPRITES[0]
        elif self.anim_count <= self.ANIM_TIME * 2:
            self.img = BIRD_SPRITES[1]
        elif self.anim_count <= self.ANIM_TIME * 3:
            self.img = BIRD_SPRITES[2]
        elif self.anim_count <= self.ANIM_TIME * 4:
            self.img = BIRD_SPRITES[1]
        elif self.anim_count == self.ANIM_TIME * 4 + 1:
            self.img = BIRD_SPRITES[0]
            self.anim_count = 0

        # если птичка падает, делаем картинку статичной
        if self.deg <= -80:
            self.img = BIRD_SPRITES[1]
            self.anim_count = self.ANIM_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.deg)
        render_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center
        )

        win.blit(rotated_image, render_rect.topleft)  # рисуем птичку

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    def activate(self, a, b, c):
        return sigmoid(np.dot(self.genes, np.array([a, b, c])))


class PipePair:
    GAP = 200  # расстояние между трубами
    VEL = 5

    def __init__(self, x):
        self.x = x

        self.PIPE_TOP = pygame.transform.flip(PIPE_SPRITE, False, True)  # отражаем спрайт по горизонтали
        self.PIPE_BOTTOM = PIPE_SPRITE

        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()  # нижня точка верхней трубы
        self.bottom = self.height + self.GAP  # верхняя точка нижней трубы

        self.passed = False

    def move(self):
        self.x -= self.VEL * speed

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        # получаем маски
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # высчитываем смещение
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # ищем пересечения
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        return b_point or t_point


class Base:
    VEL = 5
    WIDTH = BASE_SPRITE.get_width()
    IMG = BASE_SPRITE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # поочередно меняем платформы
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


win = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
generation = 0
birds = []

# создаём первую популяцию
for _ in range(POPULATION_NUM):
    birds.append(Bird(230, 350))

while True:
    generation += 1
    population = []
    matting_pool = []
    run = True
    speed = 1
    score = 0
    base = Base(730)
    pipes = [PipePair(700)]

    while run:
        rm_list = []
        add_pipe = False
        cur_pipe_idx = 0

        clock.tick(30)  # устанавливаем FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # обработчик закрытия игры
                exit()

        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                # если птички перелетели через трубу, но мы ее еще не удалили
                cur_pipe_idx = 1
        else:
            run = False

        for idx, bird in enumerate(birds):
            bird.move()
            bird.fitness += 1

            output = bird.activate(
                bird.y,
                abs(bird.y - pipes[cur_pipe_idx].height),
                abs(bird.y - pipes[cur_pipe_idx].bottom),
            )

            if output > 0.5:
                bird.jump()

        for pipe in pipes:
            pipe.move()

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                # если труба уплыла за экран
                rm_list.append(pipe)

            for idx, bird in enumerate(birds):
                if not pipe.passed and pipe.x < bird.x:
                    # если птичка перелетела через трубу
                    pipe.passed = True
                    add_pipe = True

                if pipe.collide(bird):
                    bird.fitness -= 1  # ругаем птичку, если она стакнулась

                    birds.pop(idx)
                    population.append(bird)

        if add_pipe:
            score += 1
            pipes.append(PipePair(700))

        for r in rm_list:
            pipes.remove(r)

        for idx, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                # если птички улетела в космос или упала вниз
                bird.fitness -= 1

                birds.pop(idx)
                population.append(bird)

        base.move()

        # рисуем все спрайты
        win.blit(BG_SPRITE, (0, 0))

        for pipe in pipes:
            pipe.draw(win)

        base.draw(win)

        for bird in birds:
            bird.draw(win)

        text = font.render(f'Score: {score}', True, (255, 255, 255))
        win.blit(text, (W - 10 - text.get_width(), 10))
        text = font.render(f'Generations: {generation}', True, (255, 255, 255))
        win.blit(text, (W - 10 - text.get_width(), 50))
        text = font.render(f'Alive: {len(birds)}', True, (255, 255, 255))
        win.blit(text, (W - 10 - text.get_width(), 90))

        pygame.display.update()

    # подготавливаем набор для скрещиванию
    for bird in population:
        for _ in range(bird.fitness):
            matting_pool.append(bird)

    # скрещивание
    for idx in range(len(population)):
        # выбираем случайных родителей
        parent_a = random.choice(matting_pool)
        parent_b = None

        while not parent_b and parent_a != parent_b:
            parent_b = random.choice(matting_pool)

        # crossover
        midpoint = random.randint(0, len(parent_a.genes))
        child = Bird(230, 350)

        for i in range(len(parent_a.genes)):
            if i > midpoint:
                child.genes[i] = parent_a.genes[i]
            else:
                child.genes[i] = parent_b.genes[i]

        # mutations
        for i in range(len(child.genes)):
            if MUTATION_RATE > random.random():
                child.genes[i] = 2 * np.random.rand(1) - 1

        population[idx] = child

    birds = population.copy()
