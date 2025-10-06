#!/usr/bin/env python3
"""
Voice Synthesis System for Botan
Handles audio playback and voice cache management
"""

import pygame
import threading
from pathlib import Path
from elevenlabs_client import BotanVoiceClient

class VoiceSynthesisSystem:
    def __init__(self):
        """Initialize voice synthesis system"""
        # Initialize ElevenLabs client
        self.voice_client = BotanVoiceClient()

        # Initialize pygame for audio playback
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        # Thread management
        self.playback_thread = None
        self.is_playing = False

        print("[INFO] Voice synthesis system initialized")

    def speak(self, text: str, play_audio: bool = True, async_mode: bool = True) -> str:
        """
        Convert text to speech and optionally play it

        Args:
            text: Text to speak
            play_audio: Whether to play the audio (default: True)
            async_mode: If True, play audio asynchronously (default: True)

        Returns:
            Path to audio file
        """
        # Generate audio
        audio_path = self.voice_client.text_to_speech(text)

        # Play audio if requested
        if play_audio:
            if async_mode:
                self.play_audio_async(audio_path)
            else:
                self.play_audio(audio_path)

        return audio_path

    def play_audio(self, audio_path: str):
        """
        Play audio file using pygame

        Args:
            audio_path: Path to audio file
        """
        try:
            print(f"[PLAYING] {audio_path}")

            # Load and play audio
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            print("[FINISHED] Audio playback complete")

        except Exception as e:
            print(f"[ERROR] Playback failed: {e}")

    def play_audio_async(self, audio_path: str):
        """
        Play audio file asynchronously in background thread

        Args:
            audio_path: Path to audio file
        """
        # Stop previous playback if still running
        if self.is_playing and self.playback_thread and self.playback_thread.is_alive():
            pygame.mixer.music.stop()
            self.playback_thread.join(timeout=0.5)

        # Start new playback thread
        self.is_playing = True
        self.playback_thread = threading.Thread(
            target=self._play_audio_thread,
            args=(audio_path,),
            daemon=True
        )
        self.playback_thread.start()

    def _play_audio_thread(self, audio_path: str):
        """
        Internal method to play audio in background thread

        Args:
            audio_path: Path to audio file
        """
        try:
            print(f"[PLAYING] {audio_path}")

            # Load and play audio
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            print("[FINISHED] Audio playback complete")

        except Exception as e:
            print(f"[ERROR] Playback failed: {e}")
        finally:
            self.is_playing = False

    def stop_audio(self):
        """Stop current audio playback"""
        pygame.mixer.music.stop()
        self.is_playing = False
        print("[STOPPED] Audio playback stopped")

    def clear_cache(self):
        """Clear voice cache directory"""
        cache_dir = Path("voice_cache")
        if cache_dir.exists():
            for file in cache_dir.glob("*.mp3"):
                file.unlink()
            print("[INFO] Voice cache cleared")
        else:
            print("[INFO] No cache to clear")

    def get_cache_size(self):
        """Get total size of cached audio files"""
        cache_dir = Path("voice_cache")
        if not cache_dir.exists():
            return 0

        total_size = sum(f.stat().st_size for f in cache_dir.glob("*.mp3"))
        return total_size

    def cleanup(self):
        """Cleanup resources"""
        # Stop any ongoing playback
        if self.is_playing:
            pygame.mixer.music.stop()
            if self.playback_thread and self.playback_thread.is_alive():
                self.playback_thread.join(timeout=1.0)

        pygame.mixer.quit()
        print("[INFO] Voice synthesis system cleaned up")

def main():
    """Test voice synthesis system"""
    print("=" * 60)
    print("Botan Voice Synthesis System - Test")
    print("=" * 60)

    try:
        # Initialize system
        vs = VoiceSynthesisSystem()

        # Test phrases
        test_phrases = [
            "やっほー！ぼたんだよ！",
            "マジで！？めっちゃ楽しみ！",
            "オジサン、それってどういうこと？"
        ]

        for i, text in enumerate(test_phrases, 1):
            print(f"\n--- Test {i}/{len(test_phrases)} ---")
            print(f"[TEXT] {text}")
            vs.speak(text, play_audio=True)
            print()

        # Show cache info
        cache_size = vs.get_cache_size()
        print(f"\n[INFO] Cache size: {cache_size / 1024:.2f} KB")

        # Cleanup
        vs.cleanup()

        print("\n" + "=" * 60)
        print("Test completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")

if __name__ == "__main__":
    main()
