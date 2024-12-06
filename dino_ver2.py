import threading
import pygame
import os
import random
import cv2

from pygame import mixer 
import pyautogui
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# Initialize Pygame
pygame.init()
mixer.init()


# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))



RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "planerun.png")),
           pygame.image.load(os.path.join("Assets/Dino", "planerun1.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "planejump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "planeduck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "planeduck2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "smallalien1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "smallalien2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "smallalien3.png"))]

LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "largealien1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "largealien2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "largealien3.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "meteor1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "meteor2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "PLanet.png"))

BG = pygame.image.load(os.path.join("Assets/Other", "download.png"))
BGMUSIC = mixer.music.load(os.path.join("Assets/Sound", "bgmusic.mp3"))


# Variables for game and OpenCV control
game_speed = 20
x_pos_bg = 0
y_pos_bg = 380
points = 0
obstacles = []
death_count = 0

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)

jump_line_y = 170
duck_line_y = 320
action = None


def detect_face():
    global action
    while True:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            center_y = y + h // 2
            if center_y < jump_line_y:
                action = "jump"
            elif center_y > duck_line_y:
                action = "duck"
            else:
                action = None

        cv2.line(img, (0, jump_line_y), (700, jump_line_y), (255, 0, 0), 5)#jump line
        cv2.line(img, (0, duck_line_y), (700, duck_line_y), (0, 255, 0), 5)#duck line
        cv2.imshow('Face Detection', img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING
        #Default state running
        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False
        
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self):
        global action
        if action == "jump" and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif action == "duck" and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or action == "duck"):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 200
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index//5], self.rect)
        self.index += 1



def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, death_count
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    obstacles = []
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 0
    points = 0


    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

        
    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        font = pygame.font.Font('freesansbold.ttf', 20)
        text = font.render("Light Years Travelled: " + str(points), True, (255, 255, 255))
        SCREEN.blit(text, (800, 40))


    def obstacles_manager():
        global obstacles
        if len(obstacles) == 0:
            if random.randint(0, 2 ) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0,2 ) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            else:
                obstacles.append(Bird(BIRD))


        for obstacle in obstacles:
            obstacle.update()
            obstacle.draw(SCREEN)
            if player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(500)
                global death_count
                death_count += 1
                menu()


    while run:

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((255, 255, 255))
        background()

        player.draw(SCREEN)
        player.update()
      
        # cloud.draw(SCREEN)

        obstacles_manager()
        # cloud.update()
        score()
        pygame.display.update()
        clock.tick(30)



def menu():
    mixer.music.play(loops=-1)
    global death_count, points
    run = True
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)

        if death_count == 0:
            text = font.render("Press any key to Start", True, (0, 0, 0))
        elif death_count > 0:
            text = font.render("Press any Key to Restart", True, (0, 0, 0))
            score = font.render("Your Score: " + str(points), True, (0, 0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
        else:
            text = font.render("Press any key to Restart", True, (0, 0, 0))
            score_text = font.render(f"Your Distance: {points}", True, (255, 255, 255))

            SCREEN.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        SCREEN.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                main()

if __name__ == "__main__":
    face_thread = threading.Thread(target=detect_face)
    face_thread.daemon = True
    face_thread.start()
    menu()
