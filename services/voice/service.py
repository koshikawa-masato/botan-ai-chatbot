#!/usr/bin/env python3
"""
Voice Service - ElevenLabs Integration
音声合成を担当
"""

import os
import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

# scripts/から既存モジュールをインポート
sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))

from elevenlabs_client import BotanVoiceClient

class VoiceService:
    def __init__(self):
        """
        音声合成サービスの初期化
        """
        self.voice_client = BotanVoiceClient()
        self.cache_dir = Path("/app/voice_cache")  # Docker内パス
        self.cache_dir.mkdir(exist_ok=True, parents=True)

        print("[VOICE] Voice Service initialized")
        print(f"[VOICE] Model: {self.voice_client.model}")
        print(f"[VOICE] Voice ID: {self.voice_client.voice_id}")

    def synthesize(self, text: str, output_filename: Optional[str] = None) -> str:
        """
        テキストを音声に変換

        Args:
            text: 変換するテキスト
            output_filename: 出力ファイル名（オプション）

        Returns:
            生成された音声ファイルのパス
        """
        try:
            if output_filename:
                output_path = self.cache_dir / output_filename
            else:
                # ハッシュベースのファイル名生成
                import hashlib
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_path = self.cache_dir / f"botan_{text_hash}.mp3"

            # 音声生成
            audio_path = self.voice_client.text_to_speech(
                text,
                str(output_path)
            )

            return audio_path

        except Exception as e:
            print(f"[VOICE ERROR] {e}")
            raise

    def get_cache_size(self) -> int:
        """
        キャッシュサイズ取得（バイト）
        """
        total_size = sum(
            f.stat().st_size
            for f in self.cache_dir.glob("*.mp3")
            if f.is_file()
        )
        return total_size

    def clear_cache(self):
        """
        キャッシュクリア
        """
        for file in self.cache_dir.glob("*.mp3"):
            file.unlink()
        print("[VOICE] Cache cleared")

# FastAPI integration
app = FastAPI(title="Botan Voice Service")

# グローバルインスタンス
voice_service = None

class SynthesizeRequest(BaseModel):
    text: str
    filename: Optional[str] = None

@app.on_event("startup")
async def startup():
    global voice_service
    voice_service = VoiceService()

@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    """
    テキストを音声に変換
    """
    if not voice_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        audio_path = voice_service.synthesize(
            text=request.text,
            output_filename=request.filename
        )

        # ファイル名のみ返す（API Gatewayで完全URLに変換）
        filename = Path(audio_path).name

        return {
            "status": "success",
            "filename": filename,
            "path": audio_path
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """
    音声ファイル取得
    """
    if not voice_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    file_path = voice_service.cache_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=filename
    )

@app.get("/stats")
async def get_stats():
    """
    統計情報取得
    """
    if not voice_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    cache_size = voice_service.get_cache_size()
    num_files = len(list(voice_service.cache_dir.glob("*.mp3")))

    return {
        "cache_size_bytes": cache_size,
        "cache_size_mb": round(cache_size / 1024 / 1024, 2),
        "num_cached_files": num_files
    }

@app.delete("/cache")
async def clear_cache():
    """
    キャッシュクリア
    """
    if not voice_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    voice_service.clear_cache()
    return {"status": "cleared"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "voice"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
