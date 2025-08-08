# High-Low Poker Game

A simple and interactive High-Low poker game built with Python and Pygame. Test your luck and skill by predicting whether the next card will be higher or lower than the current one!

## Features

- **Interactive Gameplay**: Click-based controls with intuitive buttons
- **Dynamic Betting System**: Adjustable bet slider with visual feedback
- **Card Animation**: Smooth card flip animations for reveals
- **Stylish UI**: Outlined text with color-coded outcomes (blue for wins, red for losses)
- **Game Management**: Pass cards, quit, restart, and track your money/pot
- **Asset Support**: Loads card images or generates placeholders automatically

## Game Rules

1. **Starting Conditions**: You begin with $100, and there's a $50 pot
2. **Betting**: Use the slider to adjust your bet amount (minimum $1)
3. **Prediction**: Click "Higher" if you think the next card will be higher, "Lower" for lower
4. **Outcomes**:
   - **Win**: Gain your bet amount from the pot
   - **Lose**: Your bet goes to the pot
   - **Tie**: You lose double your bet amount (penalty for ties)
5. **Special Actions**:
   - **Pass**: Skip the current card and get a new one (costs your current bet)
   - **Quit**: End the game early
   - **Restart**: Start over when the game ends

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup
1. Clone or download this repository
2. Navigate to the game directory
3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
4. Install required dependencies:
   ```bash
   pip install pygame
   ```

### Optional: Card Assets
- Create an `assets` folder in the game directory
- Add card image files (PNG format) with names like:
  - `2_of_hearts.png`, `3_of_spades.png`, etc.
  - `jack_of_clubs.png`, `queen_of_diamonds.png`
  - `king_of_hearts.png`, `ace_of_spades.png`
  - `back.png` for card backs
- If assets are missing, the game will automatically generate placeholder cards

## How to Play

1. Run the game:
   ```bash
   python poker.py
   ```

2. **Set Your Bet**: Drag the slider to adjust your bet amount

3. **Make Your Choice**: 
   - Click "Higher" if you think the next card will have a higher value
   - Click "Lower" if you think it will be lower
   - Click "Pass" to skip the current card

4. **Watch the Result**: The card flips with animation and shows the outcome

5. **Continue Playing**: Click anywhere after a result to continue to the next round

6. **Game Over**: When you run out of money or the pot is empty, restart or quit

## Controls

- **Mouse**: All interactions are mouse-based
- **Slider**: Click and drag to adjust bet amount
- **Buttons**: Click to make choices (Higher/Lower/Pass/Quit/Restart)
- **Continue**: Click anywhere on screen after a round result

## Technical Details

- **Built with**: Python 3.12, Pygame 2.6.1
- **Resolution**: 800x600 pixels
- **Card Values**: 2-10, Jack(11), Queen(12), King(13), Ace(14)
- **Suits**: Hearts, Diamonds, Clubs, Spades

## File Structure

```
Game/
├── poker.py          # Main game file
├── README.md         # This file
├── assets/           # Card images (optional)
│   ├── 2_of_hearts.png
│   ├── ace_of_spades.png
│   ├── back.png
│   └── ...
└── venv/            # Virtual environment (created during setup)
```

## Screenshots

*The game features a green felt background with clearly visible cards, outlined text messages, and intuitive button controls at the bottom of the screen.*

## Contributing

Feel free to fork this project and submit pull requests for improvements. Some ideas for enhancements:
- Sound effects
- Different card themes
- Statistics tracking
- Multiple difficulty levels
- Tournament mode

## License

MIT License

Copyright (c) 2025 QuantumPixelator

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

- Card assets sourced from [playing-cards-assets](https://github.com/hayeah/playing-cards-assets)
- Built with the excellent [Pygame](https://www.pygame.org/) library
- Developed as a learning project for Python game development
