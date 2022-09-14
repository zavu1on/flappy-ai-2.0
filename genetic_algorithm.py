from random import randint, choice, random

# объявляем переменные
TARGET = 'java'
POPULATION_NUM = 100
MUTATION_RATE = 0.01
matting_pool = []
population = []
generation = 0

# создаём первую популяцию
for _ in range(POPULATION_NUM):
    population.append({
        'genes': [randint(97, 122) for _ in range(len(TARGET))],
        'fitness': 0
    })

# оцениваем пригодность
for p in population:
    for g in p['genes']:
        if chr(g) in TARGET:
            p['fitness'] += 1
    p['fitness'] /= 100

# тренируем популяции
while True:
    generation += 1

    # подготавливаем набор для скрещиванию
    for p in population:
        for _ in range(int(p['fitness'] * 100)):
            matting_pool.append(p)

    # скрещивание
    for idx in range(len(population)):
        # выбираем случайных родителей
        parent_a = choice(matting_pool)
        parent_b = None

        while not parent_b and parent_a != parent_b:
            parent_b = choice(matting_pool)

        # crossover
        midpoint = randint(0, len(parent_a['genes']))
        child = {
            'genes': [randint(97, 122) for _ in range(len(TARGET))],
            'fitness': 0
        }

        for i in range(len(parent_a['genes'])):
            if i > midpoint:
                child['genes'][i] = parent_a['genes'][i]
            else:
                child['genes'][i] = parent_b['genes'][i]

        # mutations
        for i in range(len(child['genes'])):
            if MUTATION_RATE > random():
                child['genes'][i] = randint(97, 122)

        # оцениваем пригодность новой особи
        for g in child['genes']:
            if chr(g) in TARGET:
                child['fitness'] += 1
        child['fitness'] /= 100

        population[idx] = child

    matting_pool.clear()

    for p in population:
        string = ''

        for g in p['genes']:
            string += chr(g)

        if string == TARGET:
            print(string)
            print(generation)
            quit()
