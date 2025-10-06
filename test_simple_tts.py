#!/usr/bin/env python3
"""
Simple TTS test without encryption
For testing purposes, use API key directly
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Get encrypted key
encrypted_key = os.getenv("ELEVENLABS_API_KEY")
print(f"Encrypted key: {encrypted_key[:50]}...")
print(f"Key starts with ENC_: {encrypted_key.startswith('ENC_') if encrypted_key else False}")

# このAPIキーは暗号化されているため、元のWindows環境でしか復号化できません
# 代わりに、平文のAPIキーを直接.envに設定してテストすることをお勧めします

print("\n解決策:")
print("1. Windows環境 (C:/Users/firec/Documents/aite/aite/botan) でtest_tts.pyを実行")
print("2. または、.envに平文のAPIキーを一時的に設定")
print("   ELEVENLABS_API_KEY_PLAIN=sk_your_actual_key_here")
