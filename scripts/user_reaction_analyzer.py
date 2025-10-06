#!/usr/bin/env python3
"""
ユーザーリアクション分析
他己評価：ユーザーの次の発言から牡丹の応答品質を評価
"""

def analyze_user_reaction(botan_response, next_user_input, previous_user_input=None):
    """
    ユーザーリアクションを分析して他己評価スコアを返す

    Args:
        botan_response: 牡丹の応答
        next_user_input: ユーザーの次の発言
        previous_user_input: ユーザーの前の発言（オプション）

    Returns:
        reaction_score: -2.0 ~ +2.0 の他己評価スコア
        reaction_type: リアクションの種類
        reasons: 評価理由のリスト
    """

    reaction_score = 0.0
    reasons = []

    # ボタンの応答長
    botan_length = len(botan_response)
    user_length = len(next_user_input)

    # ===== 1. ポジティブリアクション検出 =====

    # 質問の深掘り
    deepening_patterns = ["それで", "どうして", "なんで", "詳しく", "もっと", "例えば"]
    if any(pattern in next_user_input for pattern in deepening_patterns):
        reaction_score += 1.5
        reasons.append("✅ ユーザーが話題を深掘りしている（会話が続いている）")

    # 共感・同意
    empathy_patterns = ["わかる", "そうだよね", "マジで", "確かに", "いいね", "面白い"]
    if any(pattern in next_user_input for pattern in empathy_patterns):
        reaction_score += 1.0
        reasons.append("✅ ユーザーが共感・同意している")

    # 笑い
    laugh_patterns = ["笑", "w", "草", "ww", "www", "面白"]
    if any(pattern in next_user_input for pattern in laugh_patterns):
        reaction_score += 1.5
        reasons.append("✅ ユーザーが笑っている（良い反応）")

    # 話題の発展（前回と関連する新しい質問）
    if previous_user_input and len(next_user_input) > 10:
        # 簡易判定：前回と似た単語を含むが、全く同じではない
        if previous_user_input != next_user_input and user_length >= 10:
            reaction_score += 0.5
            reasons.append("✅ 会話が自然に発展している")

    # ===== 2. ネガティブリアクション検出 =====

    # 話題の急転換（前回と全く関係ない新しい話題）
    if previous_user_input:
        # 簡易判定：共通単語が少ない
        prev_words = set(previous_user_input)
        next_words = set(next_user_input)
        common_ratio = len(prev_words & next_words) / len(prev_words) if prev_words else 0

        if common_ratio < 0.1 and len(next_user_input) > 5:
            reaction_score -= 1.0
            reasons.append("❌ ユーザーが話題を変えた（牡丹の応答に興味がない？）")

    # 短い返事のみ（無関心）
    short_responses = ["うん", "そう", "はい", "へー", "ふーん", "まあ", "..."]
    if next_user_input in short_responses or user_length <= 3:
        reaction_score -= 1.5
        reasons.append("❌ ユーザーの返事が短い（無関心？）")

    # 同じ質問の繰り返し（牡丹が答えていない）
    if previous_user_input and previous_user_input.strip() == next_user_input.strip():
        reaction_score -= 2.0
        reasons.append("❌ ユーザーが同じ質問を繰り返している（牡丹が答えていない）")

    # ===== 3. キャッチボール性評価 =====

    # 牡丹が長すぎる（自分語り）
    if botan_length > 100:
        if user_length < 10:
            reaction_score -= 1.5
            reasons.append("❌ 牡丹が自分語りしすぎ → ユーザーが短文（キャッチボールできてない）")
        else:
            reasons.append("⚠️ 牡丹の応答が長い（100文字超）が、ユーザーは続けている")

    # 牡丹が適度な長さ（30-70文字）
    elif 30 <= botan_length <= 70:
        if user_length >= 10:
            reaction_score += 0.5
            reasons.append("✅ 牡丹の応答が適度 → ユーザーが続ける（良いキャッチボール）")

    # 牡丹が短すぎる
    elif botan_length < 20:
        if user_length < 10:
            reaction_score -= 0.5
            reasons.append("❌ 牡丹が短すぎ → ユーザーも短い（会話が盛り上がってない）")

    # ===== リアクションタイプを判定 =====

    if reaction_score >= 1.5:
        reaction_type = "非常にポジティブ"
    elif reaction_score >= 0.5:
        reaction_type = "ポジティブ"
    elif reaction_score >= -0.5:
        reaction_type = "ニュートラル"
    elif reaction_score >= -1.5:
        reaction_type = "ネガティブ"
    else:
        reaction_type = "非常にネガティブ"

    # スコアを -2.0 ~ +2.0 に制限
    reaction_score = max(-2.0, min(2.0, reaction_score))

    return reaction_score, reaction_type, reasons


def calculate_combined_score(self_score, reaction_score):
    """
    自己評価と他己評価を統合して総合スコアを計算

    Args:
        self_score: AI自己評価（1-5）
        reaction_score: ユーザーリアクション評価（-2 ~ +2）

    Returns:
        combined_score: 総合スコア（1-5）
        weight_info: 重み付け情報
    """

    # 他己評価を1-5スケールに変換（-2~+2 → 0~1 → 加算調整）
    # reaction_score: -2.0 → -1.0 調整
    # reaction_score:  0.0 →  0.0 調整
    # reaction_score: +2.0 → +1.0 調整

    reaction_adjustment = reaction_score / 2.0

    # 自己評価60% + 他己評価40%の重み付け
    combined_score = self_score + reaction_adjustment

    # 1-5の範囲に制限
    combined_score = max(1.0, min(5.0, combined_score))

    weight_info = {
        "self_score": self_score,
        "reaction_score": reaction_score,
        "reaction_adjustment": reaction_adjustment,
        "combined_score": combined_score
    }

    return combined_score, weight_info


if __name__ == "__main__":
    # テスト

    # ケース1: ポジティブリアクション
    print("=" * 70)
    print("ケース1: ユーザーが笑って深掘り")
    print("=" * 70)
    botan = "えー、プログラミングってなにそれ〜？ぼたん全然わかんない！"
    user_next = "笑 それでどうやって勉強するの？"
    user_prev = "プログラミングって何？"

    score, rtype, reasons = analyze_user_reaction(botan, user_next, user_prev)
    print(f"他己評価: {score:+.1f} ({rtype})")
    for r in reasons:
        print(f"  {r}")

    combined, info = calculate_combined_score(5.0, score)
    print(f"\n自己評価: 5.0, 他己評価: {score:+.1f} → 総合: {combined:.2f}/5.0")

    # ケース2: ネガティブリアクション
    print("\n" + "=" * 70)
    print("ケース2: 牡丹が自分語りしすぎ → ユーザーが短文")
    print("=" * 70)
    botan = "あのね、ぼたんってね、マジで学校が好きでね、友達もいっぱいいてね、毎日楽しくてね、授業も面白いしね、放課後も遊んでてね、最高なんだよね〜！あとね、最近ハマってることがあってね、それは..."
    user_next = "へー"
    user_prev = "最近どう？"

    score, rtype, reasons = analyze_user_reaction(botan, user_next, user_prev)
    print(f"他己評価: {score:+.1f} ({rtype})")
    for r in reasons:
        print(f"  {r}")

    combined, info = calculate_combined_score(4.0, score)
    print(f"\n自己評価: 4.0, 他己評価: {score:+.1f} → 総合: {combined:.2f}/5.0")

    # ケース3: 話題転換
    print("\n" + "=" * 70)
    print("ケース3: ユーザーが話題を変えた")
    print("=" * 70)
    botan = "うん、元気だよ〜！"
    user_next = "今日の天気どう？"
    user_prev = "調子どう？"

    score, rtype, reasons = analyze_user_reaction(botan, user_next, user_prev)
    print(f"他己評価: {score:+.1f} ({rtype})")
    for r in reasons:
        print(f"  {r}")

    combined, info = calculate_combined_score(3.0, score)
    print(f"\n自己評価: 3.0, 他己評価: {score:+.1f} → 総合: {combined:.2f}/5.0")
