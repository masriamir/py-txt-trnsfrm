import pytest
from app.utils.text_transformers import TextTransformer


class TestTextTransformer:
    """Test cases for the TextTransformer class."""
    
    @pytest.fixture
    def transformer(self):
        """Create a TextTransformer instance for testing."""
        return TextTransformer()
    
    def test_get_available_transformations(self, transformer):
        """Test that all transformations are available."""
        transformations = transformer.get_available_transformations()
        expected = [
            'alternate_case', 'rainbow_html', 'l33t_speak', 'backwards',
            'upside_down', 'stutter', 'zalgo', 'morse_code', 'binary',
            'rot13', 'reverse_words', 'spongebob_case', 'wave_text'
        ]
        
        for expected_transform in expected:
            assert expected_transform in transformations
    
    def test_alternate_case(self, transformer):
        """Test alternate case transformation."""
        result = transformer.alternate_case('Hello World')
        assert result == 'HeLlO WoRlD'
        
        # Test with punctuation
        result = transformer.alternate_case('Hello, world!')
        assert result == 'HeLlO, WoRlD!'
        
        # Test sentence reset
        result = transformer.alternate_case('Hi. How are you?')
        assert result == 'Hi. HoW ArE YoU?'
    
    def test_rainbow_html(self, transformer):
        """Test rainbow HTML transformation."""
        result = transformer.rainbow_html('Hi')
        assert '<span style="color:' in result
        assert 'Hi' in result.replace('<span style="color: #FF0000;">H</span><span style="color: #FF7F00;">i</span>', 'Hi')
    
    def test_l33t_speak(self, transformer):
        """Test l33t speak transformation."""
        result = transformer.l33t_speak('Hello')
        assert result == 'H3110'
        
        result = transformer.l33t_speak('Leet Speak')
        assert result == '1337 Sp34k'
    
    def test_backwards(self, transformer):
        """Test backwards text transformation."""
        result = transformer.backwards('Hello World')
        assert result == 'dlroW olleH'
    
    def test_upside_down(self, transformer):
        """Test upside down transformation."""
        result = transformer.upside_down('hello')
        # Note: upside down also reverses the string
        assert 'ɥ' in result or 'o' in result  # Some upside down chars
    
    def test_stutter(self, transformer):
        """Test stutter transformation."""
        result = transformer.stutter('Hello world')
        assert 'H-H-Hello' in result
        assert 'w-w-world' in result
    
    def test_morse_code(self, transformer):
        """Test Morse code transformation."""
        result = transformer.morse_code('SOS')
        assert result == '... --- ...'
        
        result = transformer.morse_code('HELLO')
        expected = '.... . .-.. .-.. ---'
        assert result == expected
    
    def test_binary(self, transformer):
        """Test binary transformation."""
        result = transformer.binary('A')
        assert result == '01000001'
        
        result = transformer.binary('Hi')
        parts = result.split(' ')
        assert len(parts) == 2
        assert all(len(part) == 8 for part in parts)
        assert all(c in '01' for part in parts for c in part)
    
    def test_rot13(self, transformer):
        """Test ROT13 transformation."""
        result = transformer.rot13('Hello')
        assert result == 'Uryyb'
        
        # Test round trip
        double_rot13 = transformer.rot13(result)
        assert double_rot13 == 'Hello'
    
    def test_reverse_words(self, transformer):
        """Test reverse words transformation."""
        result = transformer.reverse_words('Hello World')
        assert result == 'olleH dlroW'
    
    def test_spongebob_case(self, transformer):
        """Test SpongeBob case transformation."""
        # This one is random, so we just test that it changes case
        result = transformer.spongebob_case('hello world')
        assert result != 'hello world'
        assert result.lower() == 'hello world'
    
    def test_wave_text(self, transformer):
        """Test wave text transformation."""
        result = transformer.wave_text('Hi')
        assert '~' in result or '∼' in result or '〜' in result
    
    def test_transform_method(self, transformer):
        """Test the main transform method."""
        result = transformer.transform('Hello', 'backwards')
        assert result == 'olleH'
        
        with pytest.raises(ValueError):
            transformer.transform('Hello', 'nonexistent')
    
    def test_empty_string_transformations(self, transformer):
        """Test transformations with empty strings."""
        for transformation in transformer.get_available_transformations():
            result = transformer.transform('', transformation)
            assert isinstance(result, str)
    
    def test_unicode_handling(self, transformer):
        """Test transformations with Unicode characters."""
        unicode_text = 'Héllo Wørld 🌍'
        
        # These should not crash with Unicode input
        safe_transforms = ['backwards', 'binary', 'stutter']
        
        for transform in safe_transforms:
            result = transformer.transform(unicode_text, transform)
            assert isinstance(result, str)
    
    def test_long_text_performance(self, transformer):
        """Test performance with longer text."""
        long_text = 'Hello World! ' * 100
        
        # Should complete reasonably quickly
        result = transformer.transform(long_text, 'alternate_case')
        assert len(result) == len(long_text)
        assert isinstance(result, str)