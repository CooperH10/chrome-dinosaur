import pygame
import os
import random
import enum
import pickle
import sys
from qlearning import QLearningAgent
pygame.init()

# Global Constants
class Mode(enum.Enum):
    HUMAN_MODE = 1
    COMPUTER_TRAIN = 2
    COMPUTER_PLAY = 3

MODE = None
EPISODE = 0
FILENAME = "states.pkl"

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

qAgent = QLearningAgent(.5, .8, .2)

class Dinosaur:
    """Dinosaur (player) object. Can duck and jump to avoid obstacles
    while running. Maintains the same x-coordinate throughout game."""

    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        """Update funciton for human play."""
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False
        
    def q_update(self, userInput):
        """Update function for q-learning"""
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput == "jump" and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput == "duck" and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput == "duck"):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        """Tells the dinosaur to duck."""
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        """Dinosaur runs, increasing score and displaying running image."""
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        """Dinosaur jumps, moving up vertically and avoiding ground obsticles."""
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        """Draw the dinosaur."""
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

    def getHeight(self):
        """Returns the height of the dinosaur."""
        return self.dino_rect.y


class Cloud:
    """Creates a cloud obstacle. Just decorative."""

    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        """Update function, same for human and q-learning play."""
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        """Draws cloud objects."""
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    """Obstacle parent class. Obstacles move left towards the dinosaur
    and the game ends upon collision."""
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        """Update function, same for human and q-learning play."""
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    """Creates small cactus obstacle."""

    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325

class LargeCactus(Obstacle):
    """Creates large cactus obstacle."""
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    """Creates bird obstacle, appears at different heights on the screen."""
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 250
        self.index = 0

    def draw(self, SCREEN):
        """Draw bird obstacle."""
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index//5], self.rect)
        self.index += 1


def main():
    """Runs the game. This function is called in each instance of the game,
    including during q-learning training."""

    # variables
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 20
    death_count = 0
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    

    def score():
        """Keeps track of score and increases the game_speed variable
        accordingly (every 100 points)."""
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1

        text = font.render("Points: " + str(points), True, (0, 0, 0))

        if MODE == Mode.COMPUTER_TRAIN:
            text = font.render("Points: " + str(points) + "  Ep: " + str(EPISODE), True, (0, 0, 0))

        textRect = text.get_rect()
        textRect.center = (1000, 40)
        SCREEN.blit(text, textRect)

    def background():
        """Display background."""
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    # Main loop: moves obstacles and generates displays
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # aesthetics
        if MODE == Mode.COMPUTER_TRAIN:
            SCREEN.fill((255, 16, 240))
        else:
            SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        player.draw(SCREEN)
        if MODE == Mode.HUMAN_MODE:
            player.update(userInput) 
        else:
            time_to_obstacle = float("inf")
            if len(obstacles) > 0:
                time_to_obstacle = int((obstacles[0].rect.x-80) / game_speed)

            # Only select an action and update qvalue if on the ground 
            if not player.dino_jump:

                # Computer train mode
                if MODE == Mode.COMPUTER_TRAIN:
                    reward = 0
                    if time_to_obstacle < 0: # Incentivize clearing obstacle
                        reward = 1000
                    else:
                        if qAgent.lastAction == "jump": # Disincentivize jumping unnecessarily
                            reward = -60
                        else:
                            reward = 20

                    # Update qvalue of previous state action pair with current state and calculated reward
                    qAgent.update(qAgent.lastState, qAgent.lastAction, time_to_obstacle, reward)

                    # Decide the agents next action
                    qAgent.lastAction = qAgent.getAction(time_to_obstacle)
                    qAgent.lastState = time_to_obstacle
                    player.q_update(qAgent.lastAction)

                # Computer play mode
                else:
                    qAgent.lastState = time_to_obstacle
                    player.q_update(qAgent.getPolicy(time_to_obstacle))
                    
            else: # If in the air, agent cannot make a move
                player.q_update(None)


        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            # elif random.randint(0, 2) == 2:
            #     obstacles.append(Bird(BIRD))

        # Check for collisions
        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                if not MODE == Mode.COMPUTER_TRAIN:
                    pygame.time.delay(1000)
                else:
                    with open(FILENAME, 'wb') as file:
                        pickle.dump(qAgent.qvalues, file)
                    qAgent.update(qAgent.lastState, qAgent.lastAction, None, -1000)
                death_count += 1
                run = False

        if run:
            background()

            cloud.draw(SCREEN)
            cloud.update()

            score()

            # Speed up the overall game to make training faster
            if MODE == Mode.COMPUTER_TRAIN:
                clock.tick(10000)
            else:
                clock.tick(30)
            
            pygame.display.update()


def menu(death_count):
    """Main function, called each time the game restarts and generates start
    screen menu during human play."""
    
    global points
    global EPISODE
    global FILENAME
    global MODE

    if MODE == Mode.COMPUTER_PLAY:
        qAgent.loadStates(FILENAME)

    run = True
    
    # While program is running check death count and generate displays
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)

        if death_count == 0:
            text = font.render("Press any Key to Start", True, (0, 0, 0))
        elif death_count > 0:
            text = font.render("Press any Key to Restart", True, (0, 0, 0))
            score = font.render("Your Score: " + str(points), True, (0, 0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
        pygame.display.update()
        if MODE == Mode.HUMAN_MODE or MODE == Mode.COMPUTER_PLAY:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    run = False
                if event.type == pygame.KEYDOWN:
                    main()
        # Limit q-learning training to 5000 episodes
        elif MODE == Mode.COMPUTER_TRAIN and EPISODE < 5000:
            EPISODE += 1
            main()
        else:
            pygame.quit()
            run = False

# Read command line arguments
if len(sys.argv) > 1:

    for i, arg in enumerate(sys.argv):
        if arg == '-h':
            MODE = Mode.HUMAN_MODE
        if arg == '-t':
            MODE = Mode.COMPUTER_TRAIN
        if arg == '-a':
            MODE = Mode.COMPUTER_PLAY
    if MODE == None:
        print("Please use the command python main.py -h (if human mode) -t (if train mode) -a (if ai mode)")
        sys.exit(0)
        
else:
    print("Please use the command python main.py -h (if human mode) -t (if train mode) -a (if ai mode)")
    sys.exit(0)

if __name__ == "__main__":
    menu(0)
