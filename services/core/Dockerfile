FROM python:3.11-slim

WORKDIR /app

# 依存関係をコピー
COPY requirements.txt .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY services/core/ ./services/core/
COPY scripts/ ./scripts/

# 環境変数
ENV PYTHONUNBUFFERED=1

# ポート公開
EXPOSE 8001

# 起動コマンド
CMD ["python", "-m", "uvicorn", "services.core.service:app", "--host", "0.0.0.0", "--port", "8001"]
