FROM python:3.11-slim

WORKDIR /app

# 依存関係をコピー
COPY requirements.txt .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY services/voice/ ./services/voice/
COPY scripts/elevenlabs_client.py ./scripts/

# 音声キャッシュディレクトリ作成
RUN mkdir -p /app/voice_cache

# 環境変数
ENV PYTHONUNBUFFERED=1

# ポート公開
EXPOSE 8002

# 起動コマンド
CMD ["python", "-m", "uvicorn", "services.voice.service:app", "--host", "0.0.0.0", "--port", "8002"]
