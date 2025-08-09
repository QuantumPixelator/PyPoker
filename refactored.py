import pygame
import random
import sys
import os
import math
import json
import time ## REF-NOTE: Moved from the main loop to the top with other imports.

# --- Constants ---

## REF-NOTE: Grouping constants makes the code easier to configure and read.
# Screen and Display
WIDTH, HEIGHT = 800, 600
CAPTION = "PyPoker (High-Low)"
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GRAY = (100, 100, 100)
PULSE_YELLOW = (255, 215, 0)
OUTCOME_COLORS = {
    'win': (WHITE, (0, 90, 220)),
    'lose': (WHITE, (200, 0, 0)),
    'tie': (WHITE, (180, 120, 0)),
    'pass': (WHITE, (50, 120, 200)),
    'quit': (WHITE, (120, 120, 120)),
    'default': (WHITE, BLACK)
}


# Game Data
SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
VALUES = list(range(2, 15))  # 2-10, J=11, Q=12, K=13, A=14
VALUE_NAMES = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
## REF-NOTE: Added a map for filenames to simplify image loading.
VALUE_FILENAME_MAP = {
    11: 'jack', 12: 'queen', 13: 'king', 14: 'ace'
}
DEFAULT_MONEY = 100
DEFAULT_POT = 50

# UI Layout Constants
CARD_SIZE = (80, 120)
DECK_POS = (50, HEIGHT // 2 - 45)
CURRENT_CARD_POS = (WIDTH // 2 - 100, HEIGHT // 2 - 60)
NEXT_CARD_POS = (WIDTH // 2 + 20, HEIGHT // 2 - 60)
MSG_START_Y = 80
SLIDER_RECT = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 60, 300, 30)
BTN_Y = HEIGHT // 2 + 120
BTN_SIZE = (120, 40)
BET_TEXT_POS = (WIDTH // 2, HEIGHT - 40)


# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()

# --- Fonts ---
## REF-NOTE: More robust font loading with a clear fallback.
def load_font(name, size, bold=False, italic=False):
    try:
        return pygame.font.SysFont(name, size, bold=bold, italic=italic)
    except pygame.error:
        print(f"Warning: Font '{name}' not found. Falling back to default.")
        return pygame.font.SysFont(None, size, bold=bold, italic=italic)

font = load_font(None, 48)
small_font = load_font(None, 32)
display_font = load_font('comic sans ms', 42, bold=True)


# --- Asset Loading & Helpers ---

def load_settings():
    """Load settings from settings.json, with clear fallbacks."""
    try:
        with open("settings.json", "r") as f:
            data = json.load(f)
            return data.get("starting_money", DEFAULT_MONEY), data.get("starting_pot", DEFAULT_POT)
    ## REF-NOTE: Catching specific exceptions is better practice.
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Could not load settings.json: {e}. Using defaults.")
        return DEFAULT_MONEY, DEFAULT_POT

def create_placeholder_surface(size, text):
    """Creates a placeholder surface for missing images."""
    surf = pygame.Surface(size)
    surf.fill((180, 180, 180))
    pygame.draw.rect(surf, BLACK, surf.get_rect(), 2)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        text_surf = small_font.render(line, True, BLACK)
        x = size[0] // 2 - text_surf.get_width() // 2
        y = (size[1] // (len(lines) + 1)) * (i + 1) - text_surf.get_height() // 2
        surf.blit(text_surf, (x, y))
    return surf

def load_card_images():
    """Load and scale all card images once."""
    images = {}
    
    ## REF-NOTE: Image loading is now more efficient and DRY.
    def load_and_scale(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, CARD_SIZE)
        except pygame.error:
            return None

    for suit in SUITS:
        for value in VALUES:
            ## REF-NOTE: Simplified filename generation.
            val_str = VALUE_FILENAME_MAP.get(value, str(value))
            fname = f"{val_str}_of_{suit}.png"
            path = os.path.join("assets", fname)
            
            img = load_and_scale(path)
            if img is None:
                img = create_placeholder_surface(CARD_SIZE, f"{VALUE_NAMES.get(value, value)}\n{suit[0].upper()}")
            images[(value, suit)] = img
            
    # Load card back
    back_img = load_and_scale(os.path.join("assets", "back.png"))
    images['back'] = back_img if back_img else create_placeholder_surface(CARD_SIZE, "BACK")
    
    return images

## REF-NOTE: Assets are loaded once and stored, ready for use.
CARD_IMAGES = load_card_images()

def make_deck():
    deck = [(value, suit) for suit in SUITS for value in VALUES]
    random.shuffle(deck)
    return deck


# --- Text and UI Drawing Functions ---

def render_outlined_text(text, font, inner_color, outline_color, outline_px=2):
    base = font.render(text, True, inner_color)
    w, h = base.get_width(), base.get_height()
    surf = pygame.Surface((w + outline_px * 2, h + outline_px * 2), pygame.SRCALPHA)
    for dx in range(-outline_px, outline_px + 1):
        for dy in range(-outline_px, outline_px + 1):
            if dx * dx + dy * dy <= outline_px * outline_px:
                surf.blit(font.render(text, True, outline_color), (dx + outline_px, dy + outline_px))
    surf.blit(base, (outline_px, outline_px))
    return surf

def draw_button(text, x, y, w, h, active=True):
    color = BLUE if active else GRAY
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    txt = small_font.render(text, True, WHITE)
    screen.blit(txt, (x + (w - txt.get_width()) // 2, y + (h - txt.get_height()) // 2))
    return rect

def draw_slider(rect, min_val, max_val, value, dragging):
    pygame.draw.rect(screen, WHITE, (rect.x, rect.centery - 4, rect.w, 8))
    pygame.draw.rect(screen, BLACK, (rect.x, rect.centery - 4, rect.w, 8), 2)
    knob_x = rect.x + int((value - min_val) / (max_val - min_val) * rect.w) if max_val > min_val else rect.x
    knob_rect = pygame.Rect(knob_x - 10, rect.centery - 15, 20, 30)
    pygame.draw.rect(screen, RED if dragging else BLUE, knob_rect)
    pygame.draw.rect(screen, BLACK, knob_rect, 2)
    return knob_rect

def draw_card(card, x, y, face_up=True):
    ## REF-NOTE: This is much simpler now. It just blits a pre-loaded, pre-scaled image.
    key = card if face_up else 'back'
    screen.blit(CARD_IMAGES[key], (x, y))
    pygame.draw.rect(screen, BLACK, (x, y, CARD_SIZE[0], CARD_SIZE[1]), 3)

def animate_card_flip(card, x, y, progress):
    rect = pygame.Rect(x, y, *CARD_SIZE)
    pygame.draw.rect(screen, WHITE, rect)
    pygame.draw.rect(screen, BLACK, rect, 3)

    img = CARD_IMAGES[card]
    w = int(CARD_SIZE[0] * abs(math.cos(progress * math.pi))) # Using cosine for a smoother shrink/grow effect
    
    if w > 0:
        if progress > 0.5:
             # After the halfway point, draw the face-up card
             scaled_img = pygame.transform.scale(img, (w, CARD_SIZE[1]))
             screen.blit(scaled_img, (x + (CARD_SIZE[0] - w) // 2, y))
        else:
             # Before halfway, draw the back
             scaled_img = pygame.transform.scale(CARD_IMAGES['back'], (w, CARD_SIZE[1]))
             screen.blit(scaled_img, (x + (CARD_SIZE[0] - w) // 2, y))

## REF-NOTE: The original text wrapping logic was fine, this is just a cleanup to use the new constants.
def draw_message(text, outcome_type):
    inner, outline = OUTCOME_COLORS.get(outcome_type, OUTCOME_COLORS['default'])
    max_text_width = WIDTH - 60
    
    words = text.split()
    lines = []
    current_line = []
    while words:
        current_line.append(words.pop(0))
        test_surf = display_font.render(" ".join(current_line), True, inner)
        if test_surf.get_width() > max_text_width and len(current_line) > 1:
            words.insert(0, current_line.pop())
            lines.append(" ".join(current_line))
            current_line = []
    if current_line:
        lines.append(" ".join(current_line))
        
    current_y = MSG_START_Y
    for line_text in lines:
        rendered_surf = render_outlined_text(line_text, display_font, inner, outline, outline_px=3)
        screen.blit(rendered_surf, (WIDTH // 2 - rendered_surf.get_width() // 2, current_y))
        current_y += rendered_surf.get_height() + 8


# --- Game State Class ---
## REF-NOTE: Encapsulating state makes the main loop cleaner and the game's data easier to manage.
class GameState:
    def __init__(self):
        self.reset()
        self.button_rects = {}
        self.slider_knob_rect = pygame.Rect(0,0,0,0)

    def reset(self):
        """Resets the game to its initial state."""
        self.player_money, self.pot = load_settings()
        self.deck = make_deck()
        self.current_card = self.deck.pop()
        self.next_card = None
        self.last_cards = (None, None)
        
        self.message = "Adjust your bet and click Higher/Lower/Pass."
        self.outcome_type = None
        self.game_over = False
        
        self.bet_amount = 1
        self.slider_value = 1
        
        self.state = 'AWAITING_BET'  # 'AWAITING_BET', 'ANIMATING', 'SHOWING_RESULT', 'GAME_OVER'
        self.slider_dragging = False
        self.guess = None
        self.animation_progress = 0

    def check_for_reshuffle(self):
        if len(self.deck) < 3:
            self.deck = make_deck()
            print("Deck reshuffled.")

    def resolve_bet(self):
        val1 = self.current_card[0]
        val2 = self.next_card[0]
        v1_str = VALUE_NAMES.get(val1, str(val1))
        v2_str = VALUE_NAMES.get(val2, str(val2))
        
        win = (self.guess == 'higher' and val2 > val1) or \
              (self.guess == 'lower' and val2 < val1)
              
        if val2 == val1:
            self.player_money -= self.bet_amount * 2
            self.pot += self.bet_amount * 2
            self.message = f"Tie! You lose double: ${self.bet_amount*2}\n{v1_str} = {v2_str}"
            self.outcome_type = 'tie'
        elif win:
            self.player_money += self.bet_amount
            self.pot -= self.bet_amount
            comp = ">" if self.guess == 'lower' else "<"
            self.message = f"You win ${self.bet_amount}\n{v1_str} {comp} {v2_str}"
            self.outcome_type = 'win'
        else: # Loss
            self.player_money -= self.bet_amount
            self.pot += self.bet_amount
            comp = "<" if self.guess == 'lower' else ">"
            self.message = f"You lose ${self.bet_amount}\n{v1_str} {comp} {v2_str}"
            self.outcome_type = 'lose'

        self.last_cards = (self.current_card, self.next_card)
        self.state = 'SHOWING_RESULT'
        
        if self.player_money <= 0 or self.pot <= 0:
            self.game_over = True


# --- Main Game Loop ---

def main():
    game = GameState()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
                if game.state == 'AWAITING_BET':
                    if game.slider_knob_rect.collidepoint(mouse_pos):
                        game.slider_dragging = True
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                game.slider_dragging = False

            if event.type == pygame.MOUSEMOTION and game.slider_dragging:
                min_val = 1
                max_val = min(game.player_money, game.pot)
                if max_val >= min_val:
                    rel_x = min(max(mouse_pos[0] - SLIDER_RECT.x, 0), SLIDER_RECT.w)
                    game.slider_value = int(min_val + (max_val - min_val) * rel_x / SLIDER_RECT.w)
                    game.bet_amount = max(min_val, min(max_val, game.slider_value))

        # --- Button and Input Logic ---
        can_bet = game.state == 'AWAITING_BET'
        if mouse_clicked:
            if game.state == 'SHOWING_RESULT':
                if game.game_over:
                    game.state = 'GAME_OVER'
                    game.message = "Game over!\nPress Restart or Quit."
                else: # Next round
                    game.state = 'AWAITING_BET'
                    game.current_card = game.deck.pop()
                    game.next_card = None
                    game.last_cards = (None, None)
                    game.slider_value = 1
                    game.bet_amount = 1
                    game.message = "Adjust your bet and click a button."
                    game.outcome_type = None
                    game.check_for_reshuffle()

            elif game.state == 'AWAITING_BET':
                ## REF-NOTE: Consolidating button logic.
                for name, rect in game.button_rects.items():
                    if rect.collidepoint(mouse_pos):
                        if name in ('higher', 'lower'):
                            game.check_for_reshuffle()
                            game.next_card = game.deck.pop()
                            game.guess = name
                            game.state = 'ANIMATING'
                            game.animation_progress = 0
                        elif name == 'pass':
                            game.check_for_reshuffle()
                            game.current_card = game.deck.pop()
                            game.message = "Card passed. Adjust bet."
                            game.outcome_type = 'pass'
                        
            # Handle quit/restart buttons regardless of state
            if game.button_rects.get('quit', pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                if game.state != 'GAME_OVER':
                    game.state = 'GAME_OVER'
                    game.outcome_type = 'quit'
                    game.message = "You quit the game.\nPress Restart to play again."
            if game.button_rects.get('restart', pygame.Rect(0,0,0,0)).collidepoint(mouse_pos) and game.state == 'GAME_OVER':
                game.reset()

        # --- Game State Updates ---
        if game.state == 'ANIMATING':
            game.animation_progress += 0.05 # Slower for smoother animation
            if game.animation_progress >= 1.0:
                game.animation_progress = 1
                game.resolve_bet()

        # --- Drawing ---
        screen.fill(GREEN)

        # Money/Pot
        money_text = small_font.render(f"Your Money: ${game.player_money}", True, WHITE)
        pot_text = small_font.render(f"Pot: ${game.pot}", True, WHITE)
        screen.blit(money_text, (10, 10))
        screen.blit(pot_text, (10, 40))

        # Deck
        for i in range(min(len(game.deck), 5)):
             screen.blit(pygame.transform.scale(CARD_IMAGES['back'], (60, 90)), (DECK_POS[0] + i*5, DECK_POS[1] - i*2))

        # Cards
        draw_card(game.last_cards[0] or game.current_card, CURRENT_CARD_POS[0], CURRENT_CARD_POS[1])
        
        if game.state == 'ANIMATING':
            # Simplified call, logic now inside animate_card_flip
            animate_card_flip(game.next_card, NEXT_CARD_POS[0], NEXT_CARD_POS[1], game.animation_progress)
        elif game.next_card:
            draw_card(game.next_card, NEXT_CARD_POS[0], NEXT_CARD_POS[1])
        else:
            draw_card(None, NEXT_CARD_POS[0], NEXT_CARD_POS[1], face_up=False)

        # Message
        draw_message(game.message, game.outcome_type)

        if game.state == 'SHOWING_RESULT' and not game.game_over:
             pulse = abs(math.sin(time.time() * 3)) * 0.5 + 0.5
             glow_size = int(3 + pulse * 2)
             glow_color = (int(PULSE_YELLOW[0] * pulse), int(PULSE_YELLOW[1] * pulse), 0)
             continue_surf = render_outlined_text("Click anywhere to continue", font, WHITE, glow_color, glow_size)
             screen.blit(continue_surf, (WIDTH // 2 - continue_surf.get_width() // 2, HEIGHT // 2 + 80))

        # UI Elements
        game.button_rects.clear()
        if game.state == 'AWAITING_BET':
            min_bet, max_bet = 1, min(game.player_money, game.pot)
            game.slider_knob_rect = draw_slider(SLIDER_RECT, min_bet, max_bet, game.slider_value, game.slider_dragging)
            bet_text = render_outlined_text(f"Bet: ${game.bet_amount}", small_font, WHITE, BLACK, 2)
            screen.blit(bet_text, (BET_TEXT_POS[0] - bet_text.get_width()//2, BET_TEXT_POS[1]))

        # Buttons
        btn_w, btn_h = BTN_SIZE
        game.button_rects['higher'] = draw_button("Higher", WIDTH//2 - 220, BTN_Y, btn_w, btn_h, can_bet)
        game.button_rects['lower'] = draw_button("Lower", WIDTH//2 - 80, BTN_Y, btn_w, btn_h, can_bet)
        game.button_rects['pass'] = draw_button("Pass", WIDTH//2 + 60, BTN_Y, btn_w, btn_h, can_bet)
        
        if game.state == 'GAME_OVER':
             game.button_rects['restart'] = draw_button("Restart", WIDTH//2 + 60, BTN_Y + 60, btn_w, btn_h, True)
        
        game.button_rects['quit'] = draw_button("Quit", WIDTH//2 + 200, BTN_Y, btn_w, btn_h, True)


        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
