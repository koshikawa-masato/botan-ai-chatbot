#!/usr/bin/env python3
"""
Botan API Gateway - FastAPI Server
WebSocket + REST API for AI Vtuber
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import logging
import httpx
import os

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# サービスURL
CORE_SERVICE_URL = os.getenv("CORE_SERVICE_URL", "http://localhost:8001")
VOICE_SERVICE_URL = os.getenv("VOICE_SERVICE_URL", "http://localhost:8002")

# FastAPIアプリケーション
app = FastAPI(
    title="Botan AI API",
    description="AI Vtuber 牡丹 API Gateway",
    version="2.0.0"
)

# CORS設定（OBS Browser Sourceから接続可能に）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では制限すべき
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# リクエストモデル
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"
    enable_voice: bool = False
    enable_reflection: bool = False

class ChatResponse(BaseModel):
    response: str
    audio_url: Optional[str] = None
    reflection: Optional[dict] = None
    reasoning: Optional[dict] = None

# WebSocket接続管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# ヘルスチェック
@app.get("/")
async def root():
    return {
        "service": "Botan AI API",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "ok",
            "core": "checking...",
            "voice": "checking...",
            "evaluation": "checking..."
        }
    }

# REST API - チャット
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    RESTful チャットエンドポイント
    """
    try:
        logger.info(f"Chat request from user_id={request.user_id}: {request.message}")

        # Core Serviceに転送
        async with httpx.AsyncClient() as client:
            core_response = await client.post(
                f"{CORE_SERVICE_URL}/chat",
                json={
                    "message": request.message,
                    "user_id": request.user_id,
                    "enable_reflection": request.enable_reflection
                },
                timeout=30.0
            )
            core_data = core_response.json()

        botan_response = core_data.get("response", "...")
        reflection = core_data.get("reflection")
        reasoning = core_data.get("reasoning")

        # Voice Serviceで音声生成（enable_voice=True時）
        audio_url = None
        if request.enable_voice:
            async with httpx.AsyncClient() as client:
                voice_response = await client.post(
                    f"{VOICE_SERVICE_URL}/synthesize",
                    json={"text": botan_response},
                    timeout=30.0
                )
                voice_data = voice_response.json()
                if voice_data.get("status") == "success":
                    audio_url = f"/api/audio/{voice_data['filename']}"

        response = ChatResponse(
            response=botan_response,
            audio_url=audio_url,
            reflection=reflection,
            reasoning=reasoning
        )

        return response

    except httpx.TimeoutException:
        logger.error("Service timeout")
        raise HTTPException(status_code=504, detail="Service timeout")
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket - リアルタイムチャット
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocketチャットエンドポイント（OBS連携用）
    """
    await manager.connect(websocket)

    try:
        while True:
            # クライアントからメッセージ受信
            data = await websocket.receive_text()
            message_data = json.loads(data)

            logger.info(f"WebSocket message: {message_data}")

            # TODO: Core Serviceに転送して応答取得
            # TODO: Voice Serviceで音声生成

            # 暫定レスポンス
            response = {
                "type": "chat_response",
                "response": "やっほー！ぼたんだよ！（WebSocket経由）",
                "audio_url": None,
                "timestamp": message_data.get("timestamp")
            }

            # レスポンス送信
            await manager.send_message(response, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# 音声エンドポイント
@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    """
    生成された音声ファイルを取得
    """
    try:
        # Voice Serviceから音声ファイル取得
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{VOICE_SERVICE_URL}/audio/{filename}",
                timeout=10.0
            )

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Audio file not found")

            return JSONResponse(
                content=response.content,
                media_type="audio/mpeg",
                headers={"Content-Disposition": f"inline; filename={filename}"}
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Voice service timeout")
    except Exception as e:
        logger.error(f"Audio fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 設定エンドポイント
@app.get("/api/config")
async def get_config():
    """
    システム設定取得
    """
    return {
        "model": "elyza:botan_custom",
        "voice_model": "eleven_v3",
        "voice_id": "kuon",
        "features": {
            "voice_synthesis": True,
            "reflection_reasoning": True,
            "learning": True
        }
    }

@app.post("/api/config")
async def update_config(config: dict):
    """
    システム設定更新
    """
    # TODO: 設定を永続化
    return {"status": "updated", "config": config}

# 統計エンドポイント
@app.get("/api/stats")
async def get_stats():
    """
    会話統計取得
    """
    return {
        "total_conversations": 0,
        "total_turns": 0,
        "average_score": 0.0,
        "active_connections": len(manager.active_connections)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
