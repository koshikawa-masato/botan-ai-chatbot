# Docker Setup Guide - 牡丹 AI システム

**Phase 2.0: Docker化完了**

Docker Composeでワンコマンド起動が可能です。

---

## 📋 前提条件

### 必須
- Docker Desktop または Docker Engine (20.10+)
- Docker Compose (v2.0+)
- **Ollama** (ホストマシンで起動)
  - WSL2/Linux: `ollama serve`
  - macOS: Ollamaアプリ起動済み
  - Windows: Ollamaサービス起動済み
- ElevenLabs APIキー（音声合成使用時）

### 推奨
- GPU対応環境（NVIDIA CUDA / Apple Silicon）
- メモリ 8GB以上

---

## 🚀 クイックスタート

### 1. Ollamaモデルの準備

```bash
# Ollamaが起動していることを確認
ollama list

# ELYZAモデルをpull（まだの場合）
ollama pull elyza:jp8b

# カスタムモデル作成（まだの場合）
cd scripts
python3 setup_botan.py
```

### 2. 環境変数の設定

```bash
# .envファイルを作成
cp .env.example .env

# .envを編集してAPI keyを設定
# ELEVENLABS_API_KEY=your_api_key_here
```

### 3. Docker起動

```bash
# ビルド & 起動
docker-compose up -d

# ログ確認
docker-compose logs -f

# 停止
docker-compose down
```

---

## 🏗️ アーキテクチャ

### サービス構成

```
┌─────────────────────────────────┐
│     http://localhost:8000       │
│       API Gateway               │
│   - REST API                    │
│   - WebSocket                   │
└───────────┬─────────────────────┘
            │
    ┌───────┴────────┐
    ↓                ↓
┌─────────┐    ┌──────────────┐
│ Core    │    │ Voice        │
│ :8001   │    │ :8002        │
│         │    │              │
│ Ollama  │    │ ElevenLabs   │
│ 連携    │    │ 音声合成     │
└─────────┘    └──────────────┘
    │
    ↓
┌─────────────────┐
│ Ollama (Host)   │
│ :11434          │
└─────────────────┘
```

### ポート

| サービス | ポート | 説明 |
|---------|--------|------|
| API Gateway | 8000 | メインAPIエンドポイント |
| Core Service | 8001 | Ollama連携・会話処理 |
| Voice Service | 8002 | ElevenLabs音声合成 |
| Ollama (Host) | 11434 | LLMエンジン |

---

## 📡 API エンドポイント

### REST API

#### チャット
```bash
# POST /api/chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "やっほー！",
    "user_id": "user1",
    "enable_voice": true,
    "enable_reflection": false
  }'
```

#### ヘルスチェック
```bash
# GET /health
curl http://localhost:8000/health
```

#### 設定取得
```bash
# GET /api/config
curl http://localhost:8000/api/config
```

### WebSocket

```javascript
// JavaScript example
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "こんにちは！",
    timestamp: Date.now()
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Response:', data.response);
  console.log('Audio:', data.audio_url);
};
```

---

## 🔧 設定

### 環境変数 (.env)

```bash
# ElevenLabs API
ELEVENLABS_API_KEY=your_api_key
ELEVENLABS_VOICE_ID=pFZP5JQG7iQjIQuC4Bku
ELEVENLABS_MODEL=eleven_multilingual_v2

# Ollama (ホスト)
# OllamaはDocker外で起動している前提
# docker-compose.ymlでhost.docker.internalを使用
```

### カスタマイズ

`docker-compose.yml`を編集して設定変更：

```yaml
services:
  core:
    environment:
      - MODEL_NAME=elyza:your_custom_model  # カスタムモデル名
      - OLLAMA_HOST=http://your-ollama-host:11434
```

---

## 🐛 トラブルシューティング

### Ollamaに接続できない

```bash
# ホストのOllamaが起動しているか確認
ollama list

# Dockerコンテナからホストに接続できるか確認
docker-compose exec core curl http://host.docker.internal:11434/api/tags
```

**WSL2の場合:**
- `host.docker.internal` が動作しない場合は、ホストのIPアドレスを直接指定

```yaml
# docker-compose.yml
services:
  core:
    environment:
      - OLLAMA_HOST=http://172.x.x.x:11434  # ホストのIPアドレス
```

### 音声が生成されない

```bash
# Voice Serviceのログ確認
docker-compose logs voice

# ElevenLabs API keyが正しく設定されているか確認
docker-compose exec voice env | grep ELEVENLABS
```

### ポートが使用中

```bash
# 既存のプロセスを確認
lsof -i :8000
lsof -i :8001
lsof -i :8002

# docker-compose.ymlでポート変更
ports:
  - "18000:8000"  # ホスト側のポートを変更
```

---

## 🧪 開発モード

### ホットリロード有効化

```yaml
# docker-compose.dev.yml
services:
  api:
    volumes:
      - ./api:/app/api
      - ./scripts:/app/scripts
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

  core:
    volumes:
      - ./services/core:/app/services/core
      - ./scripts:/app/scripts
    command: uvicorn services.core.service:app --host 0.0.0.0 --port 8001 --reload
```

```bash
# 開発モードで起動
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### ログ確認

```bash
# 全サービス
docker-compose logs -f

# 特定サービス
docker-compose logs -f api
docker-compose logs -f core
docker-compose logs -f voice
```

---

## 🔄 更新・再ビルド

### コード更新時

```bash
# サービス再起動
docker-compose restart

# 再ビルド（Dockerfile変更時）
docker-compose up -d --build

# 特定サービスのみ再ビルド
docker-compose up -d --build api
```

### クリーンビルド

```bash
# 完全クリーン
docker-compose down -v  # ボリュームも削除
docker system prune -a  # 未使用イメージ削除
docker-compose up -d --build
```

---

## 📊 モニタリング

### リソース使用状況

```bash
# コンテナ統計
docker stats

# ディスク使用量
docker system df
```

### ヘルスチェック

```bash
# 各サービスの状態確認
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

---

## 🚀 本番環境デプロイ

### セキュリティ

1. **環境変数の保護**
   ```bash
   # .envファイルを.gitignoreに追加済み
   # 本番環境では環境変数を直接設定
   ```

2. **CORS設定**
   ```python
   # api/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],  # 本番ドメインに制限
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

3. **リバースプロキシ（Nginx）**
   ```yaml
   # docker-compose.prod.yml
   services:
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf:ro
         - ./ssl:/etc/nginx/ssl:ro
   ```

---

## 📝 次のステップ

- [ ] OBS Browser Source連携
- [ ] Discord Bot統合
- [ ] Webhook API
- [ ] データベース追加（会話履歴永続化）
- [ ] Prometheus/Grafana監視

詳細は [ARCHITECTURE_ROADMAP.md](ARCHITECTURE_ROADMAP.md) 参照

---

**作成日**: 2025-10-06
**Phase**: 2.0 - Docker化完了
