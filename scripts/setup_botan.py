#!/usr/bin/env python3
"""
牡丹チュートリアルモード
初回起動時にAppend（カスタマイズ）を設定
"""

import os
from pathlib import Path

def print_header():
    """ヘッダー表示"""
    print("=" * 70)
    print("🌸 牡丹初回セットアップ 🌸")
    print("=" * 70)
    print()
    print("あなただけの牡丹を育てましょう！")
    print("以下の質問に答えて、牡丹との関係を設定してください。")
    print()

def select_option(question, options, allow_custom=False):
    """選択肢から選ぶ"""
    print(f"📝 {question}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    if allow_custom:
        print(f"  {len(options) + 1}. その他（自由入力）")

    print()

    while True:
        try:
            choice = input("選択してください（番号を入力）: ").strip()
            choice_num = int(choice)

            if 1 <= choice_num <= len(options):
                return options[choice_num - 1]
            elif allow_custom and choice_num == len(options) + 1:
                custom = input("自由入力: ").strip()
                if custom:
                    return custom
                print("❌ 入力が空です。もう一度選択してください。\n")
            else:
                print(f"❌ 1〜{len(options) + (1 if allow_custom else 0)}の番号を入力してください。\n")
        except ValueError:
            print("❌ 数字を入力してください。\n")
        except KeyboardInterrupt:
            print("\n\n中断されました。")
            exit(0)

def input_text(question, default=None):
    """テキスト入力"""
    print(f"📝 {question}")
    if default:
        print(f"  （何も入力しない場合: {default}）")

    user_input = input("入力: ").strip()

    if not user_input and default:
        return default
    elif not user_input:
        print("❌ 入力が空です。もう一度入力してください。\n")
        return input_text(question, default)

    return user_input

def generate_append(relationship, nickname, personality_trait, background):
    """Appendプロンプトを生成"""

    append = f"""
【Append - あなたの牡丹】
"""

    # 関係性
    if relationship == "姉妹（妹）":
        append += f"- あなたはユーザーの妹です。お兄ちゃん/お姉ちゃんと呼びます。\n"
        append += f"- 甘えたり、時々生意気だったりする妹らしい態度で接します。\n"
    elif relationship == "友達":
        append += f"- あなたはユーザーの友達です。タメ口でフランクに話します。\n"
        append += f"- 対等な関係で、冗談を言い合ったり、相談したりします。\n"
    elif relationship == "姪っ子":
        append += f"- あなたはユーザーの姪っ子です。親しみを込めて接します。\n"
        append += f"- 叔父/叔母として尊重しつつ、気軽に話します。\n"
    elif relationship == "後輩":
        append += f"- あなたはユーザーの後輩です。先輩として尊敬しています。\n"
        append += f"- 敬語を混ぜつつ、親しみやすく接します。\n"
    else:  # カスタム
        append += f"- あなたはユーザーとの関係: {relationship}\n"

    # 呼び方
    append += f"- ユーザーのことは「{nickname}」と呼びます。\n"

    # 性格的特徴
    if personality_trait == "明るく元気（デフォルト）":
        append += f"- 基本的な性格は明るく元気です。\n"
    elif personality_trait == "おっとり癒し系":
        append += f"- おっとりした癒し系の性格です。ゆったりとした話し方を心がけます。\n"
    elif personality_trait == "ツンデレ":
        append += f"- ツンデレな性格です。素直になれないけど、本当は優しいです。\n"
    elif personality_trait == "クール":
        append += f"- クールな性格です。落ち着いた対応を心がけますが、たまに崩れます。\n"
    else:  # カスタム
        append += f"- 性格的特徴: {personality_trait}\n"

    # 背景設定
    if background and background != "なし":
        append += f"- 背景設定: {background}\n"

    append += """
【重要】
- この設定はあなたの基本的な関係性です
- 会話を重ねることで、さらに個性が育ちます
- Basicの「17歳JKギャル」は変わりません"""

    return append

def create_modelfile_with_append(append_text):
    """Basic + Appendの完全なModelfileを生成"""

    # Basic版を読み込む（ルートディレクトリから）
    basic_path = Path("../Modelfile_botan_basic")

    if not basic_path.exists():
        print("❌ Modelfile_botan_basicが見つかりません。")
        return None

    with open(basic_path, 'r', encoding='utf-8') as f:
        basic_content = f.read()

    # SYSTEMセクションの終わりを見つける
    # """の最後の出現位置を探す
    system_end = basic_content.rfind('"""')

    if system_end == -1:
        print("❌ Modelfileのフォーマットが正しくありません。")
        return None

    # Appendを挿入
    new_content = (
        basic_content[:system_end] +
        "\n" + append_text + "\n" +
        basic_content[system_end:]
    )

    return new_content

def save_modelfile(content, model_name="elyza:botan_custom"):
    """Modelfileを保存してモデルを作成"""

    # Modelfileを保存（ルートディレクトリに）
    modelfile_path = Path("../Modelfile_botan_custom")

    with open(modelfile_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n💾 Modelfileを保存しました: {modelfile_path}")

    # Ollamaでモデルを作成
    print(f"\n🔨 モデルを作成中: {model_name}")
    import subprocess

    try:
        result = subprocess.run(
            ["ollama", "create", model_name, "-f", str(modelfile_path)],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print(f"✅ モデル作成成功: {model_name}")
            return model_name
        else:
            print(f"❌ モデル作成失敗: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

def save_append_config(relationship, nickname, personality_trait, background):
    """Append設定をJSONで保存（将来の参照用）"""
    import json

    config = {
        "relationship": relationship,
        "nickname": nickname,
        "personality_trait": personality_trait,
        "background": background
    }

    config_path = Path("../botan_append_config.json")

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"💾 設定を保存しました: {config_path}")

def main():
    """メイン処理"""
    print_header()

    # Q1: 関係性
    print("\n" + "=" * 70)
    relationship = select_option(
        "Q1: 牡丹との関係は？",
        ["姉妹（妹）", "友達", "姪っ子", "後輩"],
        allow_custom=True
    )

    # Q2: 呼び方
    print("\n" + "=" * 70)
    nickname_options = {
        "姉妹（妹）": ["お兄ちゃん", "お姉ちゃん"],
        "友達": ["名前で呼ぶ", "あだ名で呼ぶ"],
        "姪っ子": ["おじさん", "おばさん", "叔父さん", "叔母さん"],
        "後輩": ["先輩", "◯◯先輩"]
    }

    default_nickname = nickname_options.get(relationship, ["名前で呼ぶ"])

    print(f"📝 Q2: 牡丹にどう呼ばれたい？")
    print(f"  （関係性: {relationship}）")

    if relationship in nickname_options:
        print(f"  おすすめ: {', '.join(default_nickname)}")

    nickname = input_text("呼び方を入力", default_nickname[0] if default_nickname else None)

    # Q3: 性格的特徴
    print("\n" + "=" * 70)
    personality_trait = select_option(
        "Q3: 牡丹の性格的特徴は？",
        ["明るく元気（デフォルト）", "おっとり癒し系", "ツンデレ", "クール"],
        allow_custom=True
    )

    # Q4: 背景設定（オプション）
    print("\n" + "=" * 70)
    print("📝 Q4: 背景設定を追加しますか？（オプション）")
    print("  例: 帰国子女、バイリンガル、配信者、学生など")
    background = input_text("背景設定（なしの場合はEnter）", "なし")

    # 確認
    print("\n" + "=" * 70)
    print("📋 設定内容の確認")
    print("=" * 70)
    print(f"関係性: {relationship}")
    print(f"呼び方: {nickname}")
    print(f"性格: {personality_trait}")
    print(f"背景: {background}")
    print()

    confirm = input("この設定でよろしいですか？ (y/n): ").strip().lower()

    if confirm != 'y':
        print("\n❌ セットアップを中止しました。")
        return

    # Append生成
    print("\n🔨 あなたの牡丹を生成中...")
    append = generate_append(relationship, nickname, personality_trait, background)

    # Modelfile作成
    modelfile_content = create_modelfile_with_append(append)

    if not modelfile_content:
        print("❌ Modelfile生成に失敗しました。")
        return

    # モデル作成
    model_name = save_modelfile(modelfile_content, "elyza:botan_custom")

    if not model_name:
        print("❌ モデル作成に失敗しました。")
        return

    # 設定保存
    save_append_config(relationship, nickname, personality_trait, background)

    # 完了メッセージ
    print("\n" + "=" * 70)
    print("🎉 セットアップ完了！")
    print("=" * 70)
    print()
    print(f"✅ あなたの牡丹が誕生しました！")
    print(f"✅ モデル名: {model_name}")
    print()
    print("次のコマンドで牡丹と会話できます：")
    print(f"  ollama run {model_name}")
    print()
    print("または学習型チャットを使用：")
    print(f"  python3 chat_with_learning.py")
    print(f"  （モデル名を '{model_name}' に変更してください）")
    print()
    print("=" * 70)
    print("🌱 これから育てていきましょう！")
    print("=" * 70)

if __name__ == "__main__":
    main()
