import pygame
import random

import namegen

# Display constants
WIDTH, HEIGHT = 720, 480
FPS = 60

# Color constants
BLACK = (   0,   0,   0)
WHITE = ( 255, 255, 255)
BLUE =  (   0, 128, 255)
RED =   (   0, 128, 255)
GREEN = (   0, 255,   0)
ORANGE =(255,  127,   0)
BROWN = (150,   75,   0)
PURPLE =(150,    0, 150)

# Entity constants
DAY_LENGTH = 15 # How many seconds is a day.
ENTITY_SIZE = 10 # Size, diameter?
ENTITY_SPEED = WIDTH # Speed you will go (in pixels per second)
ENTITY_MAX_HEALTH = 10 # Max health you can have
ENTITY_MAX_SATIETY = 10 # Max fullness you can be
HEALTH_DRAIN = 2 # When starving, you lose 2 health every second.
SATIETY_DRAIN = 2 # Feeling 2 "less" full every second
STARVING_SATIETY = 2 # How hungry is considered "starving"
HEALTH_BAR_LENGTH = ENTITY_SIZE / 1.1 # The health bar drawn above the entity to show its health.
FINDING_FOOD = "finding food" # When you are hungry you will find food.
SLEEPING = "sleeping" # Sleep tight :)
SEEKING_WOOD = "seeking_wood" # If you have no house you will be seeking wood.
STORING_FOOD = "storing food" # When you are full, you seek food to save.
GOING_HOME = "going home" # After it becomes dark you seek your house.
HUNGER_THRESHOLD = 4 # How hungry you need to be before waking up at night.
HEALTH_GAIN = 2 # How much health you gain per second at night if not hungry.
FORAGE_HUNGER = 8 # How hungry you need to be to start foraging at day.
MALE = "male" # You know what this is
FEMALE = "female" # You know what this is.
SEXES = (MALE, FEMALE) # You obviously know.
MAX_STORED_FOOD = 10

# Food variables
FOOD_SIZE = ENTITY_SIZE * (3 / 4) # 3/4 of the entity's size.
FOOD_CHANCE = 100 # Chance of food per frame.
MAX_FOOD = 150

# Building variables
HOUSE_SIZE = 30
WOOD_REQUIRED = 20
WOOD_SIZE = ENTITY_SIZE * (5 / 4) # 1.25 the entity's size.
WOOD_CHANCE = 10 # Chance of wood per frame
MAX_WOOD = 50
MAX_HOUSE_STORED_FOOD = 100 # How much food a house can have.

# Misc variables
SPAWN_BORDER = 10 # So entities don't get stuck at the edge.

def main():
    pygame.init()

    life_display = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Life Simulation")

    is_crashed = False
    clock = pygame.time.Clock()

    day_time = True
    day_tick = 0

    game_manager = GameManager()

    while not is_crashed:
        dt = clock.tick(FPS) / 1000

        day_tick += dt

        #if day_tick >= DAY_LENGTH:
            #day_tick = 0
            #day_time = not day_time

        game_manager.run(dt, day_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_crashed = True
        life_display.fill(WHITE if day_time else BLACK)

        for entity in game_manager.entities.values():
            if entity.dead or entity.in_house:
                continue
            entity.draw(life_display)

        for food in game_manager.foods.values():
            if food.eaten:
                continue
            food.draw(life_display)

        for wood in game_manager.wood.values():
            wood.draw(life_display)

        for house in game_manager.houses.values():
            house.draw(life_display)
        #game_manager.draw_relationships(life_display)

        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()

class GameManager:
    def __init__(self):
        self.entities = {}
        self.entity_id = 0

        for i in range(50):
            self.add_entity()

        self.foods = {}
        self.food_id = 0

        self.houses = {}
        self.house_id = 0

        self.wood = {}
        self.wood_id = 0
    def draw_relationships(self, display):
        pass
    def run(self, dt, day_time):
        dead_entities = []  # Keys of dead entities
        eaten_foods = []
        chopped_woods = []
        broken_houses = []

        for entity in self.entities.values():
            if entity.dead:
                dead_entities.append(entity.entity_id)
                if entity.house:
                    broken_houses.append(entity.house)
                continue
            if entity.wood >= WOOD_REQUIRED:
                self.houses[str(self.house_id)] = Building(entity.x, entity.y)
                entity.house = str(self.house_id)
                entity.wood = 0
                self.house_id += 1
            entity.run(self.entities, self.foods, self.houses, self.wood, dt, day_time)

        for food in self.foods.values():
            if food.eaten:
                eaten_foods.append(food.entity_id)

        for wood in self.wood.values():
            if wood.chopped:
                chopped_woods.append(wood.entity_id)

        for dead in dead_entities:
            if dead in self.entities:  # Check if the entity_id exists before deletion
                del self.entities[dead]

        for eaten in eaten_foods:
            if eaten in self.foods:  # Check if the food_id exists before deletion
                del self.foods[eaten]

        for chopped in chopped_woods:
            if chopped in self.wood:
                del self.wood[chopped]

        for broken in broken_houses:
            if broken in self.houses:
                del self.houses[broken]

        self.food_adding()
        self.wood_adding()
    def food_adding(self):
        if len(self.wood) >= MAX_FOOD:
            return
        food_chance = random.randint(0, 100)

        if food_chance <= FOOD_CHANCE:
            self.foods[self.food_id] = Food(self.food_id)
            self.food_id += 1
    def wood_adding(self):
        if len(self.wood) >= MAX_WOOD:
            return
        wood_chance = random.randint(0, 100)
        if wood_chance <= WOOD_CHANCE:
            self.wood[self.wood_id] = Wood(self.wood_id)
            self.wood_id += 1
    def add_entity(self):
        self.entities[self.entity_id] = Entity(self.entity_id)
        self.entity_id += 1

class Entity:
    def __init__(self, entity_id, x = None, y = None):
        if not x and not y:
            self.x, self.y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        else:
            self.x = x
            self.y = y

        self.name = random.choice(namegen.full_name())

        self.rect = pygame.Rect(self.x, self.y, ENTITY_SIZE, ENTITY_SIZE)

        self.sex = random.choice(SEXES)

        self.health = ENTITY_MAX_HEALTH
        self.satiety = ENTITY_MAX_SATIETY
        self.wood = 0

        self.dead = False

        self.task = FINDING_FOOD

        self.house = None
        self.in_house = False

        self.stored_food = 0

        self.entity_id = entity_id
    def move_toward(self, target_x, target_y, dt):
        x1, y1 = self.x, self.y
        x2, y2 = target_x, target_y

        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        try:
            self.x += ((target_x - self.x) / distance) * ENTITY_SPEED * dt
            self.y += ((target_y - self.y) / distance) * ENTITY_SPEED * dt
        except ZeroDivisionError:
            return
    def get_nearest(self, objects):
        nearest_distance = float('inf')
        nearest_id = None

        for obj in objects.values():
            if self.entity_id != obj.entity_id:
                distance = get_distance(self.x, self.y, obj.x, obj.y)

                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_id = obj.entity_id  # Use the entity_id directly
        return nearest_id
    def draw(self, surface):
        self.rect = pygame.draw.circle(surface, BLUE if self.sex == MALE else RED, (self.x, self.y), 5)

        # Circular health bar for simplicity.
        pygame.draw.circle(surface, RED, (self.x, self.y - (HEALTH_BAR_LENGTH * 1.5)), HEALTH_BAR_LENGTH)
        pygame.draw.circle(surface, GREEN, (self.x, self.y - (HEALTH_BAR_LENGTH * 1.5)), HEALTH_BAR_LENGTH / (ENTITY_MAX_HEALTH / self.health))
    @staticmethod
    def calculate_midpoint(x1, y1, x2, y2):
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        return mid_x, mid_y
    def run(self, other_entities, food_objects, houses, wood, dt, day_time):
        if not day_time and self.satiety > HUNGER_THRESHOLD:
            if self.house:
                self.task = GOING_HOME
            else:
                self.task = SLEEPING
        elif not day_time and self.satiety < HUNGER_THRESHOLD:
            if self.house:
                if houses[self.house].stored_food > (MAX_STORED_FOOD - self.satiety):
                    self.satiety += (MAX_STORED_FOOD - self.satiety)
                    houses[self.house].stored_food -= (MAX_STORED_FOOD - self.satiety)
                else:
                    self.task = FINDING_FOOD
                    self.in_house = False
            else:
                self.task = FINDING_FOOD
        else:
            self.in_house = False
            if self.satiety < FORAGE_HUNGER:
                self.task = FINDING_FOOD
            else:
                if self.house:
                    self.task = STORING_FOOD
                else:
                    self.task = SEEKING_WOOD
        if day_time and self.stored_food >= MAX_STORED_FOOD:
            self.task = GOING_HOME

        if self.task == SLEEPING:
            if self.health < ENTITY_MAX_HEALTH:
                self.health += HEALTH_GAIN * dt
            else:
                self.health = ENTITY_MAX_HEALTH
        if self.house and houses[self.house].stored_food > MAX_HOUSE_STORED_FOOD:
            houses[self.house].stored_food = 0
        self.satiety -= SATIETY_DRAIN * dt

        if self.satiety <= STARVING_SATIETY:
            self.health -= HEALTH_DRAIN * dt
            if self.health <= 0:
                self.dead = True
            if self.satiety <= 0:
                self.satiety = 0

        for entity in other_entities.values():
            if entity.entity_id == self.entity_id:
                continue
        if self.task == GOING_HOME and self.house:
            self.move_toward(houses[self.house].x, houses[self.house].y, dt)
            if self.rect.colliderect(houses[self.house].rect):
                if day_time:
                    houses[self.house].stored_food += MAX_STORED_FOOD
                    self.stored_food = 0
                    self.task = FINDING_FOOD
                else:
                    self.in_house = True
        if self.task == FINDING_FOOD or self.task == STORING_FOOD:
            if len(food_objects) > 0:
                closest_food_id = self.get_nearest(food_objects)
                if closest_food_id is not None:
                    closest_food = food_objects[closest_food_id]
                    self.move_toward(closest_food.x, closest_food.y, dt)
                    if self.rect.colliderect(closest_food.rect):
                        if self.task == FINDING_FOOD:
                            self.satiety += closest_food.food
                            food_objects[closest_food.entity_id].eaten = True
                        else:
                            self.stored_food += closest_food.food
                            food_objects[closest_food.entity_id].eaten = True
        if self.task == SEEKING_WOOD:
            if len(wood) > 0:
                closest_wood_id = self.get_nearest(wood)
                if closest_wood_id is not None:
                    closest_wood = wood[closest_wood_id]
                    self.move_toward(closest_wood.x, closest_wood.y, dt)
                    if self.rect.colliderect(closest_wood.rect):
                        self.wood += closest_wood.wood
                        wood[closest_wood.entity_id].chopped = True

class WildBeast: # TODO WRITE
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Food:
    def __init__(self, given_id):
        # Position variables
        self.x = random.randint(0, WIDTH - SPAWN_BORDER)
        self.y = random.randint(0, HEIGHT - SPAWN_BORDER)

        # How much satiety it will give to the eater
        self.food = random.randint(1, 3)
        self.rect = pygame.Rect(self.x, self.y, FOOD_SIZE, FOOD_SIZE)

        self.entity_id = given_id

        # If the food is eaten.
        self.eaten = False
    def draw(self, surface):
        # Draw it.
        pygame.draw.rect(surface, GREEN, self.rect)

class Building:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.rect = pygame.Rect(self.x, self.y, HOUSE_SIZE, HOUSE_SIZE)

        self.broken = False
        self.stored_food = 0
    def draw(self, display):
        pygame.draw.rect(display, ORANGE, self.rect)

class Wood:
    def __init__(self, entity_id, x = None, y = None):
        if not x and not y:
            self.x, self.y = random.randint(0, WIDTH - SPAWN_BORDER), random.randint(0, HEIGHT - SPAWN_BORDER)
        else:
            self.x, self.y = x, y

        self.rect = pygame.Rect(self.x, self.y, WOOD_SIZE, WOOD_SIZE)

        self.chopped = False
        self.entity_id = entity_id

        self.wood = random.randint(1, 3)
    def draw(self, display):
        pygame.draw.rect(display, BROWN, self.rect)

def get_distance(x1, y1, x2, y2):
    return abs(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)

if __name__ == "__main__":
    main()