#!/usr/bin/env python3
"""
牡丹との学習型チャット
- 会話を記録
- AI自動評価を実行
- 高評価会話から学習
"""

import requests
import json
import sys
from datetime import datetime
from pathlib import Path

# auto_evaluate_botan.py から評価関数をインポート
from auto_evaluate_botan import evaluate_response

# user_reaction_analyzer.py から他己評価関数をインポート
from user_reaction_analyzer import analyze_user_reaction, calculate_combined_score

class LearningBotanChat:
    def __init__(self, model_name="elyza:botan_v2"):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/generate"
        self.conversation_history = []
        self.session_start = datetime.now()

    def check_ollama(self):
        """Ollamaが起動しているか確認"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def send_message(self, user_input):
        """メッセージを牡丹に送信"""
        payload = {
            "model": self.model_name,
            "prompt": user_input,
            "stream": True
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                stream=True,
                timeout=60
            )

            full_response = ""
            print("牡丹: ", end="", flush=True)

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            token = data["response"]
                            print(token, end="", flush=True)
                            full_response += token

                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

            print()  # 改行
            return full_response

        except requests.exceptions.RequestException as e:
            print(f"\n❌ エラー: {e}")
            return None

    def auto_evaluate(self, user_input, botan_response):
        """AI自動評価を実行"""
        # カテゴリを推測（簡易版）
        category = self.guess_category(user_input)

        score, reasons = evaluate_response(user_input, botan_response, category)

        return {
            "score": score,
            "category": category,
            "reasons": reasons
        }

    def guess_category(self, user_input):
        """質問からカテゴリを推測"""
        knowledge_keywords = ["何", "教えて", "どのくらい", "メートル", "って何"]
        emotion_keywords = ["嬉しい", "疲れ", "可愛い", "ボタン", "牡丹"]

        user_lower = user_input.lower()

        if any(kw in user_input for kw in knowledge_keywords):
            return "知識をひけらかさない"
        elif any(kw in user_input for kw in emotion_keywords):
            return "感情表現"
        else:
            return "ギャル語"

    def save_conversation(self):
        """会話履歴を保存"""
        if not self.conversation_history:
            print("📝 保存する会話がありません")
            return None

        # 統計情報を計算（総合スコア優先、なければ自己評価）
        scores = []
        combined_scores = []
        for turn in self.conversation_history:
            self_score = turn["evaluation"]["score"]
            scores.append(self_score)

            # 総合スコアがあれば使う
            if "reaction_evaluation" in turn:
                combined_scores.append(turn["reaction_evaluation"]["combined_score"])
            else:
                combined_scores.append(self_score)

        stats = {
            "average_score": sum(scores) / len(scores) if scores else 0,
            "average_combined_score": sum(combined_scores) / len(combined_scores) if combined_scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "high_quality_turns": len([s for s in combined_scores if s >= 4]),
            "total_turns": len(scores),
            "turns_with_reaction": len([t for t in self.conversation_history if "reaction_evaluation" in t])
        }

        # 保存データ
        data = {
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "model": self.model_name,
            "statistics": stats,
            "conversations": self.conversation_history
        }

        # ファイル名生成
        filename = f"learning_session_{self.session_start.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = Path(filename)

        # 保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n💾 会話を保存しました: {filename}")
        print(f"📊 統計:")
        print(f"   総ターン数: {stats['total_turns']}")
        print(f"   自己評価平均: {stats['average_score']:.2f}/5.0")
        print(f"   総合評価平均: {stats['average_combined_score']:.2f}/5.0")
        print(f"   他己評価済み: {stats['turns_with_reaction']}ターン")
        print(f"   高品質ターン: {stats['high_quality_turns']} ({stats['high_quality_turns']/stats['total_turns']*100:.1f}%)")

        return filepath

    def print_welcome(self):
        """ウェルカムメッセージ"""
        print("=" * 70)
        print("🌸 牡丹との学習型チャット 🌸")
        print("=" * 70)
        print(f"モデル: {self.model_name}")
        print("✨ 機能: 会話記録 + 自己評価 + 他己評価 + 学習データ蓄積")
        print()
        print("📊 評価システム:")
        print("  - 自己評価: AIが牡丹の応答を評価（1-5点）")
        print("  - 他己評価: あなたのリアクションから評価（-2~+2）")
        print("  - 総合評価: 両方を統合した最終スコア")
        print()
        print("💡 使い方:")
        print("  - メッセージを入力してEnterで送信")
        print("  - 'exit' または 'quit' で終了（自動保存）")
        print("  - 'score' で現在のセッション統計を表示")
        print("  - 'clear' で会話履歴をクリア（保存されません）")
        print("=" * 70)
        print()

    def show_statistics(self):
        """現在のセッション統計を表示"""
        if not self.conversation_history:
            print("📊 まだ会話がありません\n")
            return

        scores = [turn["evaluation"]["score"] for turn in self.conversation_history]
        combined_scores = []
        for turn in self.conversation_history:
            if "reaction_evaluation" in turn:
                combined_scores.append(turn["reaction_evaluation"]["combined_score"])
            else:
                combined_scores.append(turn["evaluation"]["score"])

        print("\n" + "=" * 70)
        print("📊 現在のセッション統計")
        print("=" * 70)
        print(f"総ターン数: {len(scores)}")
        print(f"自己評価平均: {sum(scores)/len(scores):.2f}/5.0")
        print(f"総合評価平均: {sum(combined_scores)/len(combined_scores):.2f}/5.0")
        print(f"他己評価済み: {len([t for t in self.conversation_history if 'reaction_evaluation' in t])}ターン")
        print(f"高品質ターン（4-5点）: {len([s for s in combined_scores if s >= 4])} ({len([s for s in combined_scores if s >= 4])/len(combined_scores)*100:.1f}%)")
        print()

        # 最近の評価を表示
        print("最近の評価:")
        for turn in self.conversation_history[-3:]:
            self_score = turn['evaluation']['score']
            if 'reaction_evaluation' in turn:
                combined = turn['reaction_evaluation']['combined_score']
                print(f"  [自己:{self_score}/5 総合:{combined:.1f}/5] {turn['user'][:30]}...")
            else:
                print(f"  [自己:{self_score}/5] {turn['user'][:30]}...")
        print("=" * 70 + "\n")

    def run(self):
        """メインループ"""
        # Ollama起動確認
        if not self.check_ollama():
            print("❌ Ollamaが起動していません")
            print("   次のコマンドで起動してください: ollama serve")
            sys.exit(1)

        self.print_welcome()

        # 初回挨拶
        print("牡丹: やっほ〜！何か話そうよ〜！何でも聞いてね！\n")

        while True:
            try:
                # ユーザー入力
                user_input = input("あなた: ").strip()

                if not user_input:
                    continue

                # 終了コマンド
                if user_input.lower() in ['exit', 'quit', '終了', 'さようなら']:
                    print("\n牡丹: バイバイ〜！またね〜！また話そうね！\n")
                    self.save_conversation()
                    break

                # クリアコマンド
                if user_input.lower() == 'clear':
                    self.conversation_history.clear()
                    print("✅ 会話履歴をクリアしました\n")
                    continue

                # 統計表示コマンド
                if user_input.lower() == 'score':
                    self.show_statistics()
                    continue

                # 【他己評価】前のターンのリアクション分析
                if len(self.conversation_history) >= 1:
                    prev_turn = self.conversation_history[-1]
                    prev_prev_user = self.conversation_history[-2]["user"] if len(self.conversation_history) >= 2 else None

                    # ユーザーリアクションを分析
                    reaction_score, reaction_type, reaction_reasons = analyze_user_reaction(
                        prev_turn["botan"],
                        user_input,
                        prev_prev_user
                    )

                    # 総合スコアを計算
                    combined_score, weight_info = calculate_combined_score(
                        prev_turn["evaluation"]["score"],
                        reaction_score
                    )

                    # 前のターンに他己評価を追加
                    prev_turn["reaction_evaluation"] = {
                        "reaction_score": reaction_score,
                        "reaction_type": reaction_type,
                        "reasons": reaction_reasons,
                        "combined_score": combined_score
                    }

                    # 他己評価の簡潔な表示
                    if reaction_score >= 1.0:
                        emoji = "😊"
                    elif reaction_score >= 0:
                        emoji = "😐"
                    else:
                        emoji = "😕"

                    print(f"   {emoji} 前の応答への反応: {reaction_type} ({reaction_score:+.1f}) → 総合: {combined_score:.2f}/5.0")

                # メッセージ送信
                response = self.send_message(user_input)

                if response:
                    # AI自動評価（自己評価）
                    evaluation = self.auto_evaluate(user_input, response)

                    # 評価結果を簡潔に表示
                    score_emoji = "⭐" * evaluation["score"]
                    print(f"   💬 自己評価: {score_emoji} ({evaluation['score']}/5)")

                    # 履歴に追加（他己評価は次のターンで追加される）
                    self.conversation_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "user": user_input,
                        "botan": response,
                        "evaluation": evaluation
                    })

                print()  # 空行

            except KeyboardInterrupt:
                print("\n\n牡丹: え〜、急に終わっちゃうの？またね〜！\n")
                self.save_conversation()
                break
            except Exception as e:
                print(f"\n❌ エラーが発生しました: {e}\n")

if __name__ == "__main__":
    chat = LearningBotanChat(model_name="elyza:botan_v2")
    chat.run()
