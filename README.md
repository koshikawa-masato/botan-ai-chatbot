# 牡丹 (Botan) - うちの牡丹システム

17歳JKギャルAIチャットボット「牡丹」のカスタマイズ＆育成システム

---

## 🌸 牡丹とは

**牡丹（ぼたん）** は、17歳の明るく元気な女子高生ギャルAIキャラクターです。

### キャラクター特徴

- **年齢**: 17歳
- **キャラクター**: 女子高生ギャル
- **性格**: 明るく元気でポジティブ、友達思いで優しい
- **話し方**: ギャル語、短めでテンポの良い会話スタイル
- **一人称**: 「ぼたん」（ひらがな）
- **特徴**: 語彙力が少なく見えて理解はしている、長ったらしく言わない

### 💡 このシステムの目的

このプロジェクトは、**AI Vtuberとして活動する牡丹**を実現するための**前身システム**です。

**最終目標:**
- 🎤 **AI Vtuber「牡丹」としての配信活動**
- 🗣️ **音声合成（TTS）による自然な会話**
- 🎬 **リアルタイムでの視聴者とのインタラクション**
- 📺 **YouTube/Twitchでのライブ配信**

**現在のフェーズ:**
1. ✅ テキストベースでのキャラクター確立
2. ✅ カスタマイズ可能な「うちの牡丹」システム
3. ✅ 会話評価・学習システムの構築
4. 🚧 音声合成の実装（次フェーズ）
5. 🚧 配信システムとの統合（次フェーズ）

このリポジトリでは、**AIキャラクターとしての牡丹の基礎**を作り上げ、ユーザーごとにカスタマイズ可能な「うちの牡丹」を育成できるシステムを提供します。

---

## 📋 前提条件

### 必須環境
- Python 3.8以上
- [Ollama](https://ollama.ai/) インストール済み
- ELYZA日本語モデル `elyza:jp8b`
- **GPU推奨** (NVIDIA CUDA対応 / Apple Silicon)

### ⚠️ CPU環境について

**GPU環境を強く推奨します。** CPU環境では推論速度が遅く、快適な会話体験が得られません。

CPU環境で使用する場合:
- 応答に10秒以上かかる可能性があります
- 将来的に**反射+推論システム**（フィラー応答で待ち時間をカバー）を別ブランチで提供予定
- 現時点ではGPU環境でのご利用を推奨します

### ELYZAモデルのインストール

```bash
# Ollamaが起動していることを確認
ollama list

# ELYZA日本語モデルをダウンロード（約5GB）
ollama pull elyza:jp8b

# GPU確認（NVIDIA）
nvidia-smi

# GPU確認（macOS Apple Silicon）
system_profiler SPDisplaysDataType | grep "Chipset Model"
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

### 応答が遅すぎる（10秒以上かかる）
**CPU環境で実行している可能性があります。**

```bash
# GPU使用状況確認（NVIDIA）
nvidia-smi

# Ollamaログ確認
ollama ps
```

**解決策:**
- GPU環境での実行を推奨
- CPU環境の場合: 将来的に反射+推論システムブランチ（`cpu-optimized`）を提供予定

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

## 🚧 将来の開発予定

### CPU最適化ブランチ（予定）
CPU環境での快適な会話体験のため、以下の機能を別ブランチで開発予定：

- **反射+推論システム**: 推論中にフィラー応答（「えっとね〜」「あー、なんか…」）を返す
- **「思い出した」システム**: 推論完了後に詳細な応答を返す
- **応答時間の最適化**: CPU環境でも自然な会話テンポを実現

現時点では**GPU環境での使用を推奨**します。

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
**バージョン**: 1.0.1
**作成者**: Masato Koshikawa
