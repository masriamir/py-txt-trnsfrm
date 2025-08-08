"""Text transformer unit tests module.

This module contains comprehensive unit tests for the TextTransformer class,
testing all available text transformation methods to ensure correct behavior
and output formatting for various input scenarios.
"""
import pytest

from app.utils.text_transformers import TextTransformer


class TestTextTransformer:
    """Test suite for the TextTransformer class.

    This class contains unit tests for all text transformation methods,
    including edge cases, error handling, and output validation.
    """

    @pytest.fixture
    def transformer(self):
        """Create a TextTransformer instance for testing.

        Returns:
            TextTransformer: Fresh instance for each test.
        """
        return TextTransformer()

    def test_get_available_transformations(self, transformer):
        """Test that all expected transformations are available.

        Verifies that the transformer exposes all implemented transformation
        methods and that the list is complete and accurate.

        Args:
            transformer: TextTransformer fixture.
        """
        transformations = transformer.get_available_transformations()
        expected = [
            'alternate_case', 'rainbow_html', 'l33t_speak', 'backwards',
            'upside_down', 'stutter', 'zalgo', 'morse_code', 'binary',
            'rot13', 'reverse_words', 'spongebob_case', 'wave_text'
        ]

        for expected_transform in expected:
            assert expected_transform in transformations

    def test_alternate_case(self, transformer):
        """Test alternate case transformation with various inputs.

        Tests the alternating case transformation with different scenarios
        including punctuation handling and sentence boundary detection.

        Args:
            transformer: TextTransformer fixture.
        """
        result = transformer.alternate_case('Hello World')
        assert result == 'HeLlO WoRlD'

        # Test with punctuation
        result = transformer.alternate_case('Hello, world!')
        assert result == 'HeLlO, WoRlD!'

        # Test sentence reset
        result = transformer.alternate_case('Hi. How are you?')
        assert result == 'Hi. HoW ArE YoU?'

    def test_rainbow_html(self, transformer):
        """Test rainbow HTML transformation output format.

        Verifies that the rainbow HTML transformation generates proper
        HTML markup with color styling for each character.

        Args:
            transformer: TextTransformer fixture.
        """
        result = transformer.rainbow_html('Hi')
        assert '<span style="color:' in result
        assert 'Hi' in result.replace('<span style="color: #FF0000;">H</span><span style="color: #FF7F00;">i</span>', 'Hi')

    def test_l33t_speak(self, transformer):
        """Test leet speak transformation accuracy.

        Verifies that letters are correctly replaced with leet speak
        equivalents according to the defined character mappings.

        Args:
            transformer: TextTransformer fixture.
        """
        result = transformer.l33t_speak('Hello')
        assert result == 'H3110'

        result = transformer.l33t_speak('Leet Speak')
        assert result == '1337 Sp34k'

    def test_backwards(self, transformer):
        """Test backwards text transformation.

        Verifies that text is correctly reversed character by character.

        Args:
            transformer: TextTransformer fixture.
        """
        result = transformer.backwards('Hello')
        assert result == 'olleH'

        result = transformer.backwards('Hello World')
        assert result == 'dlroW olleH'

    def test_upside_down(self, transformer):
        """Test upside-down Unicode transformation.

        Verifies that text is converted to upside-down Unicode characters
        and properly reversed.

        Args:
            transformer: TextTransformer fixture.
        """
        result = transformer.upside_down('hello')
        # Should contain upside-down characters
        assert len(result) == 5
        assert result != 'hello'

    def test_stutter(self, transformer):
        """Test stuttering effect transformation.

        Verifies that words receive proper stuttering treatment
        with first letter repetition.

        Args:
            transformer: TextTransformer fixture.
        """
        result = transformer.stutter('hello world')
        assert 'h-h-hello' in result
        assert 'w-w-world' in result

        # Short words should not stutter
        result = transformer.stutter('hi ok')
        assert result == 'hi ok'

    def test_morse_code(self, transformer):
        """Test Morse code transformation accuracy.

        Verifies that text is correctly converted to Morse code
        using proper dot and dash patterns.

        Args:
            transformer: TextTransformer fixture.
        """
        result = transformer.morse_code('SOS')
        assert result == '... --- ...'

        result = transformer.morse_code('HELLO')
        assert '....' in result  # H
        assert '.' in result     # E
        assert '.-..' in result  # L

    def test_binary(self, transformer):
        """Test binary conversion transformation.

        Verifies that characters are correctly converted to their
        8-bit binary representations.

        Args:
            transformer: TextTransformer fixture.
        """
        result = transformer.binary('A')
        assert result == '01000001'

        result = transformer.binary('Hi')
        parts = result.split(' ')
        assert len(parts) == 2
        assert all(len(part) == 8 for part in parts)

    def test_rot13(self, transformer):
        """Test ROT13 encoding transformation.

        Verifies that letters are correctly shifted by 13 positions
        in the alphabet while preserving case and non-alphabetic characters.

        Args:
            transformer: TextTransformer fixture.
        """
        result = transformer.rot13('hello')
        assert result == 'uryyb'

        # ROT13 should be reversible
        double_rot = transformer.rot13(result)
        assert double_rot == 'hello'

    def test_reverse_words(self, transformer):
        """Test individual word reversal transformation.

        Verifies that each word is reversed individually while
        maintaining word order and spacing.

        Args:
            transformer: TextTransformer fixture.
        """
        result = transformer.reverse_words('hello world')
        assert result == 'olleh dlrow'

    def test_transform_method(self, transformer):
        """Test the main transform method with valid and invalid inputs.

        Verifies that the transform method correctly routes to specific
        transformation methods and handles errors appropriately.

        Args:
            transformer: TextTransformer fixture.
        """
        # Test valid transformation
        result = transformer.transform('Hello', 'backwards')
        assert result == 'olleH'

        # Test invalid transformation
        with pytest.raises(ValueError) as exc_info:
            transformer.transform('Hello', 'invalid_transform')
        assert 'Unknown transformation' in str(exc_info.value)

    def test_empty_text_handling(self, transformer):
        """Test transformation behavior with empty input.

        Verifies that all transformations handle empty strings gracefully.

        Args:
            transformer: TextTransformer fixture.
        """
        for transform_name in transformer.get_available_transformations():
            result = transformer.transform('', transform_name)
            assert isinstance(result, str)  # Should return string, even if empty
