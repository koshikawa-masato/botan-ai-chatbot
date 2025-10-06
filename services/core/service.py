#!/usr/bin/env python3
"""
Core Service - Ollama Integration
牡丹の会話処理を担当
"""

import requests
import json
from typing import Optional, Dict, List
from pathlib import Path
import sys

# scripts/から既存モジュールをインポート
sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))

from reflection_reasoning import ReflectionReasoningSystem
from user_reaction_analyzer import analyze_user_reaction, calculate_combined_score

class BotanCoreService:
    def __init__(
        self,
        model_name: str = "elyza:botan_custom",
        ollama_host: str = "http://localhost:11434",
        enable_reflection: bool = False
    ):
        """
        牡丹コアサービスの初期化

        Args:
            model_name: 使用するOllamaモデル
            ollama_host: OllamaサーバーのURL
            enable_reflection: 反射+推論システムを有効化
        """
        self.model_name = model_name
        self.api_url = f"{ollama_host}/api/chat"
        self.enable_reflection = enable_reflection

        # 会話履歴（Ollama chat API用）
        self.chat_messages: List[Dict] = []

        # 反射+推論システム
        self.reflection_system = (
            ReflectionReasoningSystem() if enable_reflection else None
        )

        # 牡丹のキャラクタープロファイル
        self.character_profile = """
17歳の明るく元気な女子高生ギャル「牡丹」
- ギャル語を自然に使う
- 明るくポジティブ
- 知識をひけらかさない
- 相手を「オジサン」と呼ぶ
"""

        print(f"[CORE] Botan Core Service initialized")
        print(f"[CORE] Model: {self.model_name}")
        print(f"[CORE] Reflection: {self.enable_reflection}")

    def chat(
        self,
        user_input: str,
        user_id: str = "default"
    ) -> Dict:
        """
        ユーザー入力に対して応答を生成

        Args:
            user_input: ユーザーの入力
            user_id: ユーザーID

        Returns:
            応答データ（response, reflection, reasoningなど）
        """
        result = {
            "response": "",
            "reflection": None,
            "reasoning": None,
            "self_evaluation": None
        }

        # 反射+推論（有効な場合）
        if self.enable_reflection and self.reflection_system:
            # 会話コンテキスト作成
            context = self._get_conversation_context()

            # 反射: ユーザー入力を分析
            reflection_result = self.reflection_system.reflect(
                user_input, context
            )
            result["reflection"] = reflection_result

            # 推論: 応答戦略を考える
            reasoning_result = self.reflection_system.reason(
                user_input,
                reflection_result,
                self.character_profile
            )
            result["reasoning"] = reasoning_result

        # Ollamaで応答生成
        self.chat_messages.append({
            "role": "user",
            "content": user_input
        })

        payload = {
            "model": self.model_name,
            "messages": self.chat_messages,
            "stream": False
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30
            )
            data = response.json()

            # 応答テキスト取得
            if "message" in data and "content" in data["message"]:
                botan_response = data["message"]["content"]
                result["response"] = botan_response

                # 会話履歴に追加
                self.chat_messages.append({
                    "role": "assistant",
                    "content": botan_response
                })
            else:
                result["response"] = "ごめん、ちょっとわかんなかった..."

        except Exception as e:
            print(f"[CORE ERROR] {e}")
            result["response"] = "えーっと、調子悪いかも..."

        return result

    def evaluate_response(
        self,
        user_input: str,
        botan_response: str,
        user_reaction: Optional[str] = None
    ) -> Dict:
        """
        応答を評価

        Args:
            user_input: ユーザー入力
            botan_response: 牡丹の応答
            user_reaction: ユーザーのリアクション（任意）

        Returns:
            評価結果（self_score, reaction_score, combined_scoreなど）
        """
        evaluation = {
            "self_score": 0.0,
            "reaction_score": None,
            "combined_score": 0.0
        }

        # TODO: 自己評価システム統合
        # from auto_evaluate_botan import evaluate_conversation

        # ユーザーリアクション分析
        if user_reaction:
            reaction_result = analyze_user_reaction(user_reaction)
            evaluation["reaction_score"] = reaction_result["score"]

            # 総合評価
            if evaluation["self_score"] > 0:
                evaluation["combined_score"] = calculate_combined_score(
                    evaluation["self_score"],
                    reaction_result["score"]
                )

        return evaluation

    def _get_conversation_context(self, max_turns: int = 3) -> str:
        """
        最近の会話コンテキストを取得
        """
        if not self.chat_messages:
            return ""

        recent_messages = self.chat_messages[-max_turns*2:]
        context_parts = []

        for msg in recent_messages:
            role = "ユーザー" if msg["role"] == "user" else "牡丹"
            context_parts.append(f"{role}: {msg['content']}")

        return "\n".join(context_parts)

    def reset_conversation(self):
        """
        会話履歴をリセット
        """
        self.chat_messages = []
        print("[CORE] Conversation reset")

# FastAPI integration
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Botan Core Service")

# グローバルインスタンス
core_service = None

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"
    enable_reflection: bool = False

class EvaluationRequest(BaseModel):
    user_input: str
    botan_response: str
    user_reaction: Optional[str] = None

@app.on_event("startup")
async def startup():
    global core_service
    core_service = BotanCoreService(
        model_name="elyza:botan_custom",
        enable_reflection=True
    )

@app.post("/chat")
async def chat(request: ChatRequest):
    if not core_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    result = core_service.chat(
        user_input=request.message,
        user_id=request.user_id
    )
    return result

@app.post("/evaluate")
async def evaluate(request: EvaluationRequest):
    if not core_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    result = core_service.evaluate_response(
        user_input=request.user_input,
        botan_response=request.botan_response,
        user_reaction=request.user_reaction
    )
    return result

@app.post("/reset")
async def reset():
    if not core_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    core_service.reset_conversation()
    return {"status": "reset"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "core"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
