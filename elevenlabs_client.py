#!/usr/bin/env python3
"""
ElevenLabs API Client for Botan Voice Synthesis
Uses ElevenLabs v3 API with kuon voice
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings
import requests

# Add utils directory to path
sys.path.insert(0, str(Path(__file__).parent))
from utils.crypto import get_api_key

# Load environment variables
load_dotenv()

class BotanVoiceClient:
    def __init__(self):
        """Initialize ElevenLabs client for Botan"""
        # Try to get API key (decrypt if encrypted, otherwise use plain)
        encrypted_key = os.getenv("ELEVENLABS_API_KEY")
        if encrypted_key and encrypted_key.startswith("ENC_"):
            self.api_key = get_api_key("ELEVENLABS_API_KEY")
        else:
            self.api_key = encrypted_key

        if not self.api_key:
            raise ValueError(
                "ELEVENLABS_API_KEY not found. "
                "Please copy .env.example to .env and add your API key."
            )

        # Initialize ElevenLabs client
        self.client = ElevenLabs(api_key=self.api_key)

        # Voice settings from .env
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "pFZP5JQG7iQjIQuC4Bku")
        self.model = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")

        # Audio parameters
        self.voice_settings = VoiceSettings(
            stability=float(os.getenv("ELEVENLABS_STABILITY", "0.5")),
            similarity_boost=float(os.getenv("ELEVENLABS_SIMILARITY_BOOST", "0.75")),
            style=float(os.getenv("ELEVENLABS_STYLE", "0.0")),
            use_speaker_boost=os.getenv("ELEVENLABS_USE_SPEAKER_BOOST", "true").lower() == "true"
        )

        # Cache directory
        self.cache_dir = Path("voice_cache")
        self.cache_dir.mkdir(exist_ok=True)

        print(f"[INFO] ElevenLabs client initialized")
        print(f"[INFO] Voice ID: {self.voice_id}")
        print(f"[INFO] Model: {self.model}")

    def text_to_speech(self, text: str, output_path: str = None) -> str:
        """
        Convert text to speech using ElevenLabs API

        Args:
            text: Text to convert to speech
            output_path: Optional custom output path

        Returns:
            Path to generated audio file
        """
        try:
            # Generate unique filename if not provided
            if output_path is None:
                import hashlib
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_path = self.cache_dir / f"botan_{text_hash}.mp3"
            else:
                output_path = Path(output_path)

            # Check cache
            if output_path.exists():
                print(f"[CACHE] Using cached audio: {output_path}")
                return str(output_path)

            print(f"[GENERATING] Converting text to speech...")
            print(f"[TEXT] {text}")

            # Generate speech
            # Note: optimize_streaming_latency is not supported in eleven_v3
            audio_generator = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                output_format="mp3_44100_128",
                text=text,
                model_id=self.model,
                voice_settings=self.voice_settings
            )

            # Save to file
            with open(output_path, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)

            print(f"[SUCCESS] Audio saved to: {output_path}")
            return str(output_path)

        except Exception as e:
            print(f"[ERROR] Text-to-speech failed: {e}")
            raise

    def get_available_voices(self):
        """Get list of available voices"""
        try:
            voices = self.client.voices.get_all()
            return voices
        except Exception as e:
            print(f"[ERROR] Failed to fetch voices: {e}")
            return None

    def test_voice(self, test_text: str = "やっほー！ぼたんだよ！"):
        """Test voice generation with sample text"""
        print("\n[TEST] Testing Botan voice...")
        print(f"[TEST] Text: {test_text}")

        try:
            audio_path = self.text_to_speech(test_text)
            print(f"[TEST] Success! Audio file: {audio_path}")
            return audio_path
        except Exception as e:
            print(f"[TEST] Failed: {e}")
            return None

def main():
    """Test the ElevenLabs client"""
    print("=" * 60)
    print("Botan Voice Client - ElevenLabs v3 Test")
    print("=" * 60)

    try:
        # Initialize client
        client = BotanVoiceClient()

        # Test phrases
        test_phrases = [
            "やっほー！ぼたんだよ！",
            "マジで！？めっちゃ楽しみ！",
            "オジサン、それってどういうこと？",
            "え〜、わかんない！笑"
        ]

        print("\n[TEST] Generating test audio files...")
        for i, text in enumerate(test_phrases, 1):
            print(f"\n--- Test {i}/{len(test_phrases)} ---")
            client.test_voice(text)

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print("\nPlease check:")
        print("1. .env file exists with valid ELEVENLABS_API_KEY")
        print("2. API key is correct and active")
        print("3. Internet connection is available")

if __name__ == "__main__":
    main()
