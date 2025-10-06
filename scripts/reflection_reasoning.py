#!/usr/bin/env python3
"""
反射＋推論システム (Reflection + Reasoning System)

牡丹の応答品質を向上させるため、応答前に：
1. 反射（Reflection）: ユーザー入力の意図・感情を分析
2. 推論（Reasoning）: 適切な応答戦略を考える
3. 応答生成: 最終的な回答を生成
"""

import requests
import json

class ReflectionReasoningSystem:
    def __init__(self, model_name="qwen2.5:3b", ollama_host="http://localhost:11434"):
        """
        反射＋推論システムの初期化

        Args:
            model_name: 思考プロセス用のモデル（軽量モデル推奨）
            ollama_host: OllamaサーバーのURL
        """
        self.model_name = model_name
        self.api_url = f"{ollama_host}/api/generate"

    def reflect(self, user_input, conversation_context=""):
        """
        反射: ユーザー入力を分析

        Args:
            user_input: ユーザーの入力
            conversation_context: 過去の会話コンテキスト

        Returns:
            dict: 分析結果（意図、感情、重要ポイント）
        """
        prompt = f"""以下のユーザー入力を分析してください。

【ユーザー入力】
{user_input}

【過去の文脈】
{conversation_context if conversation_context else "なし"}

【分析項目】
1. 意図（何を求めているか）
2. 感情（喜怒哀楽、ニュートラル）
3. 重要ポイント（キーワード、固有名詞）
4. 応答のトーン（カジュアル/フォーマル/励まし/共感など）

JSON形式で返してください。
"""

        response = self._generate(prompt)

        try:
            # JSON抽出を試みる
            if "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass

        # JSONパースに失敗した場合、テキストとして返す
        return {
            "intent": "不明",
            "emotion": "ニュートラル",
            "key_points": [],
            "tone": "カジュアル",
            "raw_analysis": response
        }

    def reason(self, user_input, reflection_result, character_profile):
        """
        推論: 反射結果を元に応答戦略を考える

        Args:
            user_input: ユーザーの入力
            reflection_result: 反射結果
            character_profile: キャラクタープロファイル（牡丹の設定）

        Returns:
            dict: 応答戦略（アプローチ、含めるべき要素）
        """
        prompt = f"""牡丹として、以下の情報を元に応答戦略を考えてください。

【キャラクター】
{character_profile}

【ユーザー入力】
{user_input}

【入力分析結果】
{json.dumps(reflection_result, ensure_ascii=False, indent=2)}

【応答戦略を考える】
1. どのような応答アプローチが適切か（質問に答える/共感する/励ます/冗談を言う など）
2. 牡丹らしさをどう表現するか（ギャル語、絵文字的表現、明るさ）
3. 避けるべきこと（説教くさい、知識をひけらかす など）
4. 具体的な応答の方向性

JSON形式で返してください。
"""

        response = self._generate(prompt)

        try:
            # JSON抽出を試みる
            if "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass

        return {
            "approach": "カジュアルな会話",
            "botan_elements": ["明るさ", "ギャル語"],
            "avoid": ["説教"],
            "direction": "楽しく返す",
            "raw_reasoning": response
        }

    def enhance_response(self, original_response, reasoning_result):
        """
        推論結果を元に応答を改善

        Args:
            original_response: 牡丹の元の応答
            reasoning_result: 推論結果

        Returns:
            str: 改善された応答（またはoriginal_responseそのまま）
        """
        # 現時点では、推論結果を活用した応答改善は
        # 今後の拡張として、まず元の応答をそのまま返す
        #
        # 将来的には：
        # - 推論結果に基づいて応答を調整
        # - 感情表現を強化
        # - ギャル語の度合いを調整
        # などの実装が可能

        return original_response

    def _generate(self, prompt, max_tokens=500):
        """
        Ollamaで推論を実行

        Args:
            prompt: プロンプト
            max_tokens: 最大トークン数

        Returns:
            str: 生成されたテキスト
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.3  # 分析タスクなので低めの温度
            }
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            print(f"[ERROR] 推論エラー: {e}")
            return ""

def main():
    """テスト用メイン関数"""
    print("=" * 60)
    print("反射＋推論システム - テスト")
    print("=" * 60)

    rr = ReflectionReasoningSystem()

    # テストケース
    test_cases = [
        "今日めっちゃ疲れた...",
        "牡丹って何歳？",
        "最近何してる？"
    ]

    character_profile = """
17歳の明るく元気な女子高生ギャル「牡丹」
- ギャル語を自然に使う
- 明るくポジティブ
- 知識をひけらかさない
- 相手を「オジサン」と呼ぶ
"""

    for i, user_input in enumerate(test_cases, 1):
        print(f"\n【テスト {i}】")
        print(f"入力: {user_input}")

        # 反射
        print("\n[反射中...]")
        reflection = rr.reflect(user_input)
        print(f"意図: {reflection.get('intent', '不明')}")
        print(f"感情: {reflection.get('emotion', 'ニュートラル')}")

        # 推論
        print("\n[推論中...]")
        reasoning = rr.reason(user_input, reflection, character_profile)
        print(f"アプローチ: {reasoning.get('approach', '不明')}")
        print(f"牡丹要素: {reasoning.get('botan_elements', [])}")

        print("\n" + "-" * 60)

    print("\n✅ テスト完了")

if __name__ == "__main__":
    main()
