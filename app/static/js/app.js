document.addEventListener('DOMContentLoaded', function() {
    const inputText = document.getElementById('inputText');
    const outputText = document.getElementById('outputText');
    const htmlOutput = document.getElementById('htmlOutput');
    const outputContainer = document.getElementById('outputContainer');
    const copyBtn = document.getElementById('copyBtn');
    const clearBtn = document.getElementById('clearBtn');
    const transformBtns = document.querySelectorAll('.transform-btn');
    const notification = document.getElementById('notification');
    const toastBody = document.getElementById('toastBody');

    // Transform button click handlers
    transformBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const transformation = this.dataset.transform;
            const text = inputText.value.trim();

            if (!text) {
                showNotification('Please enter some text to transform!', 'warning');
                return;
            }

            // Add loading state
            this.disabled = true;
            this.innerHTML = '⏳ Transforming...';

            transformText(text, transformation)
                .then(result => {
                    if (transformation === 'rainbow_html') {
                        showHtmlOutput(result.transformed_text);
                    } else {
                        showTextOutput(result.transformed_text);
                    }
                    showNotification(`Text transformed using ${getTransformationName(transformation)}!`, 'success');
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Error transforming text. Please try again.', 'error');
                })
                .finally(() => {
                    // Remove loading state
                    this.disabled = false;
                    this.innerHTML = this.dataset.originalText || getButtonText(transformation);
                });
        });

        // Store original button text
        btn.dataset.originalText = btn.innerHTML;
    });

    // Clear button
    clearBtn.addEventListener('click', function() {
        inputText.value = '';
        outputText.value = '';
        htmlOutput.innerHTML = '';
        hideOutputs();
        showNotification('All fields cleared!', 'info');
    });

    // Copy button
    copyBtn.addEventListener('click', function() {
        const isHtmlMode = htmlOutput.style.display !== 'none';
        const textToCopy = isHtmlMode ? htmlOutput.innerHTML : outputText.value;

        if (navigator.clipboard) {
            navigator.clipboard.writeText(textToCopy).then(() => {
                showNotification('Text copied to clipboard!', 'success');
            }).catch(() => {
                fallbackCopy(textToCopy);
            });
        } else {
            fallbackCopy(textToCopy);
        }
    });

    async function transformText(text, transformation) {
        const response = await fetch('/transform', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                transformation: transformation
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Unknown error occurred');
        }

        return data;
    }

    function showTextOutput(text) {
        outputText.value = text;
        outputText.style.display = 'block';
        htmlOutput.style.display = 'none';
        copyBtn.style.display = 'inline-block';
    }

    function showHtmlOutput(html) {
        htmlOutput.innerHTML = html;
        htmlOutput.style.display = 'block';
        outputText.style.display = 'none';
        copyBtn.style.display = 'inline-block';
    }

    function hideOutputs() {
        copyBtn.style.display = 'none';
    }

    function fallbackCopy(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            document.execCommand('copy');
            showNotification('Text copied to clipboard!', 'success');
        } catch (err) {
            console.error('Fallback copy failed:', err);
            showNotification('Failed to copy text. Please select and copy manually.', 'error');
        }

        document.body.removeChild(textArea);
    }

    function showNotification(message, type = 'info') {
        const toast = new bootstrap.Toast(notification);
        toastBody.textContent = message;

        // Remove existing type classes
        notification.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info');

        // Add appropriate class based on type
        switch(type) {
            case 'success':
                notification.classList.add('bg-success', 'text-white');
                break;
            case 'error':
                notification.classList.add('bg-danger', 'text-white');
                break;
            case 'warning':
                notification.classList.add('bg-warning', 'text-dark');
                break;
            default:
                notification.classList.add('bg-info', 'text-white');
        }

        toast.show();
    }

    function getTransformationName(transformation) {
        const names = {
            'alternate_case': 'Alternate Case',
            'rainbow_html': 'Rainbow HTML',
            'l33t_speak': 'L33t Speak',
            'backwards': 'Backwards Text',
            'upside_down': 'Upside Down',
            'stutter': 'Stutter Effect',
            'zalgo': 'Zalgo Text',
            'morse_code': 'Morse Code',
            'binary': 'Binary',
            'rot13': 'ROT13',
            'spongebob_case': 'SpongeBob Case',
            'wave_text': 'Wave Text',
            'shizzle': 'Shizzle Speak'
        };
        return names[transformation] || transformation;
    }

    function getButtonText(transformation) {
        const texts = {
            'alternate_case': '🔄 AlTeRnAtE cAsE',
            'rainbow_html': '🌈 Rainbow HTML',
            'l33t_speak': '💾 L33t Sp34k',
            'backwards': '↩️ Backwards Text',
            'upside_down': '🙃 Upside Down',
            'stutter': '🗣️ St-St-Stutter',
            'zalgo': '👹 Z̃ãl̃g̃õ̃ T̃ẽx̃t̃',
            'morse_code': '📡 Morse Code',
            'binary': '🤖 Binary',
            'rot13': '🔐 ROT13',
            'spongebob_case': '🧽 SpOnGeBob CaSe',
            'wave_text': '🌊 ~Wave~ Text',
            'shizzle': '🎤 Shizzle Speak'
        };
        return texts[transformation] || transformation;
    }

    // Auto-resize textarea
    inputText.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });

    // Theme picker functionality
    initializeThemePicker();

    function initializeThemePicker() {
        // Create theme picker HTML
        const themePickerHTML = `
            <div class="theme-picker">
                <button class="theme-picker-toggle" title="Choose Theme" aria-label="Choose Theme">
                    🎨
                </button>
                <div class="theme-options">
                    <button class="theme-option active" data-theme="default" title="Pastel Sunset" aria-label="Pastel Sunset Theme"></button>
                    <button class="theme-option" data-theme="mint" title="Mint Fresh" aria-label="Mint Fresh Theme"></button>
                    <button class="theme-option" data-theme="lavender" title="Lavender Dreams" aria-label="Lavender Dreams Theme"></button>
                    <button class="theme-option" data-theme="peach" title="Peach Vibes" aria-label="Peach Vibes Theme"></button>
                    <button class="theme-option" data-theme="ocean" title="Ocean Breeze" aria-label="Ocean Breeze Theme"></button>
                </div>
            </div>
        `;

        // Add theme picker to body
        document.body.insertAdjacentHTML('beforeend', themePickerHTML);

        // Get theme picker elements
        const themePicker = document.querySelector('.theme-picker');
        const themeToggle = document.querySelector('.theme-picker-toggle');
        const themeOptions = document.querySelector('.theme-options');
        const themeButtons = document.querySelectorAll('.theme-option');

        // Load saved theme
        const savedTheme = localStorage.getItem('selectedTheme') || 'default';
        applyTheme(savedTheme);

        // Toggle theme options
        themeToggle.addEventListener('click', function() {
            themeOptions.classList.toggle('show');
        });

        // Close theme picker when clicking outside
        document.addEventListener('click', function(e) {
            if (!themePicker.contains(e.target)) {
                themeOptions.classList.remove('show');
            }
        });

        // Theme selection
        themeButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const theme = this.dataset.theme;
                applyTheme(theme);
                localStorage.setItem('selectedTheme', theme);
                themeOptions.classList.remove('show');
            });
        });

        // Keyboard navigation for theme picker
        themeToggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                themeOptions.classList.toggle('show');
            }
        });

        themeButtons.forEach(btn => {
            btn.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.click();
                }
            });
        });
    }

    function applyTheme(themeName) {
        // Remove existing theme classes
        document.documentElement.removeAttribute('data-theme');

        // Apply new theme
        if (themeName !== 'default') {
            document.documentElement.setAttribute('data-theme', themeName);
        }

        // Update active theme button
        document.querySelectorAll('.theme-option').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.theme === themeName) {
                btn.classList.add('active');
            }
        });
    }
});
