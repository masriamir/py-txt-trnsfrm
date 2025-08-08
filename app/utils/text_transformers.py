"""Text transformation utilities module.

This module provides a comprehensive collection of text transformation utilities
inspired by 90s internet culture and modern text effects. It includes various
transformations such as leet speak, case alternation, encoding methods, and
visual text effects.
"""
import random
from collections.abc import Callable

from app.logging_config import get_logger

logger = get_logger(__name__)


class TextTransformer:
    """Text transformation utilities inspired by 90s internet culture.

    This class provides a collection of text transformation methods that can
    convert input text into various formats including leet speak, alternating
    case, visual effects, encoding formats, and other nostalgic internet styles.

    Attributes:
        transformations: Dictionary mapping transformation names to their
            corresponding methods.

    Example:
        >>> transformer = TextTransformer()
        >>> result = transformer.transform("Hello World", "l33t_speak")
        >>> print(result)  # "H3110 W0r1d"
    """

    def __init__(self):
        """Initialize the TextTransformer with available transformations.

        Sets up the internal dictionary of available transformations and
        logs the initialization process for debugging purposes.
        """
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
            'shizzle': self.shizzle,
        }
        logger.debug(f"TextTransformer initialized with {len(self.transformations)} transformations")

    def transform(self, text: str, transformation: str) -> str:
        """Apply the specified transformation to the input text.

        Args:
            text: The input text to transform.
            transformation: The name of the transformation to apply.

        Returns:
            str: The transformed text.

        Raises:
            ValueError: If the transformation name is not recognized.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.transform("Hello", "backwards")
            >>> print(result)  # "olleH"
        """
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
        """Get a list of all available transformation names.

        Returns:
            list[str]: List of available transformation names.

        Example:
            >>> transformer = TextTransformer()
            >>> transformations = transformer.get_available_transformations()
            >>> print("l33t_speak" in transformations)  # True
        """
        transformations = list(self.transformations.keys())
        logger.debug(f"Returning {len(transformations)} available transformations")
        return transformations

    def alternate_case(self, text: str) -> str:
        """Convert text to alternating uppercase and lowercase letters.

        Alternates the case of each alphabetic character while maintaining
        sentence structure. Resets to uppercase after sentence-ending punctuation.

        Args:
            text: Input text to transform.

        Returns:
            str: Text with alternating case applied.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.alternate_case("hello world")
            >>> print(result)  # "HeLlO WoRlD"
        """
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
        """Generate HTML with rainbow-colored text using inline styles.

        Applies rainbow colors (red, orange, yellow, green, blue, indigo, violet)
        to each non-whitespace character using HTML span elements with inline styles.

        Args:
            text: Input text to colorize.

        Returns:
            str: HTML string with rainbow-colored text.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.rainbow_html("Hello")
            >>> # Returns HTML with each letter in different rainbow colors
        """
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
        """Convert text to leet speak (1337 speak) format.

        Replaces certain letters with numbers and symbols according to
        classic leet speak conventions popular in 90s internet culture.

        Args:
            text: Input text to convert to leet speak.

        Returns:
            str: Text converted to leet speak format.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.l33t_speak("elite hacker")
            >>> print(result)  # "311t3 h4ck3r"
        """
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
        """Reverse the entire text string.

        Args:
            text: Input text to reverse.

        Returns:
            str: The input text reversed character by character.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.backwards("Hello World")
            >>> print(result)  # "dlroW olleH"
        """
        return text[::-1]

    def upside_down(self, text: str) -> str:
        """Convert text to upside-down Unicode characters.

        Uses Unicode characters that appear upside-down when displayed,
        then reverses the entire string to simulate flipped text.

        Args:
            text: Input text to flip upside-down.

        Returns:
            str: Text using upside-down Unicode characters, reversed.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.upside_down("hello")
            >>> # Returns upside-down Unicode equivalent
        """
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
        """Add stuttering effect to words by repeating first letters.

        For alphabetic words longer than 2 characters, repeats the first
        letter with dashes to create a stuttering effect.

        Args:
            text: Input text to add stutter effect.

        Returns:
            str: Text with stuttering effect applied to words.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.stutter("hello world")
            >>> print(result)  # "h-h-hello w-w-world"
        """
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
        """Add light zalgo effect using combining diacritical marks.

        Randomly adds Unicode combining diacritical marks to create
        a "corrupted" or "glitchy" text effect reminiscent of zalgo text.

        Args:
            text: Input text to apply zalgo effect.

        Returns:
            str: Text with light zalgo effect applied.

        Note:
            This is a "light" version that adds fewer combining characters
            for better readability compared to full zalgo text.
        """
        combining_chars = ['̀', '́', '̂', '̃', '̄', '̅', '̆', '̇', '̈', '̉', '̊', '̋', '̌', '̍']
        result = []

        for char in text:
            result.append(char)
            if char.isalpha() and random.random() < 0.3:
                result.append(random.choice(combining_chars))

        return ''.join(result)

    def morse_code(self, text: str) -> str:
        """Convert text to Morse code representation.

        Converts alphabetic characters and digits to their Morse code
        equivalents using dots and dashes. Spaces are represented as '/'.

        Args:
            text: Input text to convert to Morse code.

        Returns:
            str: Morse code representation of the input text.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.morse_code("SOS")
            >>> print(result)  # "... --- ..."
        """
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
        """Convert text to binary representation.

        Converts each character to its 8-bit binary representation,
        separated by spaces.

        Args:
            text: Input text to convert to binary.

        Returns:
            str: Binary representation of the input text.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.binary("Hi")
            >>> print(result)  # "01001000 01101001"
        """
        return ' '.join(format(ord(char), '08b') for char in text)

    def rot13(self, text: str) -> str:
        """Apply ROT13 encoding to the text.

        ROT13 is a simple letter substitution cipher that replaces each
        letter with the letter 13 positions after it in the alphabet.

        Args:
            text: Input text to encode with ROT13.

        Returns:
            str: ROT13 encoded text.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.rot13("hello")
            >>> print(result)  # "uryyb"
        """
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
        """Reverse each word individually while maintaining word order.

        Args:
            text: Input text with words to reverse.

        Returns:
            str: Text with each word reversed but in original order.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.reverse_words("hello world")
            >>> print(result)  # "olleh dlrow"
        """
        return ' '.join(word[::-1] for word in text.split())

    def spongebob_case(self, text: str) -> str:
        """Apply random alternating case (SpongeBob mocking meme style).

        Randomly alternates between uppercase and lowercase for each
        alphabetic character, creating the effect popularized by the
        "Mocking SpongeBob" meme.

        Args:
            text: Input text to apply random case alternation.

        Returns:
            str: Text with randomly alternating case.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.spongebob_case("hello world")
            >>> # Returns something like "hElLo WoRLd" (random each time)
        """
        result = []
        for char in text:
            if char.isalpha():
                result.append(char.upper() if random.random() < 0.5 else char.lower())
            else:
                result.append(char)
        return ''.join(result)

    def wave_text(self, text: str) -> str:
        """Create wave effect using Unicode wave characters.

        Decorates text with various Unicode wave characters to create
        a visual wave effect around the letters.

        Args:
            text: Input text to apply wave effect.

        Returns:
            str: Text decorated with wave characters.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.wave_text("hello")
            >>> # Returns text decorated with wave characters
        """
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

    def shizzle(self, text: str) -> str:
        """Transform text to a 'shizzle' style (izzle speak).

        Adds the suffix 'izzle' to words, popularized by 90s hip-hop culture
        and Snoop Dogg. Handles words with leading/trailing punctuation by preserving
        the punctuation and only transforming the alphabetic portions.

        Args:
            text: Input text to transform to shizzle style.

        Returns:
            str: Text with 'shizzle' style applied.

        Example:
            >>> transformer = TextTransformer()
            >>> result = transformer.shizzle("hello world!")
            >>> print(result)  # "helloizzle worldizzle!"
        """
        import re

        # Handle empty or whitespace-only strings
        if not text or text.isspace():
            return text

        def transform_word(word):
            # Extract leading non-alphabetic, alphabetic part, and trailing non-alphabetic
            match = re.match(r'^([^a-zA-Z]*)([a-zA-Z]+)([^a-zA-Z]*)$', word)
            if match:
                leading_punct = match.group(1)
                alphabetic_part = match.group(2)
                trailing_punct = match.group(3)
                return leading_punct + alphabetic_part + 'izzle' + trailing_punct
            else:
                # If no alphabetic characters found, return unchanged
                return word

        words = text.split()
        result = []

        for word in words:
            if word:  # Skip empty words
                result.append(transform_word(word))
            else:
                result.append(word)

        return ' '.join(result)
