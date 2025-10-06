#!/usr/bin/env python3
"""
フィラー音声システム (Filler Sounds System)

反射＋推論中に「考えている感じ」を出すため、
フィラー音声（えーっと、んー、など）を再生
"""

import random
from pathlib import Path
from elevenlabs_client import BotanVoiceClient

class FillerSoundSystem:
    def __init__(self):
        """フィラー音声システムの初期化"""
        self.voice_client = BotanVoiceClient()
        self.filler_dir = Path("filler_cache")
        self.filler_dir.mkdir(exist_ok=True)

        # 牡丹らしいフィラー音声のバリエーション
        self.filler_phrases = [
            "えーっとね",
            "んー",
            "そうだね〜",
            "ちょっと待って",
            "なんて言うか〜",
            "あー",
            "うーん",
            "えっと〜"
        ]

        print(f"[INFO] Filler sound system initialized ({len(self.filler_phrases)} variations)")

    def generate_all_fillers(self):
        """すべてのフィラー音声を事前生成"""
        print("\n🎵 フィラー音声を生成中...")

        for i, phrase in enumerate(self.filler_phrases, 1):
            # ファイル名を生成（フィラー用の固定プレフィックス）
            filename = self.filler_dir / f"filler_{i:02d}.mp3"

            if filename.exists():
                print(f"  [{i}/{len(self.filler_phrases)}] ✓ {phrase} (キャッシュ済み)")
                continue

            try:
                print(f"  [{i}/{len(self.filler_phrases)}] 生成中: {phrase}...", end=" ", flush=True)
                self.voice_client.text_to_speech(phrase, str(filename))
                print("✓")
            except Exception as e:
                print(f"✗ エラー: {e}")

        print("✅ フィラー音声の準備完了\n")

    def get_random_filler(self):
        """ランダムなフィラー音声を取得"""
        idx = random.randint(1, len(self.filler_phrases))
        filler_path = self.filler_dir / f"filler_{idx:02d}.mp3"

        if filler_path.exists():
            return str(filler_path)
        else:
            # フィラーが存在しない場合は最初のを返す
            return str(self.filler_dir / "filler_01.mp3")

    def get_thinking_filler(self):
        """「考えている」感じのフィラーを取得"""
        thinking_fillers = ["えーっとね", "んー", "うーん", "なんて言うか〜"]
        phrase = random.choice(thinking_fillers)

        # フレーズのインデックスを探す
        try:
            idx = self.filler_phrases.index(phrase) + 1
            filler_path = self.filler_dir / f"filler_{idx:02d}.mp3"

            if filler_path.exists():
                return str(filler_path)
        except ValueError:
            pass

        # デフォルトは最初のフィラー
        return str(self.filler_dir / "filler_01.mp3")

def main():
    """フィラー音声を生成"""
    print("=" * 60)
    print("フィラー音声生成ツール")
    print("=" * 60)

    filler_system = FillerSoundSystem()
    filler_system.generate_all_fillers()

    print("\n📁 生成されたファイル:")
    for file in sorted(filler_system.filler_dir.glob("filler_*.mp3")):
        size = file.stat().st_size / 1024
        print(f"  - {file.name} ({size:.1f} KB)")

    print("\n✨ フィラー音声システムの準備が完了しました")
    print("   chat_with_learning.py で自動的に使用されます")

if __name__ == "__main__":
    main()
