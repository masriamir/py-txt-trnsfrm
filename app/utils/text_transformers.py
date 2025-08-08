import random
from collections.abc import Callable

from app.logging_config import get_logger

logger = get_logger(__name__)


class TextTransformer:
    """Text transformation utilities inspired by 90s internet culture."""

    def __init__(self):
        logger.debug("Initializing TextTransformer with available transformations")
        self.transformations: dict[str, Callable[[str], str]] = {
            'alternate_case': self.alternate_case,
            'rainbow_html': self.rainbow_html,
            'l33t_speak': self.l33t_speak,
            'backwards': self.backwards,
            'upside_down': self.upside_down,
            'stutter': self.stutter,
            'zalgo': self.zalgo_light,
            'morse_code': self.morse_code,
            'binary': self.binary,
            'rot13': self.rot13,
            'reverse_words': self.reverse_words,
            'spongebob_case': self.spongebob_case,
            'wave_text': self.wave_text,
        }
        logger.debug(f"TextTransformer initialized with {len(self.transformations)} transformations")

    def transform(self, text: str, transformation: str) -> str:
        """Apply the specified transformation to the text."""
        if transformation not in self.transformations:
            logger.error(f"Unknown transformation requested: '{transformation}'. Available: {list(self.transformations.keys())}")
            raise ValueError(f"Unknown transformation: {transformation}")

        logger.debug(f"Applying transformation '{transformation}' to text of length {len(text)}")
        try:
            result = self.transformations[transformation](text)
            logger.debug(f"Transformation '{transformation}' successful, result length: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"Error during '{transformation}' transformation: {str(e)}")
            raise

    def get_available_transformations(self) -> list[str]:
        """Get list of available transformations."""
        transformations = list(self.transformations.keys())
        logger.debug(f"Returning {len(transformations)} available transformations")
        return transformations

    def alternate_case(self, text: str) -> str:
        """Alternate case for each letter while maintaining sentence structure."""
        result = []
        uppercase = True

        for char in text:
            if char.isalpha():
                if uppercase:
                    result.append(char.upper())
                else:
                    result.append(char.lower())
                uppercase = not uppercase
            else:
                result.append(char)
                if char in '.!?':
                    uppercase = True

        return ''.join(result)

    def rainbow_html(self, text: str) -> str:
        """Generate HTML with rainbow colored text."""
        colors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#9400D3']
        result = []
        color_index = 0

        for char in text:
            if char.strip():  # Only color non-whitespace characters
                color = colors[color_index % len(colors)]
                result.append(f'<span style="color: {color};">{char}</span>')
                color_index += 1
            else:
                result.append(char)

        return ''.join(result)

    def l33t_speak(self, text: str) -> str:
        """Convert text to l33t sp34k."""
        leet_map = {
            'a': '4', 'A': '4',
            'e': '3', 'E': '3',
            'i': '1', 'I': '1',
            'l': '1', 'L': '1',
            'o': '0', 'O': '0',
            's': '5', 'S': '5',
            't': '7', 'T': '7',
            'g': '9', 'G': '9',
            'b': '6', 'B': '6',
        }

        result = []
        for char in text:
            result.append(leet_map.get(char, char))

        return ''.join(result)

    def backwards(self, text: str) -> str:
        """Reverse the entire text."""
        return text[::-1]

    def upside_down(self, text: str) -> str:
        """Convert text to upside down unicode characters."""
        upside_down_map = {
            'a': 'ɐ', 'b': 'q', 'c': 'ɔ', 'd': 'p', 'e': 'ǝ',
            'f': 'ɟ', 'g': 'ƃ', 'h': 'ɥ', 'i': 'ᴉ', 'j': 'ɾ',
            'k': 'ʞ', 'l': 'l', 'm': 'ɯ', 'n': 'u', 'o': 'o',
            'p': 'd', 'q': 'b', 'r': 'ɹ', 's': 's', 't': 'ʇ',
            'u': 'n', 'v': 'ʌ', 'w': 'ʍ', 'x': 'x', 'y': 'ʎ',
            'z': 'z', '?': '¿', '!': '¡', '.': '˙', ',': "'",
            ' ': ' '
        }

        result = []
        for char in text.lower():
            result.append(upside_down_map.get(char, char))

        return ''.join(result)[::-1]

    def stutter(self, text: str) -> str:
        """Add st-st-stutter effect to words."""
        words = text.split()
        result = []

        for word in words:
            if len(word) > 2 and word.isalpha():
                first_char = word[0]
                stuttered = f"{first_char}-{first_char}-{word}"
                result.append(stuttered)
            else:
                result.append(word)

        return ' '.join(result)

    def zalgo_light(self, text: str) -> str:
        """Add light zalgo effect (combining diacritical marks)."""
        combining_chars = ['̀', '́', '̂', '̃', '̄', '̅', '̆', '̇', '̈', '̉', '̊', '̋', '̌', '̍']
        result = []

        for char in text:
            result.append(char)
            if char.isalpha() and random.random() < 0.3:
                result.append(random.choice(combining_chars))

        return ''.join(result)

    def morse_code(self, text: str) -> str:
        """Convert text to Morse code."""
        morse_map = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
            '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
            '8': '---..', '9': '----.', ' ': '/'
        }

        result = []
        for char in text.upper():
            if char in morse_map:
                result.append(morse_map[char])
            elif char == ' ':
                result.append('/')

        return ' '.join(result)

    def binary(self, text: str) -> str:
        """Convert text to binary."""
        return ' '.join(format(ord(char), '08b') for char in text)

    def rot13(self, text: str) -> str:
        """Apply ROT13 encoding."""
        result = []
        for char in text:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)

    def reverse_words(self, text: str) -> str:
        """Reverse each word individually."""
        return ' '.join(word[::-1] for word in text.split())

    def spongebob_case(self, text: str) -> str:
        """Alternate between uppercase and lowercase randomly (SpongeBob mocking case)."""
        result = []
        for char in text:
            if char.isalpha():
                result.append(char.upper() if random.random() < 0.5 else char.lower())
            else:
                result.append(char)
        return ''.join(result)

    def wave_text(self, text: str) -> str:
        """Create wave effect with Unicode characters."""
        wave_chars = ['~', '∼', '〜', '～', '˜']
        result = []
        wave_index = 0

        for i, char in enumerate(text):
            if char == ' ':
                result.append(' ')
            else:
                wave_char = wave_chars[wave_index % len(wave_chars)]
                if i % 2 == 0:
                    result.append(f"{wave_char}{char}{wave_char}")
                else:
                    result.append(char)
                wave_index += 1

        return ''.join(result)
