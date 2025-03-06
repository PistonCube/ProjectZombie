# Initial setup
import os
import pygame
import random
import json
import sys
import locale
import time
import zipfile
from pypresence import Presence
import atexit

# Directory configuration
APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), '.projectzombie')
os.makedirs(APP_DATA_DIR, exist_ok=True)

# Asset extraction system
def extract_assets():
    target_dir = os.path.join(APP_DATA_DIR, "assets")
    if os.path.exists(target_dir):
        return

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    
    assets_zip_path = os.path.join(base_path, "assets.zip")
    
    if not os.path.exists(assets_zip_path):
        raise FileNotFoundError(f"Archivo assets.zip no encontrado en: {assets_zip_path}")
    
    with zipfile.ZipFile(assets_zip_path, 'r') as zip_ref:
        zip_ref.extractall(target_dir)

# Game data management
def load_game_data():
    default_data = {
        "high_score": 0,
        "music_volume": 0.5,
        "sfx_volume": 0.5,
        "has_seen_story": False,
        "language": "en_us",
        "resolution": {"width": 800, "height": 600},
        "fullscreen": True
    }
    
    game_data_path = os.path.join(APP_DATA_DIR, "game_data.json")
    if os.path.exists(game_data_path):
        with open(game_data_path, "r") as file:
            try:
                loaded_data = json.load(file)
                for key in default_data:
                    if key not in loaded_data:
                        loaded_data[key] = default_data[key]
                return loaded_data
            except json.JSONDecodeError:
                return default_data
    return default_data

def save_game_data(data):
    with open(os.path.join(APP_DATA_DIR, "game_data.json"), "w") as file:
        json.dump(data, file, indent=4)

game_data = load_game_data()
save_game_data(game_data)  # Guardar defaults si es primera ejecución

# Initialize Pygame
pygame.init()

# Screen configuration
screen = pygame.display.set_mode(
    (game_data["resolution"]["width"], game_data["resolution"]["height"])
)
pygame.display.set_caption('Project Zombie')

# Discord RPC setup
client_id = '1346887066297827409'
RPC = Presence(client_id)
try:
    RPC.connect()
except Exception as e:
    print(f"Discord RPC connection error: {e}")

atexit.register(RPC.close)
game_version = "V1.3 BETA"

# Sistema de extracción de assets
def extract_assets():
    target_dir = os.path.join(APP_DATA_DIR, "assets")
    if os.path.exists(target_dir):
        return

    # Determinar ruta base según si está empaquetado
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    
    assets_zip_path = os.path.join(base_path, "assets.zip")
    
    if not os.path.exists(assets_zip_path):
        raise FileNotFoundError(f"Archivo assets.zip no encontrado en: {assets_zip_path}")
    
    print(f"Extrayendo assets a {target_dir}...")
    with zipfile.ZipFile(assets_zip_path, 'r') as zip_ref:
        zip_ref.extractall(target_dir)

# Configuración de directorios
APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), '.projectzombie')
os.makedirs(APP_DATA_DIR, exist_ok=True)
extract_assets()  # Extraer assets después de crear directorio

ASSETS_DIR = os.path.join(APP_DATA_DIR, "assets")
LANG_DIR = os.path.join(ASSETS_DIR, "lang")
game_data_path = os.path.join(APP_DATA_DIR, "game_data.json")

DEFAULT_LANG = "en_us"
LANGUAGES = ["en_us", "es_es"]

def get_system_language():
    try:
        lang, _ = locale.getlocale()
        return lang.lower().replace("-", "_") if lang else DEFAULT_LANG
    except:
        return DEFAULT_LANG

def load_language(lang_code):
    lang_path = os.path.join(LANG_DIR, f"{lang_code}.json")
    if not os.path.exists(lang_path):
        lang_path = os.path.join(LANG_DIR, f"{DEFAULT_LANG}.json")
    
    with open(lang_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_game_data():
    default_data = {
        "high_score": 0,
        "music_volume": 0.5,
        "sfx_volume": 0.5,
        "has_seen_story": False,
        "language": get_system_language(),
        "resolution": {"width": 800, "height": 600},
        "fullscreen": True
    }
    
    if os.path.exists(game_data_path):
        with open(game_data_path, "r") as file:
            try:
                loaded_data = json.load(file)
                for key in default_data:
                    if key not in loaded_data:
                        loaded_data[key] = default_data[key]
                return loaded_data
            except json.JSONDecodeError:
                return default_data
    return default_data

def save_game_data(data):
    with open(game_data_path, "w") as file:
        json.dump(data, file, indent=4)

game_data = load_game_data()
save_game_data(game_data)
current_lang = game_data["language"]

lang_data = load_language(current_lang)

def change_language(new_lang):
    global current_lang, lang_data, game_data
    if new_lang in LANGUAGES:
        current_lang = new_lang
        lang_data = load_language(new_lang)
        game_data["language"] = new_lang
        save_game_data(game_data)

# Sistema de recursos
def load_image(path, size=None):
    img = pygame.image.load(os.path.join(ASSETS_DIR, "img", path))
    return pygame.transform.scale(img, size) if size else img

def load_sound(path):
    try:
        return pygame.mixer.Sound(os.path.join(ASSETS_DIR, "sounds", path))
    except Exception as e:
        print(f"Error cargando sonido: {e}")
        return pygame.mixer.Sound(os.path.join(ASSETS_DIR, "sounds", "placeholder.wav"))

# Carga de assets
icon_image = load_image("icon.png")
background_menu_image = load_image("background.png", (game_data["resolution"]["width"], game_data["resolution"]["height"]))
background_game_image = load_image("map.png", (game_data["resolution"]["width"], game_data["resolution"]["height"]))
player_image = load_image("player.png", (50, 50))
bullet_image = load_image("bullet.png", (5, 10))
enemy_image = load_image("enemy.png", (50, 50))

pygame.display.set_icon(icon_image)

# Configuración de audio
pygame.mixer.music.load(os.path.join(ASSETS_DIR, "sounds", "background_music.mp3"))
shoot_sound = load_sound("shoot.wav")
click_sound = load_sound("click.wav")
hover_sound = click_sound

# Audio configuration
def apply_audio_settings():
    pygame.mixer.music.set_volume(game_data["music_volume"])
    shoot_sound.set_volume(game_data["sfx_volume"])
    click_sound.set_volume(game_data["sfx_volume"])
    hover_sound.set_volume(game_data["sfx_volume"])

apply_audio_settings()

# UI system settings
HOVER_COLOR = (210, 210, 210)
BASE_COLOR = (255, 255, 255)
CLICK_COLOR = (180, 180, 180)
last_hovered = None

def apply_audio_settings():
    pygame.mixer.music.set_volume(game_data["music_volume"])
    shoot_sound.set_volume(game_data["sfx_volume"])
    click_sound.set_volume(game_data["sfx_volume"])
    hover_sound.set_volume(game_data["sfx_volume"])

apply_audio_settings()

# Fuentes
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "pixel.otf")
font = pygame.font.Font(FONT_PATH, 24)
font_large = pygame.font.Font(FONT_PATH, 36)
font_xlarge = pygame.font.Font(FONT_PATH, 48)
font_small = pygame.font.Font(FONT_PATH, 18)

# Sistema de resolución
RESOLUTIONS = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
current_res_index = RESOLUTIONS.index(
    (game_data["resolution"]["width"], game_data["resolution"]["height"])
) if (game_data["resolution"]["width"], game_data["resolution"]["height"]) in RESOLUTIONS else 0

def cycle_resolution():
    global current_res_index, game_data
    current_res_index = (current_res_index + 1) % len(RESOLUTIONS)
    new_width, new_height = RESOLUTIONS[current_res_index]
    game_data["resolution"]["width"] = new_width
    game_data["resolution"]["height"] = new_height
    apply_resolution()

def apply_resolution():
    global screen, background_menu_image, background_game_image
    flags = pygame.FULLSCREEN if game_data["fullscreen"] else 0
    screen = pygame.display.set_mode((game_data["resolution"]["width"], game_data["resolution"]["height"]), flags)
    background_menu_image = load_image("background.png", (game_data["resolution"]["width"], game_data["resolution"]["height"]))
    background_game_image = load_image("map.png", (game_data["resolution"]["width"], game_data["resolution"]["height"]))

def draw_button(text, x, y, width=180, height=40, is_hovered=False, is_clicked=False):
    color = CLICK_COLOR if is_clicked else HOVER_COLOR if is_hovered else BASE_COLOR
    btn_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, btn_rect)
    pygame.draw.rect(screen, (0, 0, 0), btn_rect, 2)
    text_surf = font_small.render(text, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=btn_rect.center)
    screen.blit(text_surf, text_rect)
    return btn_rect

def draw_health_bar(x, y, current, max):
    bar_width = 200
    bar_height = 20
    fill = (current / max) * bar_width
    pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, fill, bar_height))

def handle_hover_sound(hover_elements, mouse_pos):
    global last_hovered
    current_hover = None
    
    hovered = [identifier for identifier, rect in hover_elements if rect.collidepoint(mouse_pos)]
    
    if hovered:
        current_hover = hovered[0]
    
    if current_hover != last_hovered:
        if current_hover is not None:
            hover_sound.play()
        last_hovered = current_hover

# Variables del juego
player_x = game_data["resolution"]["width"] // 2
player_y = game_data["resolution"]["height"] - 60
player_velocity = 5
player_max_health = 20
player_health = player_max_health
bullet_velocity = 7
bullets = []
enemies = []
difficulty_levels = {
    "easy": {"speed": 1, "spawn_rate": 60, "damage": 2},
    "medium": {"speed": 2, "spawn_rate": 50, "damage": 4},
    "hard": {"speed": 5, "spawn_rate": 20, "damage": 6}
}
difficulty = "medium"
enemy_velocity = difficulty_levels[difficulty]["speed"]
enemy_spawn_rate = difficulty_levels[difficulty]["spawn_rate"]
enemy_damage = difficulty_levels[difficulty]["damage"]
score = 0

def update_high_score(current_score):
    if current_score > game_data["high_score"]:
        game_data["high_score"] = current_score
        save_game_data(game_data)

def adjust_difficulty():
    global enemy_velocity, enemy_spawn_rate, enemy_damage
    settings = difficulty_levels[difficulty]
    enemy_velocity = settings["speed"]
    enemy_spawn_rate = settings["spawn_rate"]
    enemy_damage = settings["damage"]

def cycle_difficulty():
    global difficulty
    difficulties = list(difficulty_levels.keys())
    current_index = difficulties.index(difficulty)
    difficulty = difficulties[(current_index + 1) % len(difficulties)]
    adjust_difficulty()

# Menús
def show_main_menu():
    global last_hovered
    last_hovered = None
    while True:
        screen.blit(background_menu_image, (0, 0))
        title = font_xlarge.render(lang_data.get("title", "Project Zombie"), True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        credit_text = font_small.render("Créditos: PistonCube", True, (255, 255, 255))
        version_text = font_small.render("Versión: v1.3 BETA", True, (255, 255, 255))
        screen.blit(credit_text, (10, screen.get_height() - 20))
        screen.blit(version_text, (screen.get_width() - version_text.get_width() - 10, screen.get_height() - 20))

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        buttons = [
            {"text": lang_data.get("play_button", "Play"), "action": "play"},
            {"text": lang_data.get("config_button", "Settings"), "action": "config"},
            {"text": lang_data.get("quit_button", "Quit"), "action": "quit"}
        ]
        
        button_rects = []
        hover_elements = []
        start_y = screen.get_height()//2 - 50
        
        for i, btn in enumerate(buttons):
            btn_y = start_y + i * 60
            rect = draw_button(btn["text"], 
                             screen.get_width()//2 - 90, 
                             btn_y, 
                             width=180, 
                             height=40)
            button_rects.append(rect)
            hover_elements.append((btn["action"], rect))
        
        handle_hover_sound(hover_elements, mouse_pos)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        click_sound.play()
                        return buttons[i]["action"]

def show_game_menu():
    global last_hovered, difficulty
    last_hovered = None
    buttons = [
        {"text": lang_data.get("start_button", "Start Game"), "action": "start"},
        {"text": f"{lang_data.get('difficulty_button', 'Difficulty: ')}{lang_data.get(f'difficulty_{difficulty}', 'Medium')}", "action": "cycle_diff"},
        {"text": lang_data.get("back_button", "Back"), "action": "back"}
    ]
    
    while True:
        screen.blit(background_menu_image, (0, 0))
        title = font_large.render(lang_data.get("select_difficulty", "Select Difficulty"), True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        button_rects = []
        hover_elements = []
        start_y = screen.get_height()//2 - 100
        
        for i, btn in enumerate(buttons):
            btn_y = start_y + i * 60
            rect = draw_button(btn["text"], 
                             screen.get_width()//2 - 150, 
                             btn_y, 300, 40,
                             is_clicked=mouse_pressed)
            button_rects.append(rect)
            hover_elements.append((btn["action"], rect))
        
        handle_hover_sound(hover_elements, mouse_pos)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        click_sound.play()
                        action = buttons[i]["action"]
                        if action == "start":
                            return "start"
                        elif action == "cycle_diff":
                            cycle_difficulty()
                            buttons[1]["text"] = f"{lang_data.get('difficulty_button', 'Difficulty: ')}{lang_data.get(f'difficulty_{difficulty}', 'Medium')}"
                        elif action == "back":
                            return "back"

def show_configuration_menu():
    global last_hovered
    last_hovered = None
    
    while True:
        screen.blit(background_menu_image, (0, 0))
        title = font_large.render(lang_data.get("config_title", "Settings"), True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))

        buttons = [
            {"text": lang_data.get("video_button", "Video"), "action": "video"},
            {"text": lang_data.get("language_button", "Language"), "action": "language"},
            {"text": lang_data.get("audio_button", "Audio"), "action": "audio"},
            {"text": lang_data.get("back_button", "Back"), "action": "back"}
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        button_rects = []
        hover_elements = []
        start_y = screen.get_height()//2 - 150
        
        for i, btn in enumerate(buttons):
            btn_y = start_y + i * 60
            rect = draw_button(btn["text"], 
                            screen.get_width()//2 - 150, 
                            btn_y, 300, 40,
                            is_clicked=mouse_pressed)
            button_rects.append(rect)
            hover_elements.append((btn["action"], rect))
        
        handle_hover_sound(hover_elements, mouse_pos)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        click_sound.play()
                        action = buttons[i]["action"]
                        if action == "video":
                            show_video_menu()
                        elif action == "audio":
                            show_audio_menu()
                        elif action == "language":
                            show_language_menu()
                        elif action == "back":
                            return

def show_video_menu():
    global current_res_index, game_data
    apply_resolution()
    
    while True:
        screen.blit(background_menu_image, (0, 0))
        title = font_large.render(lang_data.get("video_settings", "Video Settings"), True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))

        current_res = (game_data["resolution"]["width"], game_data["resolution"]["height"])
        fs_state = lang_data.get("on" if game_data["fullscreen"] else "off", "On" if game_data["fullscreen"] else "Off")
        
        # Botón de Resolución
        res_text = f"{current_res[0]}x{current_res[1]}"
        res_btn = draw_button(f"{lang_data.get('resolution', 'Resolution')}: {res_text}", 
                            screen.get_width()//2 - 200, 150, 400, 40)
        
        # Botón Fullscreen
        fs_btn = draw_button(f"{lang_data.get('fullscreen', 'Fullscreen')}: {fs_state}", 
                           screen.get_width()//2 - 200, 220, 400, 40)
        
        # Botón Atrás
        back_btn = draw_button(lang_data.get("back_button", "Back"), 
                             screen.get_width()//2 - 100, 300, 200, 40)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if res_btn.collidepoint(event.pos):
                    cycle_resolution()
                    click_sound.play()
                if fs_btn.collidepoint(event.pos):
                    game_data["fullscreen"] = not game_data["fullscreen"]
                    apply_resolution()
                    click_sound.play()
                if back_btn.collidepoint(event.pos):
                    save_game_data(game_data)
                    return

def show_audio_menu():
    slider_width = 300
    knob_radius = 10
    
    while True:
        screen.blit(background_menu_image, (0, 0))
        title = font_large.render(lang_data.get("audio_settings", "Audio Settings"), True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))
        
        # Configuración de volumen
        y = 150
        screen.blit(font.render(lang_data.get("music_volume", "Music Volume:"), True, (255, 255, 255)), (100, y))
        music_slider_rect = pygame.Rect(100, y + 40, slider_width, 20)
        pygame.draw.rect(screen, (100, 100, 100), music_slider_rect)
        pygame.draw.rect(screen, (0, 200, 0), (100, y + 40, game_data["music_volume"] * slider_width, 20))
        pygame.draw.circle(screen, (200, 200, 200), 
                         (100 + int(game_data["music_volume"] * slider_width), y + 50), 
                         knob_radius)
        
        y += 100
        screen.blit(font.render(lang_data.get("sfx_volume", "SFX Volume:"), True, (255, 255, 255)), (100, y))
        sfx_slider_rect = pygame.Rect(100, y + 40, slider_width, 20)
        pygame.draw.rect(screen, (100, 100, 100), sfx_slider_rect)
        pygame.draw.rect(screen, (0, 200, 0), (100, y + 40, game_data["sfx_volume"] * slider_width, 20))
        pygame.draw.circle(screen, (200, 200, 200), 
                         (100 + int(game_data["sfx_volume"] * slider_width), y + 50), 
                         knob_radius)
        
        # Botón Atrás
        back_btn = draw_button(lang_data.get("back_button", "Back"), 
                             screen.get_width()//2 - 100, 500, 200, 40)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if music_slider_rect.collidepoint(event.pos):
                    new_vol = (event.pos[0] - 100) / slider_width
                    game_data["music_volume"] = max(0.0, min(1.0, new_vol))
                    apply_audio_settings()
                
                if sfx_slider_rect.collidepoint(event.pos):
                    new_vol = (event.pos[0] - 100) / slider_width
                    game_data["sfx_volume"] = max(0.0, min(1.0, new_vol))
                    apply_audio_settings()
            
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    if music_slider_rect.collidepoint(event.pos):
                        new_vol = (event.pos[0] - 100) / slider_width
                        game_data["music_volume"] = max(0.0, min(1.0, new_vol))
                        apply_audio_settings()
                    
                    if sfx_slider_rect.collidepoint(event.pos):
                        new_vol = (event.pos[0] - 100) / slider_width
                        game_data["sfx_volume"] = max(0.0, min(1.0, new_vol))
                        apply_audio_settings()
            
            if event.type == pygame.MOUSEBUTTONUP:
                if back_btn.collidepoint(event.pos):
                    save_game_data(game_data)
                    return

def show_language_menu():
    while True:
        screen.blit(background_menu_image, (0, 0))
        title = font_large.render(lang_data.get("language_settings", "Language Settings"), True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))
        
        y = 150
        lang_buttons = []
        for i, (lang_code, lang_name) in enumerate(lang_data.get("languages", {"en_us": "English", "es_es": "Spanish"}).items()):
            btn_rect = draw_button(lang_name, 
                                screen.get_width()//2 - 150, 
                                y + i * 60, 300, 40,
                                is_hovered=lang_code == current_lang)
            lang_buttons.append((lang_code, btn_rect))
            if lang_code == current_lang:
                pygame.draw.rect(screen, (0, 255, 0), btn_rect.inflate(4, 4), 3)
        
        back_btn = draw_button(lang_data.get("back_button", "Back"), 
                             screen.get_width()//2 - 100, 400, 200, 40)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                for lang_code, rect in lang_buttons:
                    if rect.collidepoint(event.pos):
                        change_language(lang_code)
                        click_sound.play()
                
                if back_btn.collidepoint(event.pos):
                    return

def pause_menu():
    global last_hovered
    last_hovered = None
    while True:
        screen.blit(background_game_image, (0, 0))
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        title_text = lang_data.get("paused_title", "Paused")
        title = font_large.render(title_text, True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        buttons = [
            {"text": lang_data.get("resume_button", "Resume"), "action": "resume"},
            {"text": lang_data.get("restart_button", "Restart"), "action": "restart"},
            {"text": lang_data.get("menu_button", "Main Menu"), "action": "menu"}
        ]
        
        button_rects = []
        hover_elements = []
        start_y = screen.get_height()//2 - 50
        
        for i, btn in enumerate(buttons):
            btn_y = start_y + i * 60
            rect = draw_button(btn["text"], 
                             screen.get_width()//2 - 90, 
                             btn_y, 
                             width=180, 
                             height=40)
            button_rects.append(rect)
            hover_elements.append((btn["action"], rect))
        
        handle_hover_sound(hover_elements, mouse_pos)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"
            if event.type == pygame.MOUSEBUTTONUP:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        click_sound.play()
                        return buttons[i]["action"]

def show_dead_screen():
    global last_hovered
    last_hovered = None
    while True:
        screen.blit(background_game_image, (0, 0))
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.fill((150, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))
        
        title = font_xlarge.render(lang_data.get("game_over", "Game Over"), True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        score_text = font_large.render(f"{lang_data.get('final_score', 'Final Score')}: {score}", True, (255, 255, 255))
        screen.blit(score_text, (screen.get_width()//2 - score_text.get_width()//2, 200))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        buttons = [
            {"text": lang_data.get("retry_button", "Retry"), "action": "retry"},
            {"text": lang_data.get("menu_button", "Main Menu"), "action": "menu"}
        ]
        
        button_rects = []
        hover_elements = []
        start_y = screen.get_height()//2 + 50
        
        for i, btn in enumerate(buttons):
            btn_y = start_y + i * 60
            rect = draw_button(btn["text"], 
                             screen.get_width()//2 - 90, 
                             btn_y, 
                             width=180, 
                             height=40)
            button_rects.append(rect)
            hover_elements.append((btn["action"], rect))
        
        handle_hover_sound(hover_elements, mouse_pos)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        click_sound.play()
                        return buttons[i]["action"]

def show_story():
    story_texts = lang_data.get("story", "Welcome to Project Zombie").split('\n')
    running = True
    
    while running:
        # Fondo del menú
        screen.blit(background_menu_image, (0, 0))
        
        # Capa translúcida
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Configuración de texto
        y = 100
        line_spacing = 40
        
        for line in story_texts:
            text = font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width()//2, y))
            screen.blit(text, text_rect)
            y += line_spacing
        
        # Botón Continuar
        btn_rect = draw_button(lang_data.get("continue_button", "Continue"), 
                             screen.get_width()//2 - 90, 
                             screen.get_height() - 100,
                             width=180, 
                             height=40)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if btn_rect.collidepoint(event.pos):
                    click_sound.play()
                    running = False

def show_initial_language_selection():
    global last_hovered
    last_hovered = None
    buttons = [
        {"text": "English", "lang": "en_us"},
        {"text": "Español", "lang": "es_es"}
    ]
    
    while True:
        screen.blit(background_menu_image, (0, 0))
        
        # Fondo translúcido
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        title = font_xlarge.render("Select your language", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        button_rects = []
        hover_elements = []
        start_y = screen.get_height()//2 - 50
        
        for i, btn in enumerate(buttons):
            btn_y = start_y + i * 80
            rect = draw_button(btn["text"], 
                             screen.get_width()//2 - 90, 
                             btn_y, 180, 40,
                             is_clicked=mouse_pressed)
            button_rects.append(rect)
            hover_elements.append((btn["lang"], rect))
        
        handle_hover_sound(hover_elements, mouse_pos)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        click_sound.play()
                        change_language(buttons[i]["lang"])
                        return

# Game loop
def main_game_loop():
    global player_x, player_y, bullets, enemies, player_health, score
    clock = pygame.time.Clock()
    spawn_counter = 0
    game_start_time = time.time()
    
    try:
        RPC.update(
            state=lang_data.get("rpc_playing", "Playing"),
            details=lang_data.get("rpc_score", "Score: {score} | Version {version}").format(score=score, version=game_version),
            start=game_start_time,
            large_image="game",
            large_text=lang_data.get("rpc_game_status", "Zombie Survival"),
            buttons=[
                {"label": lang_data.get("download_button", "Download"), "url": "https://github.com/PistonCube/ProjectZombie/releases"},
                {"label": lang_data.get("website_button", "Website"), "url": "https://github.com/PistonCube/ProjectZombie/"}
            ]
        )
    except Exception as e:
        print(f"Error actualizando RPC: {e}")

    player_x = game_data["resolution"]["width"] // 2
    player_y = game_data["resolution"]["height"] - 60
    player_health = player_max_health
    bullets.clear()
    enemies.clear()
    score = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    shoot_sound.play()
                    bullets.append([player_x + 22, player_y])
                if event.key == pygame.K_ESCAPE:
                    result = pause_menu()
                    if result == "resume":
                        continue
                    elif result == "restart":
                        return "retry"
                    elif result == "menu":
                        return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                shoot_sound.play()
                bullets.append([player_x + 22, player_y])
        
        keys = pygame.key.get_pressed()
        player_x += (keys[pygame.K_d] - keys[pygame.K_a]) * player_velocity
        player_x = max(0, min(screen.get_width() - 50, player_x))
        
        bullets = [b for b in bullets if b[1] > 0]
        for b in bullets: b[1] -= bullet_velocity
        
        spawn_counter += 1
        if spawn_counter >= enemy_spawn_rate:
            spawn_counter = 0
            enemies.append([random.randint(0, screen.get_width() - 50), 0])
        
        for enemy in enemies[:]:
            enemy[0] += 1 if enemy[0] < player_x else -1
            enemy[1] += enemy_velocity
            
            enemy_rect = pygame.Rect(*enemy, 50, 50)
            if enemy_rect.colliderect(pygame.Rect(player_x, player_y, 50, 50)):
                player_health -= enemy_damage
                enemies.remove(enemy)
                if player_health <= 0:
                    update_high_score(score)
                    return show_dead_screen()
            
            for bullet in bullets[:]:
                if enemy_rect.colliderect(pygame.Rect(*bullet, 5, 10)):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 10
                    try:
                        RPC.update(details=lang_data.get("rpc_score", "Score: {score} | Version {version}").format(
                            score=score, version=game_version
                        ))
                    except Exception as e:
                        print(f"Error actualizando RPC: {e}")
                    break
        
        screen.blit(background_game_image, (0, 0))
        for bullet in bullets:
            screen.blit(bullet_image, bullet)
        for enemy in enemies:
            screen.blit(enemy_image, enemy)
        screen.blit(player_image, (player_x, player_y))
        
        draw_health_bar(10, 10, player_health, player_max_health)
        score_text = font_small.render(f"{lang_data.get('score', 'Score')}: {score}", True, (255, 255, 255))
        screen.blit(score_text, (220, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    update_high_score(score)
    return show_dead_screen()

# Main execution
if __name__ == "__main__":
    try:
        RPC.update(
            state=lang_data.get("rpc_menu_state", "In main menu"),
            details=lang_data.get("rpc_version", "Version {version}").format(version=game_version),
            large_image="main",
            large_text=lang_data.get("rpc_game_title", "Project Zombie"),
            buttons=[
                {"label": lang_data.get("download_button", "Download"), "url": "https://github.com/PistonCube/ProjectZombie/releases"},
                {"label": lang_data.get("website_button", "Website"), "url": "https://github.com/PistonCube/ProjectZombie/"}
            ]
        )
    except Exception as e:
        print(f"Error actualizando RPC: {e}")

    if not game_data["has_seen_story"]:
        show_initial_language_selection()
        show_story()
        game_data["has_seen_story"] = True
        save_game_data(game_data)
    
    pygame.mixer.music.play(-1)
    
    while True:
        action = show_main_menu()
        if action == "play":
            game_action = show_game_menu()
            if game_action == "start":
                try:
                    game_start_time = time.time()
                    RPC.update(
                        state=lang_data.get("rpc_playing", "Playing"),
                        details=lang_data.get("rpc_score", "Score: {score} | Version {version}").format(score=0, version=game_version),
                        start=game_start_time,
                        large_image="game",
                        large_text=lang_data.get("rpc_game_status", "Zombie Survival"),
                        buttons=[
                            {"label": lang_data.get("download_button", "Download"), "url": "https://github.com/PistonCube/ProjectZombie/releases"},
                            {"label": lang_data.get("website_button", "Website"), "url": "https://github.com/PistonCube/ProjectZombie/"}
                        ]
                    )
                except Exception as e:
                    print(f"Error actualizando RPC: {e}")
                
                result = main_game_loop()
                
                try:
                    RPC.update(
                        state=lang_data.get("rpc_menu_state", "In main menu"),
                        details=lang_data.get("rpc_version", "Version {version}").format(version=game_version),
                        large_image="main",
                        large_text=lang_data.get("rpc_game_title", "Project Zombie"),
                        buttons=[
                            {"label": lang_data.get("download_button", "Download"), "url": "https://github.com/PistonCube/ProjectZombie/releases"},
                            {"label": lang_data.get("website_button", "Website"), "url": "https://github.com/PistonCube/ProjectZombie/"}
                        ]
                    )
                except Exception as e:
                    print(f"Error updating RPC: {e}")
                
                if result == "retry":
                    main_game_loop()
                elif result == "menu":
                    continue
        elif action == "config":
            show_configuration_menu()
        elif action == "quit":
            pygame.quit()
            sys.exit()