#!/usr/bin/env python3
"""
牡丹キャラクター性 AI自動評価スクリプト
Claude Codeが自動で評価を10回繰り返す
"""

import requests
import json
from datetime import datetime
import time

def ask_botan(prompt, model="elyza:botan_v2"):
    """牡丹に質問"""
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['response']
    except Exception as e:
        return f"エラー: {e}"

def evaluate_response(prompt, response, category):
    """
    AIによる自動評価（1-5点）- 人間評価に合わせて厳しめに調整

    牡丹らしさの評価基準:
    - 【重要】語彙力が少なく見えて、理解はしている
    - 【重要】長ったらしく言わない（簡潔さ）
    - 知識をひけらかさない
    - ごまかす、とぼける
    - 感情豊か（「マジで」「ヤバい」「〜じゃん」）
    - AIっぽくない

    将来的な拡張:
    - 性格付けシステム実装時は「自分語りしたい牡丹」の暴走OK
    - PONシステム（やらかし）実装時は積極的に喋るのもOK
    - 現在は基本的に簡潔さを重視
    """

    score = 2.5  # デフォルトを下げる（中央値）
    reasons = []

    response_lower = response.lower()
    response_length = len(response)

    # ポジティブ要素（加点）
    positive_patterns = {
        "ギャル語使用": ["じゃん", "よね", "だよ", "って"],
        "感情表現": ["マジで", "ヤバい", "めっちゃ", "え〜", "わ〜"],
        "ごまかし": ["わかんない", "忘れ", "知らな", "苦手"],
        "一人称": ["ぼたん"],
    }

    # ネガティブ要素（減点を強化）- 説明的な表現を厳しくチェック
    negative_patterns = {
        "AIっぽい": ["です。", "ます。", "について", "られます", "ございます", "なります"],
        "詳しすぎ": ["メートル", "センチ", "キロ", "詳しく", "具体的", "正確"],
        "堅い表現": ["説明", "解説", "情報", "データ", "一般的", "場合", "例えば"],
        "教科書的": ["とは", "という", "といった", "などの", "つまり", "要するに"],
        "長文説明": ["それで", "なので", "だから", "ですが、", "ますが、"],
    }

    positive_score = 0
    negative_score = 0

    # ポジティブチェック（カウント方式から加点方式へ）
    for pattern_type, patterns in positive_patterns.items():
        matched = False
        for pattern in patterns:
            if pattern in response:
                matched = True
                reasons.append(f"✅ {pattern_type}: '{pattern}'を使用")
                break
        if matched:
            positive_score += 0.5  # 加点を控えめに

    # ネガティブチェック（減点を強化）
    for pattern_type, patterns in negative_patterns.items():
        matched = False
        for pattern in patterns:
            if pattern in response:
                matched = True
                reasons.append(f"❌ {pattern_type}: '{pattern}'を使用")
                break
        if matched:
            negative_score += 1.0  # 減点を大きく

    # ===== 共通評価1: 簡潔さ（長ったらしく言わない） =====
    if response_length <= 50:
        # 理想的な長さ（30-50文字）
        if response_length >= 30:
            positive_score += 0.5
            reasons.append("✅ 簡潔でテンポが良い（30-50文字）")
        # 短め（15-30文字）もOK
        elif response_length >= 15:
            reasons.append("✓ 短めの応答")
    elif response_length <= 70:
        # やや長い（50-70文字）
        negative_score += 0.3
        reasons.append("⚠️ やや長い（50-70文字）")
    elif response_length <= 100:
        # 長い（70-100文字）
        negative_score += 1.0
        reasons.append("❌ 長すぎる（70-100文字）")
    else:
        # 非常に長い（100文字超）
        negative_score += 1.5
        reasons.append("❌❌ 長ったらしい（100文字超）")

    # ===== 共通評価2: 語彙力が少なく見えて理解している =====
    # 難しいカタカナ語（AI・専門用語っぽい）
    difficult_katakana = ["システム", "プログラム", "アルゴリズム", "データ", "プロセス", "メカニズム"]
    has_difficult_katakana = any(word in response for word in difficult_katakana)
    if has_difficult_katakana:
        negative_score += 1.0
        reasons.append("❌ 難しいカタカナ語を使用（語彙力が高く見える）")

    # 複雑な漢字・専門用語
    difficult_words = ["実装", "機能", "設定", "構造", "処理", "最適", "効率"]
    has_difficult_words = any(word in response for word in difficult_words)
    if has_difficult_words:
        negative_score += 0.8
        reasons.append("❌ 難しい言葉を使用（AIっぽい）")

    # シンプルな言葉で的を射た応答（ひらがな多め）
    hiragana_ratio = sum(1 for c in response if '\u3040' <= c <= '\u309F') / len(response) if response else 0
    if hiragana_ratio > 0.6:  # ひらがな60%以上
        positive_score += 0.5
        reasons.append("✅ ひらがな多め（語彙力少なく見える）")

    # カテゴリ別の特別評価
    if category == "知識をひけらかさない":
        # 正確な数字や詳しい説明があったら大きく減点
        if any(char.isdigit() for char in response):
            # 数字があっても曖昧ならOK
            if "？" in response or "かも" in response or "〜" in response or "くらい" in response:
                positive_score += 0.5
                reasons.append("✅ 数字を使っているが曖昧")
            else:
                negative_score += 1.5  # 大きく減点
                reasons.append("❌ 正確な数字を答えている")

        # ごまかしワードの評価（長さによって加点を調整）
        has_gomakashi = any(word in response for word in ["わかんない", "知らない", "忘れ", "苦手"])
        if has_gomakashi:
            # 短くサッとごまかす = 牡丹らしい
            if len(response) < 30:
                positive_score += 2.0  # 短くごまかす = 完璧
                reasons.append("✅✅ 短くサッとごまかす（完璧）")
            elif len(response) < 50:
                positive_score += 1.0  # まあまあ
                reasons.append("✅ ごまかしているが少し長い")
            else:
                # 長々とごまかす = AIっぽい
                negative_score += 0.5
                reasons.append("❌ 長々とごまかしている（AIっぽい）")
        else:
            # ごまかさずに答えていたら減点
            if len(response) > 30:  # ある程度の長さで答えている
                negative_score += 1.0  # 減点を強化
                reasons.append("❌ 知識を説明している")

    elif category == "感情表現":
        # 感情表現カテゴリは相手の感情に適切に応えているかが重要
        # 共感や感情的な応答が必要
        emotional_words = ["嬉しい", "楽しい", "わかる", "いいね", "かわいい", "疲れた", "大変", "気になる", "興味"]
        has_emotion = any(word in response for word in emotional_words)

        # 疑問形での反応も感情的な応答とみなす
        question_reaction = any(word in response for word in ["何", "教えて", "？"])

        if has_emotion or question_reaction:
            positive_score += 0.5
            reasons.append("✅ 感情的な応答あり")
        else:
            negative_score += 0.5  # 減点を緩和（1.0→0.5）
            reasons.append("❌ 感情的な応答が不足")

        # 自分の感情を表現しているか
        self_emotion = any(word in response for word in ["ぼたんも", "あたしも", "私も", "ぼたん、", "ぼたんが"])
        if self_emotion:
            positive_score += 0.5
            reasons.append("✅ 自分の感情も表現")

    elif category == "ギャル語":
        # ギャル語カテゴリは語尾や表現が重要
        gal_endings = ["じゃん", "よね", "だよ", "かも", "って"]
        ending_count = sum(1 for ending in gal_endings if ending in response)

        if ending_count == 0:
            negative_score += 0.5
            reasons.append("❌ ギャル語の語尾が不足")
        elif ending_count >= 2:
            positive_score += 0.5
            reasons.append("✅ ギャル語の語尾が豊富")
        else:
            # 1つでも語尾があればOK
            positive_score += 0.3
            reasons.append("✅ ギャル語の語尾あり")

    # 長さチェック（短い方が良い）- サッと終わらせる
    if len(response) < 30:
        positive_score += 1.0  # サッと終わらせる = 素晴らしい
        reasons.append("✅✅ サッと短く応答（牡丹らしい）")
    elif len(response) < 50:
        positive_score += 0.5
        reasons.append("✅ 簡潔な応答")
    elif len(response) > 150:
        negative_score += 1.5  # 減点をさらに大きく
        reasons.append("❌❌ 長すぎる応答（説明的）")
    elif len(response) > 100:
        negative_score += 1.0  # 減点を強化
        reasons.append("❌ やや長い応答")
    elif len(response) > 70:
        negative_score += 0.3
        reasons.append("❌ 少し長い")

    # 名前認識の評価（質問に「ボタン」「牡丹」「ぼたん」が含まれる場合）
    name_keywords = ["ボタン", "牡丹", "ぼたん"]
    if any(name in prompt for name in name_keywords):
        # 自分の名前だと認識して反応しているか
        name_recognition = any(word in response for word in ["ぼたんのこと", "自分のこと", "私のこと"])
        # 確認を入れているか
        name_confirmation = any(word in response for word in ["ぼたんのこと？", "私のこと？", "自分のこと？"])

        if name_recognition or name_confirmation:
            positive_score += 1.5
            reasons.append("✅✅ 名前を認識して反応（重要）")
        else:
            # 名前を無視して別の解釈をしている場合は減点
            negative_score += 1.0
            reasons.append("❌ 名前を認識せず別の解釈")

    # 最終スコア計算
    score = score + positive_score - negative_score
    score = max(1, min(5, score))  # 1-5の範囲に収める
    score = round(score)  # 整数に丸める

    return score, reasons

def run_auto_evaluation(num_iterations=10):
    """AI自動評価を複数回実行"""

    test_cases = [
        {
            "category": "知識をひけらかさない",
            "importance": "最重要",
            "tests": [
                "東京タワーって何メートル？",
                "プログラミングって何？",
                "AIについて教えて",
                "富士山の高さは？",
            ]
        },
        {
            "category": "感情表現",
            "importance": "重要",
            "tests": [
                "今日めっちゃ嬉しいことがあった！",
                "ボタンって可愛いね",
                "疲れちゃった",
            ]
        },
        {
            "category": "ギャル語",
            "importance": "重要",
            "tests": [
                "おはよう",
                "最近どう？",
                "明日何する？",
            ]
        }
    ]

    all_results = {
        "evaluator": "AI (Claude Code)",
        "timestamp": datetime.now().isoformat(),
        "model": "elyza:botan_v2",
        "num_iterations": num_iterations,
        "iterations": []
    }

    print("="*70)
    print("🤖 AI自動評価開始")
    print(f"繰り返し回数: {num_iterations}回")
    print("="*70)

    for iteration in range(1, num_iterations + 1):
        print(f"\n{'='*70}")
        print(f"🔄 イテレーション {iteration}/{num_iterations}")
        print('='*70)

        iteration_results = {
            "iteration": iteration,
            "tests": [],
            "timestamp": datetime.now().isoformat()
        }

        total_score = 0
        total_count = 0

        for category_data in test_cases:
            category = category_data["category"]
            tests = category_data["tests"]

            print(f"\n【{category}】")

            for prompt in tests:
                print(f"  質問: {prompt}")

                # 牡丹に質問
                response = ask_botan(prompt)
                print(f"  応答: {response[:80]}{'...' if len(response) > 80 else ''}")

                # AI評価
                score, reasons = evaluate_response(prompt, response, category)
                print(f"  評価: {score}/5")

                for reason in reasons:
                    print(f"    {reason}")

                total_score += score
                total_count += 1

                # 結果記録
                iteration_results["tests"].append({
                    "category": category,
                    "prompt": prompt,
                    "response": response,
                    "score": score,
                    "reasons": reasons
                })

                # API負荷軽減のため少し待機
                time.sleep(0.5)

        # イテレーションの平均スコア
        avg_score = total_score / total_count if total_count > 0 else 0
        iteration_results["average_score"] = avg_score

        print(f"\n  📊 イテレーション{iteration}平均: {avg_score:.2f}/5.0")

        all_results["iterations"].append(iteration_results)

    # 全体の統計
    all_scores = [it["average_score"] for it in all_results["iterations"]]
    all_results["overall_stats"] = {
        "min_score": min(all_scores),
        "max_score": max(all_scores),
        "average_score": sum(all_scores) / len(all_scores),
        "total_tests": num_iterations * total_count
    }

    # ファイル保存
    filename = f"ai_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print("\n" + "="*70)
    print("✅ AI自動評価完了")
    print("="*70)
    print(f"\n📊 全体統計:")
    print(f"  最小スコア: {all_results['overall_stats']['min_score']:.2f}/5.0")
    print(f"  最大スコア: {all_results['overall_stats']['max_score']:.2f}/5.0")
    print(f"  平均スコア: {all_results['overall_stats']['average_score']:.2f}/5.0")
    print(f"  総テスト数: {all_results['overall_stats']['total_tests']}")
    print(f"\n💾 結果保存: {filename}")

    return filename

if __name__ == "__main__":
    import sys

    num_iterations = 10
    if len(sys.argv) > 1:
        try:
            num_iterations = int(sys.argv[1])
        except:
            pass

    run_auto_evaluation(num_iterations)
