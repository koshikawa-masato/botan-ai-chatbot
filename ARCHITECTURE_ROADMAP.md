# 牡丹AIシステム アーキテクチャロードマップ

**作成日**: 2025-10-06
**目的**: 環境依存を解消し、OBS連携・API化を見据えた設計方針

---

## 現状の課題

### 環境依存の問題

| 環境 | メリット | デメリット |
|------|---------|-----------|
| **Windows PowerShell** | フィラー音声動作 | 一部環境で導入困難、Pythonセットアップ複雑 |
| **WSL2** | Linux環境、開発しやすい | フィラー音声制限、PulseAudioの制約 |
| **Docker** | 環境統一、再現性高い | **未実装** |

### 将来の要件

1. **OBS連携**: 配信・録画での使用
2. **API化**: 外部サービスとの連携
3. **マルチプラットフォーム**: どこでも動く
4. **簡単導入**: `docker-compose up` で完了

---

## 推奨アーキテクチャ: マイクロサービス化

### Phase 2.0: サービス分離アーキテクチャ

```
┌─────────────────────────────────────────────────────┐
│                  OBS / ブラウザ                      │
│                  (フロントエンド)                     │
└────────────────────┬────────────────────────────────┘
                     │ WebSocket/HTTP
                     ↓
┌─────────────────────────────────────────────────────┐
│              API Gateway (FastAPI)                  │
│          - WebSocket Server                         │
│          - REST API                                 │
│          - CORS設定                                 │
└────┬───────────────┬───────────────┬────────────────┘
     │               │               │
     ↓               ↓               ↓
┌─────────┐    ┌─────────┐    ┌──────────────┐
│ Core    │    │ Voice   │    │ Evaluation   │
│ Service │    │ Service │    │ Service      │
│         │    │         │    │              │
│ Ollama  │    │ ElevenL │    │ Learning     │
│ ELYZA   │    │ abs     │    │ System       │
└─────────┘    └─────────┘    └──────────────┘
     │               │               │
     └───────────────┴───────────────┘
                     │
                     ↓
              ┌─────────────┐
              │  Database   │
              │  (SQLite/   │
              │   Postgres) │
              └─────────────┘
```

---

## 具体的な実装プラン

### Step 1: API化（Phase 2.1）

**優先度**: 最高

#### 1.1 FastAPI基盤構築

```python
# api_server.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS設定（OBS Browser Sourceから接続可能に）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    # リアルタイム会話処理
    ...

@app.post("/api/chat")
async def chat(message: str):
    # REST API
    return {"response": "..."}
```

#### 1.2 WebSocket実装

**メリット**:
- リアルタイムストリーミング応答
- OBSからブラウザ経由で接続
- テキスト・音声の同時配信

#### 1.3 OBS連携

```html
<!-- OBS Browser Source -->
<div id="botan-chat">
  <div id="avatar">牡丹</div>
  <div id="message"></div>
  <audio id="voice"></audio>
</div>

<script>
const ws = new WebSocket('ws://localhost:8000/ws/chat');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  document.getElementById('message').innerText = data.text;
  document.getElementById('voice').src = data.audio_url;
  document.getElementById('voice').play();
};
</script>
```

---

### Step 2: Docker化（Phase 2.2）

**優先度**: 高

#### 2.1 マルチコンテナ構成

```yaml
# docker-compose.yml
version: '3.8'

services:
  # コアAIサービス
  botan-core:
    build: ./core
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_HOST=http://ollama:11434
    depends_on:
      - ollama
      - voice-service

  # Ollama（LLMエンジン）
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama

  # 音声生成サービス
  voice-service:
    build: ./voice
    environment:
      - ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
    volumes:
      - voice-cache:/app/cache

  # データベース
  db:
    image: postgres:15
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  ollama-data:
  voice-cache:
  db-data:
```

#### 2.2 環境非依存を実現

**メリット**:
- WSL2/PowerShell/Macどこでも同じ動作
- フィラー音声問題を解消（コンテナ内で統一環境）
- `docker-compose up` で一発起動

---

### Step 3: OBS統合（Phase 2.3）

**優先度**: 中

#### 3.1 OBS Browser Source設定

```
URL: http://localhost:8000/obs/chat
Width: 1920
Height: 1080
CSS: custom-overlay.css
```

#### 3.2 配信用UI

```
┌─────────────────────────────┐
│   🌸 牡丹との配信チャット    │
├─────────────────────────────┤
│                             │
│  [牡丹のアバター]            │
│                             │
│  「やっほー！」              │
│  └─ 音声波形アニメーション    │
│                             │
│  [視聴者コメント]            │
│  └─ リアルタイム表示         │
│                             │
└─────────────────────────────┘
```

#### 3.3 配信用機能

- **テキストストリーミング**: 文字を1つずつ表示
- **音声同期**: 口パク・波形表示
- **リアクション**: 絵文字・エフェクト
- **チャット履歴**: 過去の会話を表示

---

### Step 4: 外部API連携（Phase 2.4）

**優先度**: 中

#### 4.1 REST API公開

```python
# 外部サービスから利用可能
POST /api/v1/chat
{
  "message": "こんにちは",
  "user_id": "user123",
  "voice": true
}

Response:
{
  "text": "やっほー！",
  "audio_url": "https://.../botan_voice.mp3",
  "emotion": "happy",
  "evaluation": {
    "score": 4.5
  }
}
```

#### 4.2 Webhook対応

```python
# Discord Bot連携
@bot.command()
async def botan(ctx, *, message):
    response = await call_botan_api(message)
    await ctx.send(response['text'])
    await ctx.send(file=discord.File(response['audio_url']))
```

---

## 環境別推奨

### 現在（Phase 1.x）

| 用途 | 推奨環境 | 理由 |
|------|---------|------|
| 開発 | WSL2 | Linux環境、開発ツール充実 |
| テスト | Windows PowerShell | フィラー音声含む全機能動作 |
| 配信 | **Docker推奨（未実装）** | 環境依存なし |

### 将来（Phase 2.x）

| 用途 | 推奨環境 | 理由 |
|------|---------|------|
| **すべて** | **Docker** | 統一環境、簡単導入 |
| OBS連携 | Docker + Browser Source | WebSocket接続 |
| API利用 | Docker（クラウド可） | スケーラブル |

---

## 実装優先順位

### フェーズ別タスク

#### Phase 2.1: API化（1-2週間）
```
□ FastAPI基盤構築
□ WebSocketサーバー実装
□ REST API設計
□ CORS設定
□ 既存機能のAPI化
  - 会話処理
  - 音声生成
  - 評価システム
```

#### Phase 2.2: Docker化（1-2週間）
```
□ Dockerfile作成（各サービス）
□ docker-compose.yml設計
□ 環境変数管理（.env統一）
□ ボリューム設定（永続化）
□ ネットワーク設定
□ ドキュメント整備
```

#### Phase 2.3: OBS統合（1週間）
```
□ Browser Source用HTML/CSS/JS
□ WebSocket接続実装
□ リアルタイム表示
□ 音声同期
□ アニメーション実装
```

#### Phase 2.4: 外部連携（1週間）
```
□ REST API v1公開
□ 認証・レート制限
□ Webhook実装
□ ドキュメント（OpenAPI）
```

---

## 技術スタック（Phase 2.x）

### バックエンド
- **FastAPI**: API Server
- **WebSocket**: リアルタイム通信
- **Ollama**: LLMエンジン
- **ElevenLabs**: 音声合成
- **PostgreSQL**: データベース（学習データ）

### フロントエンド（OBS用）
- **HTML5/CSS3/JavaScript**: Browser Source
- **WebSocket Client**: リアルタイム接続
- **Howler.js**: 音声再生
- **Anime.js**: アニメーション

### インフラ
- **Docker/Docker Compose**: コンテナ化
- **Nginx**: リバースプロキシ（オプション）
- **Let's Encrypt**: SSL（外部公開時）

---

## 移行戦略

### 段階的移行

#### ステージ1: 互換性維持
```
現行システム（Phase 1.x）
  ↓ 並行稼働
新システム（Phase 2.x - Docker）
```
- 既存のスクリプトは動作継続
- 新機能はDocker版で追加

#### ステージ2: API移行
```
chat_with_learning.py → API Client化
  ↓
Docker API Server
```
- CLIツールはAPIクライアントに
- ロジックはサーバー側に集約

#### ステージ3: 完全移行
```
すべての機能 → Docker化
```
- CLIもコンテナ内で実行
- 環境依存完全解消

---

## 結論と推奨

### 短期（1-2ヶ月）

**推奨**: Docker化 + API化を優先

1. ✅ **Phase 2.1**: FastAPI基盤構築
   - WebSocketサーバー
   - REST API
   - 既存機能のAPI化

2. ✅ **Phase 2.2**: Docker化
   - マルチコンテナ構成
   - 環境非依存
   - 簡単導入（`docker-compose up`）

### 中期（3-6ヶ月）

**推奨**: OBS連携 + 外部API公開

3. ✅ **Phase 2.3**: OBS統合
   - Browser Source対応
   - リアルタイム配信

4. ✅ **Phase 2.4**: 外部連携
   - REST API公開
   - Discord/Slack連携

### 長期（6ヶ月以降）

**推奨**: マルチモーダル化

5. **Phase 3.x**: AI Vtuber完全版
   - Live2D/3Dアバター
   - 表情・リップシンク
   - ジェスチャー生成

---

## 即座に着手すべきこと

### Next Step（今週中）

```bash
# 1. FastAPI基盤を作成
mkdir -p api/{core,voice,evaluation}

# 2. docker-compose.yml 設計
touch docker-compose.yml

# 3. API設計ドキュメント作成
touch API_DESIGN.md
```

### 最初のマイルストーン

**目標**: Docker化されたAPI版牡丹（Phase 2.1 + 2.2）

**成果物**:
- `docker-compose up` で起動
- WebSocket経由で会話可能
- REST APIで外部連携可能
- 環境依存なし

**期間**: 2-3週間

---

## まとめ

### 現在の推奨

- **開発**: WSL2（制約を理解して使用）
- **全機能テスト**: Windows PowerShell

### 将来の推奨（Phase 2.x以降）

- **すべて**: **Docker**
- **配信**: Docker + OBS
- **外部連携**: Docker（API Server）

### 次のアクション

1. ✅ **Phase 2.1開始**: FastAPI基盤構築
2. ✅ **Docker設計**: マルチコンテナ構成
3. ✅ **API設計**: WebSocket + REST

**この方向性で進めることをお勧めします。**
