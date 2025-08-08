import pygame
import random
import sys
import os
import math

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("High-Low Poker")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)

# Fonts
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)
# Fun display font (fallback to default if unavailable)
try:
    display_font = pygame.font.SysFont('comic sans ms', 42, bold=True)
except Exception:
    display_font = pygame.font.SysFont(None, 42)

def render_outlined_text(text, font, inner_color, outline_color, outline_px=2):
    base = font.render(text, True, inner_color)
    w, h = base.get_width(), base.get_height()
    surf = pygame.Surface((w + outline_px*2, h + outline_px*2), pygame.SRCALPHA)
    # Draw outline by offsetting
    for dx in range(-outline_px, outline_px+1):
        for dy in range(-outline_px, outline_px+1):
            if dx*dx + dy*dy <= outline_px*outline_px:
                surf.blit(font.render(text, True, outline_color), (dx+outline_px, dy+outline_px))
    surf.blit(base, (outline_px, outline_px))
    return surf

def wrap_outlined_text(text, font, inner_color, outline_color, max_width, outline_px=2, line_spacing=6):
    words = text.split()
    lines = []
    current = []
    while words:
        current.append(words.pop(0))
        test = " ".join(current)
        test_surface = font.render(test, True, inner_color)
        if test_surface.get_width() > max_width:
            # remove last word and commit line
            last = current.pop()
            if current:
                line_text = " ".join(current)
                lines.append(line_text)
            current = [last]
    if current:
        lines.append(" ".join(current))
    # Render each line with outline
    rendered = [render_outlined_text(l, font, inner_color, outline_color, outline_px) for l in lines]
    total_height = sum(s.get_height() for s in rendered) + line_spacing * (len(rendered)-1)
    return rendered, total_height

# Card suits and values
SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
VALUES = list(range(2, 15))  # 2-10, J=11, Q=12, K=13, A=14
VALUE_NAMES = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}

# Helper functions
def make_deck():
    deck = [(value, suit) for suit in SUITS for value in VALUES]
    random.shuffle(deck)
    return deck

def card_name(card):
    value, suit = card
    return f"{VALUE_NAMES.get(value, str(value))} of {suit.capitalize()}"

def load_card_images():
    """Load all card images; create placeholders if files missing to avoid KeyErrors."""
    images = {}
    def placeholder(text):
        surf = pygame.Surface((80, 120))
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
                except Exception:
                    img = placeholder(f"{VALUE_NAMES.get(value, value)}\n{suit[0].upper()}")
            else:
                img = placeholder(f"{VALUE_NAMES.get(value, value)}\n{suit[0].upper()}")
            images[(value, suit)] = img
    back_path = os.path.join("assets", "back.png")
    if os.path.exists(back_path):
        try:
            images['back'] = pygame.image.load(back_path)
        except Exception:
            images['back'] = placeholder("BACK")
    else:
        images['back'] = placeholder("BACK")
    return images

card_images = load_card_images()

def draw_card(card, x, y, face_up=True, border=True):
    rect = pygame.Rect(x, y, 80, 120)
    if face_up:
        pygame.draw.rect(screen, WHITE, rect)
    if border:
        pygame.draw.rect(screen, BLACK, rect, 3)
    key = card if face_up else 'back'
    if key not in card_images:
        # Fallback placeholder if somehow missing
        surf = pygame.Surface((80, 120))
        surf.fill((200, 200, 200))
        pygame.draw.rect(surf, BLACK, surf.get_rect(), 2)
        txt = small_font.render("??", True, BLACK)
        surf.blit(txt, (surf.get_width()//2 - txt.get_width()//2, surf.get_height()//2 - txt.get_height()//2))
        img = surf
    else:
        img = card_images[key]
    img = pygame.transform.scale(img, (80, 120))
    screen.blit(img, (x, y))


def draw_deck(x, y, count):
    for i in range(min(count, 5)):
        screen.blit(pygame.transform.scale(card_images['back'], (60, 90)), (x + i*5, y - i*2))

def animate_card_flip(card, x, y, progress):
    rect = pygame.Rect(x, y, 80, 120)
    pygame.draw.rect(screen, WHITE, rect)
    pygame.draw.rect(screen, BLACK, rect, 3)
    img = card_images[card]
    img = pygame.transform.scale(img, (80, 120))
    w = int(80 * abs(progress))
    if w > 0:
        img = pygame.transform.scale(img, (w, 120))
        screen.blit(img, (x + (80-w)//2, y))


player_money = 100
pot = 50
deck = make_deck()
current_card = deck.pop()
next_card = None
message = "Adjust your bet and click Higher/Lower/Pass."
outcome_type = None  # 'win','lose','tie','pass','quit', or None
game_over = False
bet_amount = 0
animating = False
animation_progress = 0
bet_ready = False
slider_value = 1
slider_dragging = False


# Button helper
def draw_button(text, x, y, w, h, active=True):
    color = BLUE if active else (100, 100, 100)
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    txt = small_font.render(text, True, WHITE)
    screen.blit(txt, (x + (w-txt.get_width())//2, y + (h-txt.get_height())//2))
    return rect

# Slider helper
def draw_slider(x, y, w, h, min_val, max_val, value, dragging):
    # Draw bar
    pygame.draw.rect(screen, WHITE, (x, y + h//2 - 4, w, 8))
    pygame.draw.rect(screen, BLACK, (x, y + h//2 - 4, w, 8), 2)
    # Draw knob
    knob_x = x + int((value - min_val) / (max_val - min_val) * w) if max_val > min_val else x
    knob_rect = pygame.Rect(knob_x - 10, y + h//2 - 15, 20, 30)
    pygame.draw.rect(screen, RED if dragging else BLUE, knob_rect)
    pygame.draw.rect(screen, BLACK, knob_rect, 2)
    # Draw value
    val_text = small_font.render(f"${value}", True, BLACK)
    screen.blit(val_text, (x + w//2 - val_text.get_width()//2, y + h + 5))
    return knob_rect

def main(max_frames: int | None = None):
    global player_money, pot, deck, current_card, next_card, message, game_over, bet_amount, animating, animation_progress, bet_ready, slider_value, slider_dragging, outcome_type
    clock = pygame.time.Clock()
    guess = None
    wait_for_continue = False
    last_cards = (None, None)
    button_rects = {}
    slider_rect = None
    frame_count = 0
    while True:
        screen.fill(GREEN)
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
                # Click anywhere to continue to next round after result
                if not animating and last_cards[0] and last_cards[1] and wait_for_continue and not game_over:
                    if player_money <= 0 or pot <= 0:
                        game_over = True
                        message = "Game over! Press Restart or Quit."
                    else:
                        if len(deck) <= 3:
                            deck = make_deck()
                        current_card = deck.pop()
                        next_card = None
                        last_cards = (None, None)
                        bet_ready = False
                        slider_value = 1
                        message = "Adjust your bet and click a button."
                        wait_for_continue = False
                        outcome_type = None
                # Slider drag start
                if slider_rect and slider_rect.collidepoint(mouse_pos) and not animating and not game_over:
                    slider_dragging = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if slider_dragging:
                    bet_ready = True  # Bet becomes ready when user releases after drag
                slider_dragging = False
            if event.type == pygame.MOUSEMOTION and slider_dragging and not game_over:
                # Move slider while dragging
                slider_x, slider_y, slider_w, slider_h = WIDTH//2 - 150, HEIGHT//2 + 60, 300, 30
                min_val = 1
                max_val = min(player_money, pot)
                rel_x = min(max(event.pos[0] - slider_x, 0), slider_w)
                slider_value = int(min_val + (max_val - min_val) * rel_x / slider_w)
                slider_value = max(min_val, min(max_val, slider_value))

        # Draw deck
        draw_deck(50, HEIGHT//2 - 45, len(deck))
        # Draw cards side by side
        if game_over and last_cards[0] and last_cards[1]:
            draw_card(last_cards[0], WIDTH//2 - 100, HEIGHT//2 - 60, face_up=True, border=True)
            draw_card(last_cards[1], WIDTH//2 + 20, HEIGHT//2 - 60, face_up=True, border=True)
        else:
            draw_card(current_card, WIDTH//2 - 100, HEIGHT//2 - 60, face_up=True, border=True)
            if next_card:
                if animating:
                    animate_card_flip(next_card, WIDTH//2 + 20, HEIGHT//2 - 60, animation_progress)
                else:
                    draw_card(next_card, WIDTH//2 + 20, HEIGHT//2 - 60, face_up=True, border=True)
            else:
                draw_card('back', WIDTH//2 + 20, HEIGHT//2 - 60, face_up=False, border=True)

        # Animate card flip and resolve bet
        if animating and next_card:
            animation_progress += 0.1
            if animation_progress < 1:
                animate_card_flip(next_card, WIDTH//2 + 20, HEIGHT//2 - 60, animation_progress)
            else:
                value1, _ = current_card
                value2, _ = next_card
                if guess == 'higher':
                    if value2 > value1:
                        player_money += bet_amount
                        pot -= bet_amount
                        message = f"You won ${bet_amount}! {card_name(next_card)} is higher."
                        outcome_type = 'win'
                    elif value2 == value1:
                        player_money -= bet_amount * 2
                        pot += bet_amount * 2
                        message = f"Tie! You lose double: ${bet_amount*2}. ({card_name(next_card)})"
                        outcome_type = 'tie'
                    else:
                        player_money -= bet_amount
                        pot += bet_amount
                        message = f"You lost ${bet_amount}. {card_name(next_card)} is lower."
                        outcome_type = 'lose'
                else:
                    if value2 < value1:
                        player_money += bet_amount
                        pot -= bet_amount
                        message = f"You won ${bet_amount}! {card_name(next_card)} is lower."
                        outcome_type = 'win'
                    elif value2 == value1:
                        player_money -= bet_amount * 2
                        pot += bet_amount * 2
                        message = f"Tie! You lose double: ${bet_amount*2}. ({card_name(next_card)})"
                        outcome_type = 'tie'
                    else:
                        player_money -= bet_amount
                        pot += bet_amount
                        message = f"You lost ${bet_amount}. {card_name(next_card)} is higher."
                        outcome_type = 'lose'
                last_cards = (current_card, next_card)
                animating = False
                animation_progress = 0
                bet_ready = False
                bet_amount = 0
                wait_for_continue = True
                # Only set game_over after user clicks to continue

        # Draw money and pot
        money_text = small_font.render(f"Your Money: ${player_money}", True, WHITE)
        pot_text = small_font.render(f"Pot: ${pot}", True, WHITE)
        screen.blit(money_text, (10, 10))
        screen.blit(pot_text, (10, 40))

        # Draw bet slider (always available before result/game over)
        result_showing_temp = last_cards[0] and last_cards[1] and wait_for_continue and not game_over
        if not animating and not game_over and not result_showing_temp:
            min_val = 1
            max_val = min(player_money, pot)
            slider_x, slider_y, slider_w, slider_h = WIDTH//2 - 150, HEIGHT//2 + 60, 300, 30
            slider_rect = draw_slider(slider_x, slider_y, slider_w, slider_h, min_val, max_val, slider_value, slider_dragging)
            bet_amount = slider_value

        # Draw central outcome / status message above cards
        color_map = {
            'win': ((255,255,255),(0,90,220)),
            'lose': ((255,255,255),(200,0,0)),
            'tie': ((255,255,255),(180,120,0)),
            'pass': ((255,255,255),(50,120,200)),
            'quit': ((255,255,255),(120,120,120)),
            None: ((255,255,255),(0,0,0))
        }
        inner, outline = color_map.get(outcome_type, ((255,255,255),(0,0,0)))
        max_text_width = WIDTH - 60
        wrapped_surfaces, total_h = wrap_outlined_text(message, display_font, inner, outline, max_text_width, outline_px=3, line_spacing=8)
        top_y = 80  # lowered to avoid overlap with money/pot display
        current_y = top_y
        for i, surf_line in enumerate(wrapped_surfaces):
            screen.blit(surf_line, (WIDTH//2 - surf_line.get_width()//2, current_y))
            current_y += surf_line.get_height() + 8
        # Show click anywhere to continue after round
        if not animating and last_cards[0] and last_cards[1] and wait_for_continue and not game_over:
            continue_text = small_font.render("Click anywhere to continue", True, RED)
            screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 20))

        # Draw buttons
        button_rects.clear()
        btn_y = HEIGHT//2 + 120
        btn_w, btn_h = 120, 40
        result_showing = last_cards[0] and last_cards[1] and wait_for_continue and not game_over
        active = bet_ready and not animating and not game_over and not result_showing
        button_rects['higher'] = draw_button("Higher", WIDTH//2 - 220, btn_y, btn_w, btn_h, active)
        button_rects['lower'] = draw_button("Lower", WIDTH//2 - 80, btn_y, btn_w, btn_h, active)
        active_pass = bet_ready and not animating and not game_over and not result_showing
        button_rects['pass'] = draw_button("Pass", WIDTH//2 + 60, btn_y, btn_w, btn_h, active_pass)
        active_quit = not animating
        button_rects['quit'] = draw_button("Quit", WIDTH//2 + 200, btn_y, btn_w, btn_h, active_quit)
        active_restart = game_over and wait_for_continue
        button_rects['restart'] = draw_button("Restart", WIDTH//2 + 60, btn_y + 60, btn_w, btn_h, active_restart)

        # Draw bet amount near bottom for visibility
        bet_outline = render_outlined_text(f"Bet: ${bet_amount}", small_font, (255,255,255), (0,0,0), outline_px=2)
        screen.blit(bet_outline, (WIDTH//2 - bet_outline.get_width()//2, HEIGHT - 40))

        # Button logic
        if mouse_clicked:
            if not result_showing:
                for name, rect in button_rects.items():
                    if rect.collidepoint(mouse_pos):
                        if name == 'higher' and bet_ready and not animating and not game_over:
                            if len(deck) <= 3:
                                deck = make_deck()
                            next_card = deck.pop()
                            animating = True
                            animation_progress = 0
                            guess = 'higher'
                        elif name == 'lower' and bet_ready and not animating and not game_over:
                            if len(deck) <= 3:
                                deck = make_deck()
                            next_card = deck.pop()
                            animating = True
                            animation_progress = 0
                            guess = 'lower'
                        elif name == 'pass' and bet_ready and not animating and not game_over:
                            if len(deck) <= 3:
                                deck = make_deck()
                            current_card = deck.pop()
                            next_card = None
                            bet_ready = False
                            slider_value = 1
                            bet_amount = 0
                            message = "Card passed. Adjust your bet and click a button."
                            outcome_type = 'pass'
                        elif name == 'quit' and not animating:
                            game_over = True
                            wait_for_continue = True
                            message = "You quit the game. Press Restart to play again."
                            outcome_type = 'quit'
                        elif name == 'restart' and game_over and wait_for_continue:
                            player_money = 100
                            pot = 50
                            deck = make_deck()
                            current_card = deck.pop()
                            next_card = None
                            message = "Adjust your bet and click a button."
                            game_over = False
                            bet_amount = 0
                            bet_ready = False
                            animating = False
                            animation_progress = 0
                            guess = None
                            wait_for_continue = False
                            last_cards = (None, None)
                            outcome_type = None
        pygame.display.flip()
        clock.tick(60)
        if max_frames is not None:
            frame_count += 1
            if frame_count >= max_frames:
                break

if __name__ == "__main__":
    try:
        # Run a short self-test (a few frames) to ensure no immediate crash, then start full game.
        main(max_frames=5)
        main()
    except SystemExit:
        pass
    except Exception as e:
        print("Unhandled exception:", e)
    finally:
        pygame.quit()
