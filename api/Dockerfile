FROM python:3.11-slim

WORKDIR /app

# 依存関係をコピー
COPY requirements.txt .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY api/ ./api/
COPY scripts/ ./scripts/

# 環境変数
ENV PYTHONUNBUFFERED=1

# ポート公開
EXPOSE 8000

# 起動コマンド
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
