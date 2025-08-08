import pygame
import random
import os
from math import sin
from enum import Enum
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CARD_WIDTH, CARD_HEIGHT = 80, 120
DECK_CARD_WIDTH, DECK_CARD_HEIGHT = 60, 90
BUTTON_WIDTH, BUTTON_HEIGHT = 120, 40
SLIDER_WIDTH, SLIDER_HEIGHT = 300, 30
SLIDER_MIN_VALUE = 1
OUTLINE_PX = 2
LINE_SPACING = 6
CLICK_COOLDOWN = 0.2  # seconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)

# Fonts
font = pygame.font.SysFont('arial', 48)
small_font = pygame.font.SysFont('arial', 32)
try:
    display_font = pygame.font.SysFont('comic sans ms', 42, bold=True)
except Exception:
    display_font = pygame.font.SysFont('arial', 42, bold=True)

# Card suits and values
SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
VALUES = list(range(2, 15))  # 2-10, J=11, Q=12, K=13, A=14
VALUE_NAMES = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}

# Outcome types
class OutcomeType(Enum):
    WIN = 'win'
    LOSE = 'lose'
    TIE = 'tie'
    PASS = 'pass'
    QUIT = 'quit'
    NONE = None

# Game state class
class GameState:
    def __init__(self):
        self.player_money = 100
        self.pot = 50
        self.deck = make_deck()
        self.current_card = self.deck.pop()
        self.next_card = None
        self.message = "Adjust your bet and click Higher/Lower/Pass."
        self.outcome_type = OutcomeType.NONE
        self.game_over = False
        self.bet_amount = 0
        self.animating = False
        self.animation_progress = 0
        self.bet_ready = False
        self.slider_value = SLIDER_MIN_VALUE
        self.slider_dragging = False
        self.guess = None
        self.wait_for_continue = False
        self.last_cards = (None, None)
        self.last_click_time = 0

# Cache for rendered text
text_cache = {}

def render_outlined_text(text, font, inner_color, outline_color, outline_px=OUTLINE_PX):
    """Render text with an outline."""
    cache_key = (text, font.get_name(), inner_color, outline_color, outline_px)
    if cache_key not in text_cache:
        base = font.render(text, True, inner_color)
        w, h = base.get_width(), base.get_height()
        surf = pygame.Surface((w + outline_px*2, h + outline_px*2), pygame.SRCALPHA)
        for dx in range(-outline_px, outline_px+1):
            for dy in range(-outline_px, outline_px+1):
                if dx*dx + dy*dy <= outline_px*outline_px:
                    surf.blit(fontThe
        surf.blit(base, (outline_px, outline_px))
        text_cache[cache_key] = surf
    return text_cache[cache_key]

def wrap_outlined_text(text, font, inner_color, outline_color, max_width, outline_px=OUTLINE_PX, line_spacing=LINE_SPACING):
    """Wrap text to fit within max_width and render with outline."""
    words = text.split()
    lines = []
    current = []
    while words:
        current.append(words.pop(0))
        test = " ".join(current)
        test_surface = font.render(test, True, inner_color)
        if test_surface.get_width() > max_width:
            last = current.pop()
            if current:
                lines.append(" ".join(current))
            current = [last]
    if current:
        lines.append(" ".join(current))
    rendered = [render_outlined_text(l, font, inner_color, outline_color, outline_px) for l in lines]
    total_height = sum(s.get_height() for s in rendered) + line_spacing * (len(rendered)-1)
    return rendered, total_height

def make_deck():
    """Create and shuffle a standard deck of 52 cards."""
    deck = [(value, suit) for suit in SUITS for value in VALUES]
    random.shuffle(deck)
    return deck

def card_name(card):
    """Return the display name of a card (e.g., 'Ace of Spades')."""
    value, suit = card
    return f"{VALUE_NAMES.get(value, str(value))} of {suit.capitalize()}"

def load_card_images():
    """Load all card images; create placeholders if files missing."""
    images = {}
    if not os.path.exists("assets"):
        logger.error("'assets' directory not found. Using placeholder images.")
    def placeholder(text):
        surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        surf.fill((180, 180, 180))
        pygame.draw.rect(surf, BLACK, surf.get_rect(), 2)
        t = small_font.render(text, True, BLACK)
        surf.blit(t, (surf.get_width()//2 - t.get_width()//2, surf.get_height()//2 - t.get_height()//2))
        return surf
    for suit in SUITS:
        for value in VALUES:
            if value == 11:
                fname = f"jack_of_{suit}.png"
            elif value == 12:
                fname = f"queen_of_{suit}.png"
            elif value == 13:
                fname = f"king_of_{suit}.png"
            elif value == 14:
                fname = f"ace_of_{suit}.png"
            else:
                fname = f"{value}_of_{suit}.png"
            path = os.path.join("assets", fname)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path)
                except Exception as e:
                    logger.error(f"Failed to load {fname}: {e}. Using placeholder.")
                    img = placeholder(f"{VALUE_NAMES.get(value, value)}\n{suit[0].upper()}")
            else:
                img = placeholder(f"{VALUE_NAMES.get(value, value)}\n{suit[0].upper()}")
            images[(value, suit)] = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
    back_path = os.path.join("assets", "back.png")
    if os.path.exists(back_path):
        try:
            back_img = pygame.image.load(back_path)
            images['back'] = pygame.transform.scale(back_img, (CARD_WIDTH, CARD_HEIGHT))
            images['deck_back'] = pygame.transform.scale(back_img, (DECK_CARD_WIDTH, DECK_CARD_HEIGHT))
        except Exception as e:
            logger.error(f"Failed to load back.png: {e}. Using placeholder.")
            images['back'] = placeholder("BACK")
            images['deck_back'] = pygame.transform.scale(images['back'], (DECK_CARD_WIDTH, DECK_CARD_HEIGHT))
    else:
        images['back'] = placeholder("BACK")
        images['deck_back'] = pygame.transform.scale(images['back'], (DECK_CARD_WIDTH, DECK_CARD_HEIGHT))
    return images

card_images = load_card_images()

def draw_card(card, x, y, face_up=True, border=True):
    """Draw a card at position (x, y)."""
    rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    if face_up:
        pygame.draw.rect(screen, WHITE, rect)
    if border:
        pygame.draw.rect(screen, BLACK, rect, 3)
    key = card if face_up else 'back'
    if key not in card_images:
        logger.warning(f"Image not found for {key}. Using placeholder.")
        surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        surf.fill((200, 200, 200))
        pygame.draw.rect(surf, BLACK, surf.get_rect(), 2)
        txt = small_font.render("??", True, BLACK)
        surf.blit(txt, (surf.get_width()//2 - txt.get_width()//2, surf.get_height()//2 - txt.get_height()//2))
    else:
        surf = card_images[key]
    screen.blit(surf, (x, y))

def draw_deck(x, y, count):
    """Draw a stack of card backs to represent the deck."""
    for i in range(min(count, 5)):
        screen.blit(card_images['deck_back'], (x + i*5, y - i*2))

def animate_card_flip(card, x, y, progress):
    """Animate a card flip effect."""
    rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    pygame.draw.rect(screen, WHITE, rect)
    pygame.draw.rect(screen, BLACK, rect, 3)
    img = card_images[card]
    w = int(CARD_WIDTH * abs(progress))
    if w > 0:
        img = pygame.transform.scale(img, (w, CARD_HEIGHT))
        screen.blit(img, (x + (CARD_WIDTH-w)//2, y))

def draw_button(text, x, y, w, h, active=True):
    """Draw a button with the specified text."""
    color = BLUE if active else (100, 100, 100)
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    txt = small_font.render(text, True, WHITE)
    screen.blit(txt, (x + (w-txt.get_width())//2, y + (h-txt.get_height())//2))
    return rect

def draw_slider(x, y, w, h, min_val, max_val, value, dragging):
    """Draw a slider for bet amount selection."""
    pygame.draw.rect(screen, WHITE, (x, y + h//2 - 4, w, 8))
    pygame.draw.rect(screen, BLACK, (x, y + h//2 - 4, w, 8), 2)
    knob_x = x + int((value - min_val) / (max_val - min_val) * w) if max_val > min_val else x
    knob_rect = pygame.Rect(knob_x - 10, y + h//2 - 15, 20, 30)
    pygame.draw.rect(screen, RED if dragging else BLUE, knob_rect)
    pygame.draw.rect(screen, BLACK, knob_rect, 2)
    val_text = small_font.render(f"${value}", True, BLACK)
    screen.blit(val_text, (x + w//2 - val_text.get_width()//2, y + h + 5))
    return knob_rect

def draw_card_from_deck(state):
    """Draw a card from the deck, reshuffling if necessary."""
    if len(state.deck) <= 3:
        state.deck[:] = make_deck()
        logger.debug("Deck reshuffled.")
    return state.deck.pop()

def handle_button_click(name, state, current_time):
    """Handle button click events and update game state."""
    if current_time - state.last_click_time < CLICK_COOLDOWN:
        return
    state.last_click_time = current_time
    logger.debug(f"Button clicked: {name}")
    if name == 'higher' and state.bet_ready and not state.animating and not state.game_over:
        state.next_card = draw_card_from_deck(state)
        state.animating = True
        state.animation_progress = 0
        state.guess = 'higher'
        logger.debug(f"Guess: higher, next card: {card_name(state.next_card)}")
    elif name == 'lower' and state.bet_ready and not state.animating and not state.game_over:
        state.next_card = draw_card_from_deck(state)
        state.animating = True
        state.animation_progress = 0
        state.guess = 'lower'
        logger.debug(f"Guess: lower, next card: {card_name(state.next_card)}")
    elif name == 'pass' and state.bet_ready and not state.animating and not state.game_over:
        state.current_card = draw_card_from_deck(state)
        state.next_card = None
        state.bet_ready = False
        state.slider_value = SLIDER_MIN_VALUE
        state.bet_amount = 0
        state.message = "Card passed. Adjust your bet and click a button."
        state.outcome_type = OutcomeType.PASS
        logger.debug(f"Player passed. New card: {card_name(state.current_card)}")
    elif name == 'quit' and not state.animating:
        state.game_over = True
        state.wait_for_continue = True
        state.message = "You quit the game. Press Restart to play again."
        state.outcome_type = OutcomeType.QUIT
        logger.debug("Game quit")
    elif name == 'restart' and state.game_over and state.wait_for_continue:
        state.player_money = 100
        state.pot = 50
        state.deck = make_deck()
        state.current_card = draw_card_from_deck(state)
        state.next_card = None
        state.message = "Adjust your bet and click a button."
        state.outcome_type = OutcomeType.NONE
        state.game_over = False
        state.bet_amount = 0
        state.bet_ready = False
        state.animating = False
        state.animation_progress = 0
        state.slider_value = SLIDER_MIN_VALUE
        state.slider_dragging = False
        state.guess = None
        state.wait_for_continue = False
        state.last_cards = (None, None)
        logger.debug("Game restarted")

def handle_events(state, button_rects, slider_rect, mouse_pos, mouse_clicked, current_time):
    """Handle Pygame events and update game state."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            logger.debug("Pygame quit event received")
            pygame.quit()
            raise SystemExit
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_time - state.last_click_time >= CLICK_COOLDOWN:
                mouse_clicked = True
                if slider_rect and slider_rect.collidepoint(mouse_pos) and not state.animating and not state.game_over:
                    state.slider_dragging = True
                    logger.debug("Slider drag started")
                if not state.animating and state.last_cards[0] and state.last_cards[1] and state.wait_for_continue and not state.game_over:
                    if state.player_money <= 0 or state.pot <= 0:
                        state.game_over = True
                        state.message = "Game over! Press Restart or Quit."
                        state.outcome_type = OutcomeType.QUIT
                        logger.debug("Game over due to insufficient funds")
                    else:
                        state.current_card = draw_card_from_deck(state)
                        state.next_card = None
                        state.last_cards = (None, None)
                        state.bet_ready = False
                        state.slider_value = SLIDER_MIN_VALUE
                        state.message = "Adjust your bet and click a button."
                        state.wait_for_continue = False
                        state.outcome_type = OutcomeType.NONE
                        logger.debug("New round started")
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if state.slider_dragging:
                state.bet_ready = True
                logger.debug("Slider drag ended, bet ready")
            state.slider_dragging = False
        if event.type == pygame.MOUSEMOTION and state.slider_dragging and not state.game_over:
            slider_x, slider_y = SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 60
            min_val = SLIDER_MIN_VALUE
            max_val = min(state.player_money, state.pot)
            rel_x = min(max(event.pos[0] - slider_x, 0), SLIDER_WIDTH)
            state.slider_value = max(min_val, min(max_val, int(min_val + (max_val - min_val) * rel_x / SLIDER_WIDTH)))
            state.bet_amount = state.slider_value
            logger.debug(f"Slider moved, bet amount: ${state.bet_amount}")
        if mouse_clicked:
            for name, rect in button_rects.items():
                if rect.collidepoint(mouse_pos):
                    handle_button_click(name, state, current_time)

def render_game(state, button_rects, slider_rect):
    """Render the game state to the screen."""
    screen.fill(GREEN)
    # Draw deck
    draw_deck(50, SCREEN_HEIGHT//2 - 45, len(state.deck))
    # Draw cards
    if state.game_over and state.last_cards[0] and state.last_cards[1]:
        draw_card(state.last_cards[0], SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 60, face_up=True, border=True)
        draw_card(state.last_cards[1], SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2 - 60, face_up=True, border=True)
    else:
        draw_card(state.current_card, SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 60, face_up=True, border=True)
        if state.next_card:
            if state.animating:
                animate_card_flip(state.next_card, SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2 - 60, state.animation_progress)
            else:
                draw_card(state.next_card, SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2 - 60, face_up=True, border=True)
        else:
            draw_card('back', SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2 - 60, face_up=False, border=True)
    # Draw money and pot
    money_text = small_font.render(f"Your Money: ${state.player_money}", True, WHITE)
    pot_text = small_font.render(f"Pot: ${state.pot}", True, WHITE)
    screen.blit(money_text, (10, 10))
    screen.blit(pot_text, (10, 40))
    # Draw bet slider
    result_showing = state.last_cards[0] and state.last_cards[1] and state.wait_for_continue and not state.game_over
    if not state.animating and not state.game_over and not result_showing:
        min_val = SLIDER_MIN_VALUE
        max_val = min(state.player_money, state.pot)
        slider_rect = draw_slider(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 60, SLIDER_WIDTH, SLIDER_HEIGHT,
                                 min_val, max_val, state.slider_value, state.slider_dragging)
    # Draw outcome message
    color_map = {
        OutcomeType.WIN: ((255, 255, 255), (0, 90, 220)),
        OutcomeType.LOSE: ((255, 255, 255), (200, 0, 0)),
        OutcomeType.TIE: ((255, 255, 255), (180, 120, 0)),
        OutcomeType.PASS: ((255, 255, 255), (50, 120, 200)),
        OutcomeType.QUIT: ((255, 255, 255), (120, 120, 120)),
        OutcomeType.NONE: ((255, 255, 255), (0, 0, 0))
    }
    inner, outline = color_map[state.outcome_type]
    max_text_width = SCREEN_WIDTH - 60
    wrapped_surfaces, total_h = wrap_outlined_text(state.message, display_font, inner, outline, max_text_width, outline_px=3)
    top_y = 80
    current_y = top_y
    for surf_line in wrapped_surfaces:
        screen.blit(surf_line, (SCREEN_WIDTH//2 - surf_line.get_width()//2, current_y))
        current_y += surf_line.get_height() + LINE_SPACING
    # Draw continue prompt
    if not state.animating and state.last_cards[0] and state.last_cards[1] and state.wait_for_continue and not state.game_over:
        pulse = abs(sin(pygame.time.get_ticks() / 1000 * 3)) * 0.5 + 0.5
        glow_size = int(4 + pulse * 2)
        glow_color = (int(255 * pulse), int(20 * pulse), int(147 * pulse))
        continue_surface = render_outlined_text("Click anywhere to continue", font, WHITE, glow_color, outline_px=glow_size)
        screen.blit(continue_surface, (SCREEN_WIDTH//2 - continue_surface.get_width()//2, SCREEN_HEIGHT//2 + 80))
    # Draw buttons
    btn_y = SCREEN_HEIGHT//2 + 120
    active = state.bet_ready and not state.animating and not state.game_over and not result_showing
    button_rects['higher'] = draw_button("Higher", SCREEN_WIDTH//2 - 220, btn_y, BUTTON_WIDTH, BUTTON_HEIGHT, active)
    button_rects['lower'] = draw_button("Lower", SCREEN_WIDTH//2 - 80, btn_y, BUTTON_WIDTH, BUTTON_HEIGHT, active)
    active_pass = state.bet_ready and not state.animating and not state.game_over and not result_showing
    button_rects['pass'] = draw_button("Pass", SCREEN_WIDTH//2 + 60, btn_y, BUTTON_WIDTH, BUTTON_HEIGHT, active_pass)
    active_quit = not state.animating
    button_rects['quit'] = draw_button("Quit", SCREEN_WIDTH//2 + 200, btn_y, BUTTON_WIDTH, BUTTON_HEIGHT, active_quit)
    active_restart = state.game_over and state.wait_for_continue
    button_rects['restart'] = draw_button("Restart", SCREEN_WIDTH//2 + 60, btn_y + 60, BUTTON_WIDTH, BUTTON_HEIGHT, active_restart)
    # Draw bet amount
    bet_outline = render_outlined_text(f"Bet: ${state.bet_amount}", small_font, WHITE, BLACK, outline_px=2)
    screen.blit(bet_outline, (SCREEN_WIDTH//2 - bet_outline.get_width()//2, SCREEN_HEIGHT - 40))
    return slider_rect

def update_game_state(state):
    """Update game state, including card flip animation and bet resolution."""
    if state.animating and state.next_card:
        state.animation_progress += 0.1
        if state.animation_progress >= 1:
            value1, _ = state.current_card
            value2, _ = state.next_card
            if state.guess == 'higher':
                if value2 > value1:
                    state.player_money += state.bet_amount
                    state.pot -= state.bet_amount
                    state.message = f"You won ${state.bet_amount}! {card_name(state.next_card)} is higher."
                    state.outcome_type = OutcomeType.WIN
                    logger.debug(f"Won ${state.bet_amount}: {card_name(state.next_card)} > {card_name(state.current_card)}")
                elif value2 == value1:
                    state.player_money -= state.bet_amount * 2
                    state.pot += state.bet_amount * 2
                    state.message = f"Tie! You lose double: ${state.bet_amount*2}. ({card_name(state.next_card)})"
                    state.outcome_type = OutcomeType.TIE
                    logger.debug(f"Tie, lost ${state.bet_amount*2}: {card_name(state.next_card)}")
      
