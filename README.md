# 牡丹 (Botan) - うちの牡丹システム

17歳JKギャルAIチャットボット「牡丹」のカスタマイズ＆育成システム

## 📋 前提条件

### 必須環境
- Python 3.8以上
- [Ollama](https://ollama.ai/) インストール済み
- ELYZA日本語モデル `elyza:jp8b`

### ELYZAモデルのインストール

```bash
# Ollamaが起動していることを確認
ollama list

# ELYZA日本語モデルをダウンロード
ollama pull elyza:jp8b
```

### Pythonライブラリのインストール

```bash
pip install -r requirements.txt
```

---

## 🚀 クイックスタート

### 1. チュートリアルで「うちの牡丹」を作成

```bash
python3 setup_botan.py
```

質問に答えるだけで、あなた専用の牡丹が誕生します。

- 関係性（姉妹、友達、姪っ子、後輩など）
- 呼び方（お兄ちゃん、おじさん、先輩など）
- 性格（明るく元気、おっとり、ツンデレなど）
- 背景設定（帰国子女、配信者など）

### 2. 牡丹と会話

```bash
# Ollama直接実行
ollama run elyza:botan_custom

# または学習型チャット（推奨）
python3 chat_with_learning.py
```

学習型チャットでは:
- 会話履歴が自動保存
- AI自己評価 + ユーザーリアクション評価
- 会話統計の表示

---

## 📁 ファイル構成

```
.
├── Modelfile_botan_basic       # Basic版（17歳JKギャル）
├── setup_botan.py              # チュートリアルシステム
├── chat_with_learning.py       # 学習型チャット
├── auto_evaluate_botan.py      # AI自己評価システム
├── user_reaction_analyzer.py   # ユーザーリアクション分析
├── TUTORIAL_SYSTEM.md          # チュートリアル詳細ドキュメント
├── REACTION_EVALUATION_README.md # 評価システム詳細
├── requirements.txt            # Pythonライブラリ依存
└── README.md                   # このファイル
```

### 実行後に生成されるファイル

```
├── Modelfile_botan_custom      # あなたの牡丹のModelfile
├── botan_append_config.json    # カスタマイズ設定
└── learning_session_*.json     # 会話履歴ログ
```

---

## 🎨 カスタマイズ例

### パターン1: 妹キャラ
```
関係性: 姉妹（妹）
呼び方: お兄ちゃん
性格: ツンデレ
背景: なし
```

### パターン2: 友達キャラ
```
関係性: 友達
呼び方: あだ名（例：タロー）
性格: 明るく元気
背景: なし
```

### パターン3: 姪っ子キャラ（開発版）
```
関係性: 姪っ子
呼び方: オジサン
性格: 明るく元気
背景: 帰国子女、配信者
```

---

## 🌱 育成の仕組み

### Basic + Append アーキテクチャ

```
Basic（17歳JKギャル）
  +
Append（あなたのカスタマイズ）
  =
あなたの牡丹
```

- **Basic**: すべての牡丹に共通の基礎設定
- **Append**: ユーザーごとに異なるカスタマイズ

### 学習システム

会話を重ねるごとに:
- AI自己評価: キャラ設定への準拠度
- ユーザーリアクション評価: 実際の会話の盛り上がり
- 両方の評価を組み合わせて総合スコア算出
- 会話履歴として蓄積

---

## 🔧 トラブルシューティング

### `ollama: command not found`
Ollamaがインストールされていません。[公式サイト](https://ollama.ai/)からインストールしてください。

### `elyza:jp8b` が見つからない
```bash
ollama pull elyza:jp8b
```

### モデル作成に失敗する
```bash
# Ollamaが起動しているか確認
ollama list

# Basic版が存在するか確認
ls Modelfile_botan_basic
```

### 設定をやり直したい
```bash
# もう一度チュートリアルを実行（上書きされます）
python3 setup_botan.py
```

---

## 📚 詳細ドキュメント

- [TUTORIAL_SYSTEM.md](TUTORIAL_SYSTEM.md) - チュートリアルシステムの詳細
- [REACTION_EVALUATION_README.md](REACTION_EVALUATION_README.md) - 評価システムの詳細

---

## 💡 設計思想

### 「うちの牡丹」コンセプト

従来のAIチャットボット:
- すべてのユーザーが同じAIと会話
- カスタマイズ性なし
- 「道具」として使う

牡丹の目指すもの:
- ユーザーごとに異なる牡丹
- 初回セットアップで関係性を定義
- 会話を重ねて個性が育つ
- 「相手」として接する

**これが「うちの牡丹」システムの核心**

---

## 📄 ライセンス

### ソフトウェアライセンス
このプロジェクトのコードはMITライセンスの下で公開されています。
詳細は[LICENSE](LICENSE)ファイルを参照してください。

### 使用モデルのライセンス

**ELYZA Llama-3-ELYZA-JP-8B**
- ライセンス: [Meta Llama 3 Community License](https://llama.meta.com/llama3/license/)
- モデルURL: [huggingface.co/elyza/Llama-3-ELYZA-JP-8B](https://huggingface.co/elyza/Llama-3-ELYZA-JP-8B)
- 開発元: ELYZA, Inc.

このソフトウェアを使用する際は、Meta Llama 3 Community LicenseおよびAcceptable Use Policyに従う必要があります。

---

**作成日**: 2025-10-06
**バージョン**: 1.0
**作成者**: Masato Koshikawa
