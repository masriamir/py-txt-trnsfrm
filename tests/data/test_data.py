# Test Data for Text Transformers
sample_texts = {
    "simple": "Hello World",
    "punctuation": "Hello, World! How are you?",
    "numbers": "Test123 with numbers456",
    "unicode": "Héllø Wørld with émojis 🌍",
    "multiline": """Line one
Line two
Line three""",
    "empty": "",
    "whitespace": "   spaces   and   tabs\t\n",
    "special_chars": "Special @#$% characters & symbols",
    "long_text": "This is a very long text that should be used for testing performance and edge cases in text transformation algorithms. "
    * 10,
    "html": "<p>HTML content with <strong>tags</strong></p>",
    "quotes": "Text with \"double quotes\" and 'single quotes'",
    "case_mixed": "MiXeD cAsE tExT FoR tEsTiNg",
}

expected_results = {
    "alternate_case": {
        "simple": "hElLo WoRlD",
        "empty": "",
        "punctuation": "hElLo, WoRlD! hOw ArE yOu?",
    },
    "backwards": {
        "simple": "dlroW olleH",
        "empty": "",
        "numbers": "654srebmun htiw 321tseT",
    },
    "rot13": {
        "simple": "Uryyb Jbeyq",
        "empty": "",
        "numbers": "Grfg123 jvgu ahzoref456",
    },
}

# Performance test data
performance_texts = {
    "small": "A" * 100,
    "medium": "B" * 1000,
    "large": "C" * 10000,
    "xlarge": "D" * 100000,
}

# Edge cases for testing
edge_cases = {
    "only_spaces": "     ",
    "only_newlines": "\n\n\n",
    "only_tabs": "\t\t\t",
    "mixed_whitespace": " \t\n \t\n",
    "single_char": "a",
    "repeated_chars": "aaaaaaa",
    "all_caps": "ALL UPPERCASE TEXT",
    "all_lower": "all lowercase text",
    "numbers_only": "1234567890",
    "symbols_only": "!@#$%^&*()",
    "unicode_emoji": "🚀🌟💫⭐🌈",
    "unicode_accents": "àáâãäåæçèéêë",
}
