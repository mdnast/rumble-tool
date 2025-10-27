# -*- coding: utf-8 -*-
"""Fix emoji encoding issues in main_ultimate.py"""
import re

# Read file
import os
filepath = os.path.join(os.path.dirname(__file__), 'main.py')
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Emoji replacements
replacements = {
    '🚀': '[INIT]',
    '🧬': '[UA]',
    '👻': '[HEADLESS]',
    '✅': '[OK]',
    '🌐': '[VIEWPORT]',
    '❌': '[FAIL]',
    '🧪': '[TEST]',
    '🌐': '[NAV]',
    '📸': '[SCREENSHOT]',
    '🔍': '[CAPTCHA CHECK]',
    '🔒': '[CAPTCHA]',
    '🤖': '[SOLVING]',
    '💉': '[INJECT]',
    '📝': '[FORM]',
    '⏳': '[WAIT]',
    '🎉': '[SUCCESS]',
    '⚠️': '[WARN]',
    'ℹ️': '[INFO]',
    '🖱️': '[CLICK]',
    '🎯': '[TARGET]',
    '💰': '[BALANCE]',
    '⏰': '[TIME]',
    '🔐': '[TOKEN]',
    '🛑': '[STOP]',
}

# Replace all emojis
for emoji, replacement in replacements.items():
    content = content.replace(emoji, replacement)

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed emojis in {os.path.basename(filepath)}")
print(f"Replaced {len(replacements)} different emojis")
