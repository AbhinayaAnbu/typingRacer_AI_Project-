import copy
import pygame
import random
import os
import nltk

# Download the NLTK 'words' corpus
nltk.download('words')

# Initialize Pygame
pygame.init()

# Load fonts (using default font)
def load_font(size):
    return pygame.font.Font(None, size)  # Using default font as fallback

# Load fonts (using default font)
header_font = load_font(50)
pause_font = load_font(38)
banner_font = load_font(28)
font = load_font(48)

# Initialize NLTK and load the words corpus
from nltk.corpus import words
wordlist = words.words()

len_indexes = []
length = 1

wordlist.sort(key=len)
for i in range(len(wordlist)):
    if len(wordlist[i]) > length:
        length += 1
        len_indexes.append(i)
len_indexes.append(len(wordlist))

# Set up Pygame display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Typing Racer!')
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
timer = pygame.time.Clock()
fps = 60

# Game variables
level = 1
lives = 5
score = 0  # Initialize the score variable
word_objects = []
try:
    with open('high_score.txt', 'r') as file:
        high_score = int(file.readline().strip())
except FileNotFoundError:
    print("Error: High score file 'high_score.txt' not found.")
    high_score = 0

pz = True
new_level = True
submit = ''
active_string = ''
letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]
choices = [False, True, False, False, False, False, False]  # 2 letter, 3 letter, 4 letter, etc.

class Word:
    def __init__(self, text, speed, y_pos, x_pos):
        self.text = text
        self.speed = speed
        self.y_pos = y_pos
        self.x_pos = x_pos

    def draw(self):
        color = 'black'
        screen.blit(font.render(self.text, True, color), (self.x_pos, self.y_pos))
        act_len = len(active_string)
        if active_string == self.text[:act_len]:
            screen.blit(font.render(active_string, True, 'green'), (self.x_pos, self.y_pos))

    def update(self):
        self.x_pos -= self.speed

class Button:
    def __init__(self, x_pos, y_pos, text, clicked, surf):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text = text
        self.clicked = clicked
        self.surf = surf

    def draw(self):
        cir = pygame.draw.circle(self.surf, (45, 89, 135), (self.x_pos, self.y_pos), 35)
        if cir.collidepoint(pygame.mouse.get_pos()):
            butts = pygame.mouse.get_pressed()
            if butts[0]:
                pygame.draw.circle(self.surf, (190, 35, 35), (self.x_pos, self.y_pos), 35)
                self.clicked = True
            else:
                pygame.draw.circle(self.surf, (190, 89, 135), (self.x_pos, self.y_pos), 35)
        pygame.draw.circle(self.surf, 'white', (self.x_pos, self.y_pos), 35, 3)
        self.surf.blit(pause_font.render(self.text, True, 'white'), (self.x_pos - 15, self.y_pos - 25))

def draw_screen():
    # Draw screen outlines and text
    pygame.draw.rect(screen, (32, 42, 68), [0, HEIGHT - 100, WIDTH, 100], 0)
    pygame.draw.rect(screen, 'white', [0, 0, WIDTH, HEIGHT], 5)
    pygame.draw.line(screen, 'white', (0, HEIGHT - 100), (WIDTH, HEIGHT - 100), 2)
    pygame.draw.line(screen, 'white', (250, HEIGHT - 100), (250, HEIGHT), 2)
    pygame.draw.line(screen, 'white', (700, HEIGHT - 100), (700, HEIGHT), 2)
    pygame.draw.rect(screen, 'black', [0, 0, WIDTH, HEIGHT], 2)
    screen.blit(header_font.render(f'Level: {level}', True, 'white'), (10, HEIGHT - 75))
    screen.blit(header_font.render(f'"{active_string}"', True, 'white'), (270, HEIGHT - 75))
    pause_btn = Button(748, HEIGHT - 52, 'II', False, screen)
    pause_btn.draw()
    screen.blit(banner_font.render(f'Score: {score}', True, 'black'), (250, 10))
    screen.blit(banner_font.render(f'Best: {high_score}', True, 'black'), (550, 10))
    screen.blit(banner_font.render(f'Lives: {lives}', True, 'black'), (10, 10))
    return pause_btn.clicked

def draw_pause():
    choice_commits = copy.deepcopy(choices)
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(surface, (0, 0, 0, 100), [100, 100, 600, 300], 0, 5)
    pygame.draw.rect(surface, (0, 0, 0, 200), [100, 100, 600, 300], 5, 5)
    resume_btn = Button(160, 200, '>', False, surface)
    resume_btn.draw()
    quit_btn = Button(410, 200, 'X', False, surface)
    quit_btn.draw()
    surface.blit(header_font.render('MENU', True, 'white'), (110, 110))
    surface.blit(header_font.render('PLAY!', True, 'white'), (210, 175))
    surface.blit(header_font.render('QUIT', True, 'white'), (450, 175))
    surface.blit(header_font.render('Active Letter Lengths:', True, 'white'), (110, 250))

    for i in range(len(choices)):
        btn = Button(160 + (i * 80), 350, str(i + 2), False, surface)
        btn.draw()
        if btn.clicked:
            if choice_commits[i]:
                choice_commits[i] = False
            else:
                choice_commits[i] = True
        if choices[i]:
            pygame.draw.circle(surface, 'green', (160 + (i * 80), 350), 35, 5)
    screen.blit(surface, (0, 0))
    return resume_btn.clicked, choice_commits, quit_btn.clicked

def generate_level():
    word_objs = []
    include = []
    vertical_spacing = (HEIGHT - 150) // level
    if True not in choices:
        choices[0] = True
    for i in range(len(choices)):
        if choices[i]:
            include.append((len_indexes[i], len_indexes[i + 1]))
    for i in range(level):
        speed = random.randint(1, 3)
        y_pos = random.randint(10 + (i * vertical_spacing), (i + 1) * vertical_spacing)
        x_pos = random.randint(WIDTH, WIDTH + 1000)
        ind_sel = random.choice(include)
        index = random.randint(ind_sel[0], ind_sel[1])
        text = wordlist[index].lower()
        new_word = Word(text, speed, y_pos, x_pos)
        word_objs.append(new_word)
    return word_objs

def check_answer(scor):
    for wrd in word_objects:
        if wrd.text == submit:
            points = wrd.speed * len(wrd.text) * 10 * (len(wrd.text) / 4)
            scor += int(points)
            word_objects.remove(wrd)
    return scor

def check_high_score():
    global high_score
    if score > high_score:
        high_score = score
        try:
            with open('high_score.txt', 'w') as file:
                file.write(str(int(high_score)))
        except IOError:
            print("Error: Unable to write to 'high_score.txt'.")

run = True
while run:
    screen.fill('gray')
    timer.tick(fps)
    pause_butt = draw_screen()
    if pz:
        resume_butt, changes, quit_butt = draw_pause()
        if resume_butt:
            pz = False
        if quit_butt:
            check_high_score()
            run = False
    if new_level and not pz:
        word_objects = generate_level()
        new_level = False
    else:
        for w in word_objects:
            w.draw()
            if not pz:
                w.update()
            if w.x_pos < -200:
                word_objects.remove(w)
                lives -= 1
    if len(word_objects) <= 0 and not pz:
        level += 1
        new_level = True

    if submit != '':
        init = score
        score = check_answer(score)
        submit = ''
        if init == score:
            # Placeholder sound effect for 'wrong' (not implemented)
            pass

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            check_high_score()
            run = False

        if event.type == pygame.KEYDOWN:
            if not pz:
                if event.unicode.lower() in letters:
                    active_string += event.unicode
                    # Placeholder sound effect for 'click' (not implemented)
                    pass
                if event.key == pygame.K_BACKSPACE and len(active_string) > 0:
                    active_string = active_string[:-1]
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    submit = active_string
                    active_string = ''
            if event.key == pygame.K_ESCAPE:
                if pz:
                    pz = False
                else:
                    pz = True
        if event.type == pygame.MOUSEBUTTONUP and pz:
            if event.button == 1:
                choices = changes

    if pause_butt:
        pz = True

    if lives < 0:
        pz = True
        level = 1
        lives = 5
        word_objects = []
        new_level = True
        check_high_score()
        score = 0

    pygame.display.flip()

pygame.quit()
