import pygame
import random
import os
import json
import time
import sys  # Importar sys para sys.exit()

pygame.init()

# Configuración de la pantalla
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Project Zombie')

# Obtener ruta del directorio actual
BASE_DIR = os.path.dirname(__file__)

# Cargar el icono del juego y establecerlo
icon_image = pygame.image.load(os.path.join(BASE_DIR, "assets/img", "icon.png"))
pygame.display.set_icon(icon_image)

# Cargar imágenes
background_menu_image = pygame.image.load(os.path.join(BASE_DIR, "assets/img", "background.png"))
background_game_image = pygame.image.load(os.path.join(BASE_DIR, "assets/img", "map.png"))
player_image = pygame.image.load(os.path.join(BASE_DIR, "assets/img", "player.png"))
bullet_image = pygame.image.load(os.path.join(BASE_DIR, "assets/img", "bullet.png"))
enemy_image = pygame.image.load(os.path.join(BASE_DIR, "assets/img", "enemy.png"))

# Redimensionar imágenes
background_menu_image = pygame.transform.scale(background_menu_image, (screen_width, screen_height))
background_game_image = pygame.transform.scale(background_game_image, (screen_width, screen_height))
player_image = pygame.transform.scale(player_image, (50, 50))
bullet_image = pygame.transform.scale(bullet_image, (5, 10))
enemy_image = pygame.transform.scale(enemy_image, (50, 50))

# Cargar sonidos
pygame.mixer.music.load(os.path.join(BASE_DIR, "assets/sounds", "background_music.mp3"))
pygame.mixer.music.play(-1)
shoot_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "assets/sounds", "shoot.wav"))
click_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "assets/sounds", "click.wav"))
hover_sound = click_sound  # Se reutiliza el sonido click para el hover

# Fuentes
font = pygame.font.Font(os.path.join(BASE_DIR, 'assets/front/pixel.otf'), 30)
font_large = pygame.font.Font(os.path.join(BASE_DIR, 'assets/front/pixel.otf'), 50)
font_xlarge = pygame.font.Font(os.path.join(BASE_DIR, 'assets/front/pixel.otf'), 70)  # Fuente extra grande para la pantalla de muerte
font_small = pygame.font.Font(os.path.join(BASE_DIR, 'assets/front/pixel.otf'), 15)

# Archivo game_data.json para guardar high score y configuración.
game_data_path = os.path.join(BASE_DIR, "game_data.json")
def load_game_data():
    if os.path.exists(game_data_path):
        with open(game_data_path, "r") as file:
            return json.load(file)
    return {"high_score": 0, "music_volume": 0.5, "sfx_volume": 0.5, "has_seen_story": False}

def save_game_data(data):
    with open(game_data_path, "w") as file:
        json.dump(data, file)

game_data = load_game_data()

# Configuración de sonido
music_volume = game_data.get("music_volume", 0.5)
sfx_volume = game_data.get("sfx_volume", 0.5)
pygame.mixer.music.set_volume(music_volume)
shoot_sound.set_volume(sfx_volume)
click_sound.set_volume(sfx_volume)

def set_music_volume(vol):
    global music_volume, game_data
    music_volume = max(0, min(1, vol))
    pygame.mixer.music.set_volume(music_volume)
    game_data["music_volume"] = music_volume
    save_game_data(game_data)

def set_sfx_volume(vol):
    global sfx_volume, game_data
    sfx_volume = max(0, min(1, vol))
    shoot_sound.set_volume(sfx_volume)
    click_sound.set_volume(sfx_volume)
    game_data["sfx_volume"] = sfx_volume
    save_game_data(game_data)

# Variables del jugador
player_x = screen_width // 2
player_y = screen_height - 60
player_velocity = 5
player_max_health = 20  # Vida máxima del jugador: 20 puntos
player_health = player_max_health  # Salud inicial

# Bala
bullet_velocity = 7
bullets = []  # Lista global de balas

# Enemigos
enemy_velocity = 2
enemy_spawn_rate = 50
enemies = []  # Lista global de enemigos

# Dificultad: (velocidad de enemigo, frecuencia de spawn)
difficulty_levels = {"easy": (1, 60), "medium": (2, 50), "hard": (5, 20)}
difficulty = "medium"

# Score
score = 0

def update_high_score(current_score):
    if current_score > game_data.get("high_score", 0):
        game_data["high_score"] = current_score
        save_game_data(game_data)

def adjust_difficulty():
    global enemy_velocity, enemy_spawn_rate
    enemy_velocity, enemy_spawn_rate = difficulty_levels[difficulty]

# Daño según la dificultad:
# Fácil: 2, Medio: 4, Difícil: 6 puntos de daño por colisión.
damage_levels = {"easy": 2, "medium": 4, "hard": 6}

# Variables para animación de botones
HOVER_COLOR = (210, 210, 210)
BASE_BUTTON_COLOR = (255, 255, 255)
CLICK_COLOR = (180, 180, 180)
last_hovered_index = None  # Para evitar repetir sonido hover

def draw_button(text, x, y, width=200, height=50, is_hovered=False, is_clicked=False):
    """Dibuja un botón con animación según el estado."""
    color = BASE_BUTTON_COLOR
    if is_clicked:
        color = CLICK_COLOR
    elif is_hovered:
        color = HOVER_COLOR
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, button_rect)
    pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)
    label = font.render(text, True, (0, 0, 0))
    screen.blit(label, (x + (width - label.get_width()) // 2, y + (height - label.get_height()) // 2))
    return button_rect

# Función para ciclar la dificultad (tipo Minecraft)
def cycle_difficulty():
    global difficulty
    if difficulty == "easy":
        difficulty = "medium"
    elif difficulty == "medium":
        difficulty = "hard"
    else:
        difficulty = "easy"
    adjust_difficulty()

# MENÚ PRINCIPAL (Minecraft Style con Estadísticas y sin Dificultad)

def show_main_menu():
    """Muestra el menú principal estilo Minecraft con Estadísticas."""
    global last_hovered_index
    menu_running = True
    last_hovered_index = None
    buttons = [
        {"text": "Jugar", "action": lambda: "game"},
        {"text": "Estadísticas", "action": lambda: "stats"},  # Botón de Estadísticas
        {"text": "Configuración", "action": lambda: "config"},
        {"text": "Salir", "action": lambda: sys.exit()}
    ]

    while menu_running:
        screen.blit(background_menu_image, (0, 0))
        title = font_large.render("Project Zombie", True, (255, 255, 255))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 50))

        # Credits and version
        credit_text = font_small.render("Créditos: PistonCube", True, (255, 255, 255))
        version_text = font_small.render("Version: V1.2 BETA", True, (255, 255, 255))
        screen.blit(credit_text, (10, screen_height - 20))
        screen.blit(version_text, (screen_width - version_text.get_width() - 10, screen_height - 20))

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        button_rects = []

        # Minecraft style button layout (centered column)
        start_y = screen_height // 2 - (len(buttons) * 60) // 2  # Center vertically
        for i, btn in enumerate(buttons):
            btn_x = screen_width // 2 - 100  # Centered
            btn_y = start_y + i * 60  # Vertical spacing
            is_hovered = pygame.Rect(btn_x, btn_y, 200, 50).collidepoint(mouse_pos)
            if is_hovered and last_hovered_index != i:
                hover_sound.play()
                last_hovered_index = i
            is_clicked = is_hovered and mouse_pressed
            rect = draw_button(btn["text"], btn_x, btn_y, 200, 50, is_hovered, is_clicked)
            button_rects.append(rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        click_sound.play()
                        result = buttons[i]["action"]()
                        if result == "game":
                            game_result = show_game_menu()
                            if game_result == "start":
                                return "start"
                        elif result == "stats":  # Acción para el botón de Estadísticas
                            show_statistics_screen()
                        elif result == "config":
                            show_configuration_menu()

        pygame.time.Clock().tick(60)

# MENÚ DE JUGAR (con Dificultad)

def show_game_menu():
    """Submenú de 'Jugar' con Dificultad."""
    game_running = True
    global last_hovered_index, difficulty
    last_hovered_index = None
    
    # Elimina la definición inicial de buttons aquí

    start_x = screen_width // 2 - 100  # Centrado
    start_y = screen_height // 2 - (3 * 60) // 2  # Centrado verticalmente (3 botones)
    spacing = 60

    while game_running:
        # Mueve la definición de buttons DENTRO del bucle
        buttons = [
            {"text": "Iniciar", "action": lambda: "start"},
            {"text": f"Dificultad: {difficulty.capitalize()}", "action": cycle_difficulty},
            {"text": "Volver", "action": lambda: "back"}
        ]
        
        screen.blit(background_menu_image, (0, 0))
        title = font_large.render("Jugar", True, (255, 255, 255))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 100))

        # Credits and version
        credit_text = font_small.render("Créditos: PistonCube", True, (255, 255, 255))
        version_text = font_small.render("Version: V1.2 BETA", True, (255, 255, 255))
        screen.blit(credit_text, (10, screen_height - 20))
        screen.blit(version_text, (screen_width - version_text.get_width() - 10, screen_height - 20))

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        button_rects = []
        for i, btn in enumerate(buttons):
            btn_x = start_x
            btn_y = start_y + i * spacing
            is_hovered = pygame.Rect(btn_x, btn_y, 200, 50).collidepoint(mouse_pos)
            if is_hovered and last_hovered_index != i:
                hover_sound.play()
                last_hovered_index = i
            is_clicked = is_hovered and mouse_pressed
            rect = draw_button(btn["text"], btn_x, btn_y, 200, 50, is_hovered, is_clicked)
            button_rects.append(rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        click_sound.play()
                        action = buttons[i]["action"]()
                        if action == "start":
                            return "start"
                        elif action == "back":
                            return "back"
        pygame.time.Clock().tick(60)

def show_statistics_screen():
    """Muestra una pantalla con las estadísticas del juego (por ejemplo, High Score)."""
    stats_running = True
    while stats_running:
        screen.blit(background_menu_image, (0, 0))
        title = font_large.render("Estadísticas", True, (255, 255, 255))
        screen.blit(title, (screen_width//2 - title.get_width()//2, 100))
        # Mostrar el High Score (puedes agregar más estadísticas si lo deseas)
        high_score_text = font.render("High Score: " + str(game_data.get("high_score", 0)), True, (255, 255, 255))
        screen.blit(high_score_text, (screen_width//2 - high_score_text.get_width()//2, 250))
        back_text = font.render("Pulsa cualquier tecla para volver", True, (255, 255, 255))
        screen.blit(back_text, (screen_width//2 - back_text.get_width()//2, screen_height - 100))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                stats_running = False
        pygame.time.Clock().tick(60)

# MENÚ DE CONFIGURACIÓN

def show_configuration_menu():
    """Muestra el menú de configuración con el slider de volumen."""
    config_running = True
    slider_x = 300
    slider_y = 250
    slider_width = 200
    slider_height = 20
    knob_radius = 10
    back_button = {"text": "Volver", "action": lambda: "back"}
    global last_hovered_index

    while config_running:
        screen.blit(background_menu_image, (0, 0))
        title = font_large.render("Configuración", True, (255, 255, 255))
        screen.blit(title, (screen_width//2 - title.get_width()//2, 100))
        
        # Slider música
        music_info = font_small.render("Volumen Música:", True, (255, 255, 255))
        screen.blit(music_info, (slider_x, slider_y - 40))
        pygame.draw.rect(screen, (100, 100, 100), (slider_x, slider_y, slider_width, slider_height))
        pygame.draw.rect(screen, (0, 0, 0), (slider_x, slider_y, slider_width, slider_height), 2)
        knob_x_music = slider_x + int(music_volume * slider_width)
        knob_y_music = slider_y + slider_height // 2
        pygame.draw.circle(screen, (200, 200, 200), (knob_x_music, knob_y_music), knob_radius)
        pygame.draw.circle(screen, (0, 0, 0), (knob_x_music, knob_y_music), knob_radius, 2)

        # Slider efectos
        sfx_info = font_small.render("Volumen Efectos:", True, (255, 255, 255))
        screen.blit(sfx_info, (slider_x, slider_y + 60 - 40))
        pygame.draw.rect(screen, (100, 100, 100), (slider_x, slider_y + 60, slider_width, slider_height))
        pygame.draw.rect(screen, (0, 0, 0), (slider_x, slider_y + 60, slider_width, slider_height), 2)
        knob_x_sfx = slider_x + int(sfx_volume * slider_width)
        knob_y_sfx = slider_y + 60 + slider_height // 2
        pygame.draw.circle(screen, (200, 200, 200), (knob_x_sfx, knob_y_sfx), knob_radius)
        pygame.draw.circle(screen, (0, 0, 0), (knob_x_sfx, knob_y_sfx), knob_radius, 2)

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        back_button_rect = draw_button(back_button["text"], screen_width//2 - 100, slider_y + 140, 200, 50,
                                        is_hovered=pygame.Rect(screen_width//2 - 100, slider_y + 140, 200, 50).collidepoint(mouse_pos),
                                        is_clicked=mouse_pressed)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Control slider música
                music_slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
                if music_slider_rect.collidepoint(event.pos):
                    rel_x = event.pos[0] - slider_x
                    new_volume = rel_x / slider_width
                    set_music_volume(new_volume)
                
                # Control slider efectos
                sfx_slider_rect = pygame.Rect(slider_x, slider_y + 60, slider_width, slider_height)
                if sfx_slider_rect.collidepoint(event.pos):
                    rel_x = event.pos[0] - slider_x
                    new_volume = rel_x / slider_width
                    set_sfx_volume(new_volume)
            
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    # Actualizar volumen música
                    music_slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
                    if music_slider_rect.collidepoint(event.pos):
                        rel_x = event.pos[0] - slider_x
                        new_volume = rel_x / slider_width
                        set_music_volume(new_volume)
                    
                    # Actualizar volumen efectos
                    sfx_slider_rect = pygame.Rect(slider_x, slider_y + 60, slider_width, slider_height)
                    if sfx_slider_rect.collidepoint(event.pos):
                        rel_x = event.pos[0] - slider_x
                        new_volume = rel_x / slider_width
                        set_sfx_volume(new_volume)
            
            if event.type == pygame.MOUSEBUTTONUP:
                if back_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    config_running = False
        pygame.time.Clock().tick(60)

# MENÚ DE PAUSA

def pause_menu_buttons():
    """Devuelve la lista de botones del menú de pausa."""
    return [
        {"text": "Continuar", "action": lambda: "resume"},
        {"text": "Configuración", "action": lambda: "config"},
        {"text": "Menú Principal", "action": lambda: "main_menu"}
    ]

def pause_menu():
    """Muestra el menú de pausa con el fondo del mapa y superposición negra semitransparente."""
    global last_hovered_index
    pause_running = True
    buttons = pause_menu_buttons()
    start_x = screen_width//2 - 100
    start_y = screen_height//2 - 100
    spacing = 70
    last_hovered_index = None

    while pause_running:
        screen.blit(background_game_image, (0, 0))
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        pause_title = font_large.render("PAUSA", True, (255, 255, 255))
        screen.blit(pause_title, (screen_width//2 - pause_title.get_width()//2, start_y - 80))

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        button_rects = []
        for i, btn in enumerate(buttons):
            btn_x = start_x
            btn_y = start_y + i*spacing
            is_hovered = pygame.Rect(btn_x, btn_y, 200, 50).collidepoint(mouse_pos)
            if is_hovered and last_hovered_index != i:
                hover_sound.play()
                last_hovered_index = i
            is_clicked = is_hovered and mouse_pressed
            rect = draw_button(btn["text"], btn_x, btn_y, 200, 50, is_hovered, is_clicked)
            button_rects.append(rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"
            if event.type == pygame.MOUSEBUTTONUP:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        click_sound.play()
                        action = buttons[i]["action"]()
                        if action == "config":
                            show_configuration_menu()
                        if action in ("resume", "main_menu"):
                            return action
        pygame.time.Clock().tick(60)

# BARRA DE VIDA

def draw_health_bar(x, y, health, max_health):
    bar_width = 200
    bar_height = 20
    fill = (health / max_health) * bar_width
    pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, fill, bar_height))
    pygame.draw.rect(screen, (0, 0, 0), (x, y, bar_width, bar_height), 2)

# PANTALLA DE MUERTE

def show_dead_screen():
    """Muestra una pantalla de muerte estilizada con fondo del mapa, overlay rojo semitransparente y mensaje en grande."""
    dead_running = True
    clock = pygame.time.Clock()
    fade = 0  # Valor inicial para el efecto de fundido
    
    while dead_running:
        screen.blit(background_game_image, (0, 0))
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill((150, 0, 0))
        if fade < 180:
            fade = min(180, fade + 2)
        overlay.set_alpha(fade)
        screen.blit(overlay, (0, 0))
        
        mensaje = "¡Has caído!"
        text_shadow = font_xlarge.render(mensaje, True, (0, 0, 0))
        text_main = font_xlarge.render(mensaje, True, (255, 255, 255))
        text_x = screen_width//2 - text_main.get_width()//2
        text_y = screen_height//2 - text_main.get_height() - 50
        screen.blit(text_shadow, (text_x+4, text_y+4))
        screen.blit(text_main, (text_x, text_y))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        btn_menu = draw_button("Menú Principal", screen_width//2 - 220, screen_height//2 + 20,
                                width=200, height=60,
                                is_hovered=pygame.Rect(screen_width//2 - 220, screen_height//2 + 20, 200, 60).collidepoint(mouse_pos),
                                is_clicked=mouse_pressed)
        btn_retry = draw_button("Reintentar", screen_width//2 + 20, screen_height//2 + 20,
                                 width=200, height=60,
                                 is_hovered=pygame.Rect(screen_width//2 + 20, screen_height//2 + 20, 200, 60).collidepoint(mouse_pos),
                                 is_clicked=mouse_pressed)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if btn_menu.collidepoint(event.pos):
                    click_sound.play()
                    return "main_menu"
                if btn_retry.collidepoint(event.pos):
                    click_sound.play()
                    return "retry"
        clock.tick(60)

# BUCLE PRINCIPAL DEL JUEGO

def main():
    """Bucle principal del juego."""
    global player_x, player_y, bullets, enemies, player_health, score
    clock = pygame.time.Clock()
    spawn_enemy_timer = 0
    running = True
    adjust_difficulty()

    player_x = screen_width//2
    player_y = screen_height - 60
    player_health = player_max_health
    bullets.clear()
    enemies.clear()
    score = 0

    while running:
        screen.blit(background_game_image, (0, 0))
        spawn_enemy_timer += 1
        if spawn_enemy_timer > enemy_spawn_rate:
            spawn_enemy_timer = 0
            enemy_x = random.randint(0, screen_width - 50)
            enemies.append([enemy_x, 0])
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    action = pause_menu()
                    if action == "main_menu":
                        return "main_menu"
                if event.key == pygame.K_SPACE:
                    shoot_sound.play()
                    bullets.append([player_x + 22, player_y])
            if event.type == pygame.MOUSEBUTTONDOWN:
                shoot_sound.play()
                bullets.append([player_x + 22, player_y])
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player_x > 0:
            player_x -= player_velocity
        if keys[pygame.K_d] and player_x < screen_width - 50:
            player_x += player_velocity

        for bullet in bullets[:]:
            bullet[1] -= bullet_velocity
            if bullet[1] < 0:
                bullets.remove(bullet)
        for bullet in bullets:
            screen.blit(bullet_image, (bullet[0], bullet[1]))

        for enemy in enemies[:]:
            if player_x < enemy[0]:
                enemy[0] -= 1
            elif player_x > enemy[0]:
                enemy[0] += 1
            enemy[1] += enemy_velocity

            enemy_rect = pygame.Rect(enemy[0], enemy[1], 50, 50)
            for bullet in bullets[:]:
                bullet_rect = pygame.Rect(bullet[0], bullet[1], bullet_image.get_width(), bullet_image.get_height())
                if enemy_rect.colliderect(bullet_rect):
                    if enemy in enemies:
                        enemies.remove(enemy)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    score += 10
                    break

            player_rect = pygame.Rect(player_x, player_y, 50, 50)
            if player_rect.colliderect(enemy_rect):
                damage = damage_levels.get(difficulty, 2)
                player_health -= damage
                if enemy in enemies:
                    enemies.remove(enemy)
                if player_health <= 0:
                    running = False

        for enemy in enemies:
            screen.blit(enemy_image, (enemy[0], enemy[1]))

        screen.blit(player_image, (player_x, player_y))
        draw_health_bar(10, 10, player_health, player_max_health)
        score_text = font_small.render("Score: " + str(score), True, (255, 255, 255))
        screen.blit(score_text, (220, 10))
        pygame.display.flip()
        clock.tick(60)
    
    update_high_score(score)
    if player_health <= 0:
        return show_dead_screen()
    pygame.time.delay(1000)

if __name__ == "__main__":
    if not game_data.get("has_seen_story", False):
        def show_story():
            story_text = [
                "Bienvenido a Project Zombie.",
                "En un mundo devastado por hordas de zombies,",
                "tu misión es sobrevivir y eliminar a la amenaza.",
                "Recorre las calles, dispara sin piedad, y recupera",
                "la esperanza perdida de la humanidad.",
                "",
                "Pulsa cualquier tecla para continuar..."
            ]
            showing = True
            while showing:
                screen.fill((0, 0, 0))
                y_offset = 150
                for line in story_text:
                    rendered_line = font.render(line, True, (255, 255, 255))
                    screen.blit(rendered_line, (screen_width//2 - rendered_line.get_width()//2, y_offset))
                    y_offset += 40
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                        showing = False
            game_data["has_seen_story"] = True
            save_game_data(game_data)
        show_story()
    while True:  # Main game loop
        action = show_main_menu()
        if action == "start":
            result = main()
            if result in ("main_menu", "retry"):
                continue  # Go back to main menu or retry