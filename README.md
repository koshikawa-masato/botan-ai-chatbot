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
4. ✅ 音声合成の実装（ElevenLabs v3統合）
5. ✅ Docker化＋API化（FastAPI + マイクロサービス）
6. ✅ OBS Browser Source字幕連携（Phase 2.1-A完了）
7. ✅ WebUI統合（ブラウザチャット）
8. 🚧 音声認識・配信システム統合（次フェーズ）

このリポジトリでは、**AIキャラクターとしての牡丹の基礎**を作り上げ、ユーザーごとにカスタマイズ可能な「うちの牡丹」を育成できるシステムを提供します。

---

## 📋 前提条件

### 必須環境
- Python 3.8以上
- [Ollama](https://ollama.ai/) インストール済み
- ELYZA日本語モデル `elyza:jp8b`
- **GPU推奨** (NVIDIA CUDA対応 / Apple Silicon)

### 音声合成機能（オプション）
- ElevenLabs APIキー（[elevenlabs.io](https://elevenlabs.io/)で取得）
- pygame（音声再生用）
- 環境: Windows PowerShell推奨（WSL2は一部機能に制限あり）

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

### 🐳 Docker版（推奨）

```bash
# 1. Ollamaモデル作成
cd scripts
python3 setup_botan.py

# 2. 環境変数設定
cp .env.example .env
# .envを編集してELEVENLABS_API_KEYを設定

# 3. Docker起動
docker compose up -d

# 4. WebUIでチャット
http://localhost:8000
```

#### 📺 OBS Studio連携（字幕表示）

```bash
# OBS Studio - Browser Source設定
URL: http://localhost:8000/static/obs/subtitle.html
幅: 1920
高さ: 1080
```

WebUIでチャットした内容が、OBS配信画面に字幕として表示されます。

**提供機能:**
- 🌐 **WebUI**: ブラウザでリアルタイムチャット
- 🎬 **OBS字幕**: 配信画面に透過字幕表示
- 🔊 **音声合成**: ElevenLabs v3統合（273倍高速キャッシュ）
- ⚡ **WebSocket**: リアルタイム双方向通信

詳細は以下を参照:
- [DOCKER_TEST_REPORT.md](DOCKER_TEST_REPORT.md) - システム概要
- [WEBUI_GUIDE.md](WEBUI_GUIDE.md) - WebUI利用ガイド
- [OBS_SETUP_GUIDE.md](OBS_SETUP_GUIDE.md) - OBS設定手順

---

### ローカル実行版

#### 1. チュートリアルで「うちの牡丹」を作成

```bash
cd scripts
python3 setup_botan.py
```

質問に答えるだけで、あなた専用の牡丹が誕生します。

- 関係性（姉妹、友達、姪っ子、後輩など）
- 呼び方（お兄ちゃん、おじさん、先輩など）
- 性格（明るく元気、おっとり、ツンデレなど）
- 背景設定（帰国子女、配信者など）

#### 2. 牡丹と会話

```bash
# Ollama直接実行
ollama run elyza:botan_custom

# または学習型チャット（推奨）
cd scripts
python3 chat_with_learning.py
```

学習型チャットでは:
- 会話履歴が自動保存
- AI自己評価 + ユーザーリアクション評価
- 会話統計の表示

#### 3. 音声合成を有効にする（オプション）

```bash
# .envファイルを作成（ルートディレクトリ）
cp .env.example .env
# .envにElevenLabs APIキーを設定

# 音声合成有効で実行
cd scripts
python3 chat_with_learning.py --voice

# 音声＋反射推論システムを有効にする
python3 chat_with_learning.py --voice --reflection
```

詳細は [docs/VOICE_SETUP.md](docs/VOICE_SETUP.md) を参照してください。

---

## 📁 ファイル構成

```
.
├── api/                            # API Gateway
│   ├── main.py                     # FastAPI WebSocket統合
│   └── Dockerfile                  # APIコンテナ設定
├── services/                       # マイクロサービス
│   ├── core/                       # Core Service（Ollama統合）
│   │   ├── service.py
│   │   └── Dockerfile
│   └── voice/                      # Voice Service（音声合成）
│       ├── service.py
│       └── Dockerfile
├── static/                         # WebUI・OBS連携
│   ├── index.html                  # WebUIチャット画面
│   ├── chat.js                     # WebSocketクライアント
│   └── obs/                        # OBS Browser Source
│       ├── subtitle.html           # 字幕表示（透過背景）
│       ├── subtitle.css
│       └── subtitle.js
├── scripts/                        # 実行スクリプト
│   ├── setup_botan.py              # チュートリアルシステム
│   ├── chat_with_learning.py       # 学習型チャット（音声対応）
│   ├── elevenlabs_client.py        # ElevenLabs API クライアント
│   ├── voice_synthesis.py          # 音声合成システム
│   └── reflection_reasoning.py     # 反射＋推論システム
├── docs/                           # ドキュメント（従来版）
│   ├── TUTORIAL_SYSTEM.md
│   ├── VOICE_SETUP.md
│   └── ARCHITECTURE_ROADMAP.md
├── DOCKER_TEST_REPORT.md           # Docker化完了レポート
├── WEBUI_GUIDE.md                  # WebUI利用ガイド
├── OBS_SETUP_GUIDE.md              # OBS設定手順
├── VOICE_ARCHITECTURE.md           # 音声合成アーキテクチャ
├── PHASE2_COMPLETION_REPORT.md     # Phase 2完了レポート
├── docker-compose.yml              # Docker Compose設定
├── requirements.txt                # Pythonライブラリ依存
├── .env.example                    # 環境変数テンプレート
└── README.md                       # このファイル
```

### 実行後に生成されるファイル

```
├── Modelfile_botan_custom      # あなたの牡丹のModelfile
├── botan_append_config.json    # カスタマイズ設定
├── voice_cache/                # 音声キャッシュ（音声有効時）
├── filler_cache/               # フィラー音声（反射推論有効時）
├── data/learning_session_*.json # 会話履歴ログ
└── .env                        # 環境変数（API キーなど）
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

### 基本システム
- [docs/TUTORIAL_SYSTEM.md](docs/TUTORIAL_SYSTEM.md) - チュートリアルシステムの詳細
- [docs/REACTION_EVALUATION_README.md](docs/REACTION_EVALUATION_README.md) - 評価システムの詳細

### 音声合成
- [docs/VOICE_SETUP.md](docs/VOICE_SETUP.md) - 音声合成セットアップガイド
- [docs/VOICE_SYNTHESIS_ROADMAP.md](docs/VOICE_SYNTHESIS_ROADMAP.md) - 開発ロードマップ
- [docs/WSL2_LIMITATIONS.md](docs/WSL2_LIMITATIONS.md) - WSL2環境の制約

### 開発計画
- [docs/ARCHITECTURE_ROADMAP.md](docs/ARCHITECTURE_ROADMAP.md) - 次期アーキテクチャ（Docker + API）
- [docs/CHANGELOG.md](docs/CHANGELOG.md) - 変更履歴

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

### Phase 2: Docker化 + API化
次期バージョンでは、以下の実装を予定しています：

- **Docker Compose**: ワンコマンドで環境構築
- **FastAPI**: REST API + WebSocket サポート
- **マルチコンテナ**: AI処理・API・音声処理の分離
- **OBS統合**: WebSocket経由でのリアルタイム連携
- **外部API公開**: Discord/Slack/Webhookとの統合

詳細は [docs/ARCHITECTURE_ROADMAP.md](docs/ARCHITECTURE_ROADMAP.md) を参照してください。

### 反射+推論システム（実装済み）
CPU/GPU環境での快適な会話体験のため、以下の機能を実装：

- ✅ **反射+推論システム**: ユーザー入力の意図・感情分析と応答戦略の事前計画
- ✅ **フィラー音声**: 推論中に「えっとね〜」などの音声を再生（Windows環境のみ）
- ✅ **会話コンテキスト保持**: Ollama chat API による会話履歴の維持

`--reflection` オプションで有効化できます。

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
**バージョン**: 2.1.0 - Phase 2.1-A: OBS連携＋WebUI完了
**作成者**: Masato Koshikawa

---

## 🎉 最新アップデート（Phase 2.1-A）

### ✨ 新機能
- **WebUI統合**: ブラウザでリアルタイムチャット（`http://localhost:8000`）
- **OBS Browser Source字幕**: 配信画面に透過字幕表示
- **WebSocket二重配信**: チャット＋OBS同時配信
- **音声合成キャッシュ**: 273倍高速化（MD5ハッシュベース）

### 📊 テスト結果
- REST API: 4/4成功 ✅
- WebSocket: 5/5成功 ✅
- OBS WebSocket: 3/3成功 ✅
- **総合成功率: 100%**

詳細は [PHASE2_COMPLETION_REPORT.md](PHASE2_COMPLETION_REPORT.md) を参照してください。
