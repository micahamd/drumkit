import pygame
import os

pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (170, 170, 170)
GREEN = (0, 255, 0)
GOLD = (212, 175, 55)
BLUE = (0, 255, 255)

# Screen setup
WIDTH = 1400
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Beat Maker")

# Fonts
label_font = pygame.font.SysFont('Arial', 32)
medium_font = pygame.font.SysFont('Arial', 24)

# Timer
timer = pygame.time.Clock()
FPS = 60

# Game variables
run = True
playing = True
save_menu = False
load_menu = False
beat_changed = True
active_beat = 0
active_length = 0
beats = 8
bpm = 240
beat_name = ""
typing = False
index = 100
boxes = []
clicked = [[-1 for _ in range(beats)] for _ in range(6)]
active_list = [1] * 6
saved_beats = []

# Load sounds
sounds = {}
sound_files = {
    "hi_hat": "sounds/hihat.wav",
    "snare": "sounds/snare.wav",
    "kick": "sounds/kick.wav",
    "crash": "sounds/crash.wav",
    "clap": "sounds/clap.wav",
    "tom": "sounds/tom.wav"
}

for name, file in sound_files.items():
    if os.path.exists(file):
        sounds[name] = pygame.mixer.Sound(file)
    else:
        print(f"Warning: Sound file {file} not found.")

# Set number of mixer channels
pygame.mixer.set_num_channels(6 * 3)

# Load saved beats from file
try:
    with open("savedbeats.txt", "r") as file:
        saved_beats = file.readlines()
except FileNotFoundError:
    print("No saved beats file found. Starting with an empty list.")

# Define UI elements
instrument_rects = [pygame.Rect((0, i * 100, 200, 100)) for i in range(6)]
add_bpm_rect = pygame.Rect(300, HEIGHT - 150, 50, 50)
bpm_sub_rect = pygame.Rect(200, HEIGHT - 150, 50, 50)
beats_add_rect = pygame.Rect(600, HEIGHT - 150, 50, 50)
beats_sub_rect = pygame.Rect(500, HEIGHT - 150, 50, 50)
play_pause = pygame.Rect(850, HEIGHT - 150, 100, 50)
clear_button = pygame.Rect(1000, HEIGHT - 150, 100, 50)
save_button = pygame.Rect(1150, HEIGHT - 150, 100, 50)
load_button = pygame.Rect(1300, HEIGHT - 150, 100, 50)

def draw_grid(clicked, active_beat):
    global boxes
    boxes = []
    screen.fill(BLACK)

    # Left menu
    pygame.draw.rect(screen, GRAY, (0, 0, 200, HEIGHT - 200), 5)

    # Bottom menu
    pygame.draw.rect(screen, GRAY, (0, HEIGHT - 200, WIDTH, 200), 5)

    # Instrument text
    instruments = ["Hi-Hat", "Snare", "Bass Drum", "Crash", "Clap", "Floor Tom"]
    for i, instrument in enumerate(instruments):
        text = label_font.render(instrument, True, WHITE if active_list[i] else GRAY)
        screen.blit(text, (10, 10 + i * 100))
        pygame.draw.line(screen, GRAY, (0, (i + 1) * 100), (200, (i + 1) * 100), 3)

    # Draw beat rectangles
    for i in range(beats):
        for j in range(6):
            rect = pygame.Rect(205 + i * ((WIDTH - 200) // beats), 5 + j * 100, (WIDTH - 200) // beats - 10, 90)
            boxes.append((rect, (i, j)))
            
            if clicked[j][i] == 1:
                pygame.draw.rect(screen, GOLD, rect)
            elif active_list[j] == 1:
                pygame.draw.rect(screen, GREEN, rect, 2)
            else:
                pygame.draw.rect(screen, GRAY, rect, 2)

    # Draw active beat marker
    pygame.draw.rect(screen, BLUE, (205 + active_beat * ((WIDTH - 200) // beats), 5, (WIDTH - 200) // beats, 600), 5, 3)

    # Draw UI elements
    ui_elements = [
        (add_bpm_rect, "+"), (bpm_sub_rect, "-"),
        (beats_add_rect, "+"), (beats_sub_rect, "-"),
        (play_pause, "Play/Pause"), (clear_button, "Clear"),
        (save_button, "Save"), (load_button, "Load")
    ]
    
    for rect, text in ui_elements:
        pygame.draw.rect(screen, GRAY, rect)
        screen.blit(medium_font.render(text, True, WHITE), rect.topleft)

    screen.blit(medium_font.render(f'BPM: {bpm}', True, WHITE), (250, HEIGHT - 140))
    screen.blit(medium_font.render(f'Beats: {beats}', True, WHITE), (550, HEIGHT - 140))

    return boxes

def play_notes():
    for i, sound in enumerate(sounds.values()):
        if clicked[i][active_beat] == 1 and active_list[i] == 1:
            sound.play()

def draw_save_menu(beat_name, typing):
    screen.fill(BLACK)
    exit_btn = pygame.draw.rect(screen, GRAY, (WIDTH - 200, HEIGHT - 100, 180, 90), 0, 5)
    saving_btn = pygame.draw.rect(screen, GRAY, (WIDTH // 2 - 200, HEIGHT * 0.75, 400, 100), 0, 5)
    entry_rect = pygame.draw.rect(screen, GRAY, (400, 200, 600, 200), 5, 5)
    
    screen.blit(label_font.render("Save Menu", True, WHITE), (440, 100))
    screen.blit(label_font.render("Save Beat", True, WHITE), (WIDTH // 2 - 70, HEIGHT * 0.75 + 30))
    screen.blit(label_font.render(beat_name, True, WHITE), (410, 210))
    screen.blit(label_font.render("Close", True, WHITE), (WIDTH - 160, HEIGHT - 70))
    
    if typing:
        pygame.draw.rect(screen, DARK_GRAY, entry_rect, 0)
    
    return exit_btn, saving_btn, entry_rect

def draw_load_menu(index):
    screen.fill(BLACK)
    exit_btn = pygame.draw.rect(screen, GRAY, (WIDTH - 200, HEIGHT - 100, 180, 90), 0, 5)
    loading_btn = pygame.draw.rect(screen, GRAY, (WIDTH // 2 - 200, HEIGHT * 0.87, 400, 100), 0, 5)
    delete_btn = pygame.draw.rect(screen, GRAY, (WIDTH // 2 - 485, HEIGHT * 0.87, 400, 100), 0, 5)
    loaded_rect = pygame.draw.rect(screen, GRAY, (190, 90, 1000, 600), 5, 5)
    
    screen.blit(label_font.render("Load Menu", True, WHITE), (440, 100))
    screen.blit(label_font.render("Load Beat", True, WHITE), (WIDTH // 2 - 70, HEIGHT * 0.87 + 30))
    screen.blit(label_font.render("Delete Beat", True, WHITE), (WIDTH // 2 - 485 + 30, HEIGHT * 0.87 + 30))
    screen.blit(label_font.render("Close", True, WHITE), (WIDTH - 160, HEIGHT - 70))
    
    for i, beat in enumerate(saved_beats):
        if i < 10:
            row_rect = pygame.Rect(190, 90 + i * 50, 1000, 50)
            if i == index:
                pygame.draw.rect(screen, LIGHT_GRAY, row_rect)
            screen.blit(medium_font.render(f"{i + 1}", True, WHITE), (200, 100 + i * 50))
            name = beat.split(',')[0].split(': ')[1]
            screen.blit(medium_font.render(name, True, WHITE), (240, 100 + i * 50))
    
    return exit_btn, loading_btn, delete_btn, loaded_rect

# Main game loop
while run:
    timer.tick(FPS)
    
    if not save_menu and not load_menu:
        boxes = draw_grid(clicked, active_beat)
    elif save_menu:
        exit_btn, saving_btn, entry_rect = draw_save_menu(beat_name, typing)
    elif load_menu:
        exit_btn, loading_btn, delete_btn, loaded_rect = draw_load_menu(index)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and not save_menu and not load_menu:
            for i, box in enumerate(boxes):
                if box[0].collidepoint(event.pos):
                    coords = box[1]
                    clicked[coords[1]][coords[0]] *= -1
        
        if event.type == pygame.MOUSEBUTTONUP:
            if not save_menu and not load_menu:
                if play_pause.collidepoint(event.pos):
                    playing = not playing
                elif clear_button.collidepoint(event.pos):
                    clicked = [[-1 for _ in range(beats)] for _ in range(6)]
                elif save_button.collidepoint(event.pos):
                    save_menu = True
                elif load_button.collidepoint(event.pos):
                    load_menu = True
                elif add_bpm_rect.collidepoint(event.pos):
                    bpm = min(bpm + 5, 300)
                elif bpm_sub_rect.collidepoint(event.pos):
                    bpm = max(bpm - 5, 60)
                elif beats_add_rect.collidepoint(event.pos):
                    beats += 1
                    for i in range(len(clicked)):
                        clicked[i].append(-1)
                elif beats_sub_rect.collidepoint(event.pos) and beats > 1:
                    beats -= 1
                    for i in range(len(clicked)):
                        clicked[i].pop()
                for i, rect in enumerate(instrument_rects):
                    if rect.collidepoint(event.pos):
                        active_list[i] *= -1
            elif save_menu:
                if exit_btn.collidepoint(event.pos):
                    save_menu = False
                    typing = False
                    beat_name = ""
                elif entry_rect.collidepoint(event.pos):
                    typing = not typing
                elif saving_btn.collidepoint(event.pos):
                    saved_beats.append(f"name: {beat_name}, beats: {beats}, bpm: {bpm}, selected: {clicked}\n")
                    with open("savedbeats.txt", "w") as f:
                        f.writelines(saved_beats)
                    save_menu = False
                    typing = False
                    beat_name = ""
            elif load_menu:
                if exit_btn.collidepoint(event.pos):
                    load_menu = False
                    index = 100
                elif loaded_rect.collidepoint(event.pos):
                    index = (event.pos[1] - 90) // 50
                elif delete_btn.collidepoint(event.pos):
                    if 0 <= index < len(saved_beats):
                        saved_beats.pop(index)
                        index = 100
                elif loading_btn.collidepoint(event.pos):
                    if 0 <= index < len(saved_beats):
                        beat_data = saved_beats[index].split(', ')
                        beats = int(beat_data[1].split(': ')[1])
                        bpm = int(beat_data[2].split(': ')[1])
                        clicked = eval(beat_data[3].split(': ')[1])
                        load_menu = False
                        index = 100
                        playing = True
        
        if event.type == pygame.TEXTINPUT and typing:
            beat_name += event.text
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE and len(beat_name) > 0 and typing:
                beat_name = beat_name[:-1]

    if playing:
        active_length += 1
        if active_length >= 60 * FPS // bpm:
            active_length = 0
            active_beat = (active_beat + 1) % beats
            play_notes()

    pygame.display.flip()

pygame.quit()