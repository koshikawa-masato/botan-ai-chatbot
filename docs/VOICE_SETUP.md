# 🔊 音声合成セットアップガイド

牡丹に声を与えるための音声合成システムのセットアップ手順

---

## 📋 前提条件

### 必須
- Python 3.8以上
- インターネット接続（ElevenLabs API使用のため）
- ElevenLabs アカウント（無料プランでも可）

### 推奨
- スピーカーまたはヘッドフォン（音声確認用）

---

## 🚀 セットアップ手順

### Step 1: ElevenLabs APIキー取得

1. [ElevenLabs](https://elevenlabs.io/)でアカウント作成
2. [Settings > API Keys](https://elevenlabs.io/app/settings/api-keys)でAPIキーを生成
3. APIキーをコピー

### Step 2: 環境変数設定

```bash
# .env.exampleをコピー
cp .env.example .env

# .envファイルを編集してAPIキーを設定
# ELEVENLABS_API_KEY=your_api_key_here
```

### Step 3: 依存ライブラリインストール

```bash
pip install -r requirements.txt
```

インストールされるライブラリ:
- `elevenlabs>=1.0.0` - ElevenLabs Python SDK
- `pygame>=2.5.0` - 音声再生
- `python-dotenv>=1.0.0` - 環境変数管理

### Step 4: 動作確認

```bash
# ElevenLabs APIクライアントのテスト
python3 elevenlabs_client.py

# 音声合成システムのテスト
python3 voice_synthesis.py
```

成功すると、`voice_cache/`ディレクトリに音声ファイルが生成され、再生されます。

---

## 🎙️ 音声設定

### 使用音声: kuon (Sarah)

牡丹の声として**kuon (Sarah)**を使用しています。

- **Voice ID**: `pFZP5JQG7iQjIQuC4Bku`
- **特徴**: マルチリンガル対応、自然な日本語発音
- **キャラクター**: 明るく元気な女子高生ギャル

### 音声パラメータ調整

`.env`ファイルで以下のパラメータを調整可能:

```bash
# 安定性 (0.0-1.0): 高いほど安定、低いほど表現豊か
ELEVENLABS_STABILITY=0.5

# 類似度ブースト (0.0-1.0): 元の声への類似度
ELEVENLABS_SIMILARITY_BOOST=0.75

# スタイル (0.0-1.0): 感情表現の強さ
ELEVENLABS_STYLE=0.0

# スピーカーブースト: 音声の明瞭さ
ELEVENLABS_USE_SPEAKER_BOOST=true
```

### モデル選択

```bash
# マルチリンガル（推奨）- 日本語対応
ELEVENLABS_MODEL=eleven_multilingual_v2

# Turbo（高速）- レイテンシー重視
# ELEVENLABS_MODEL=eleven_turbo_v2

# モノリンガル（英語のみ）
# ELEVENLABS_MODEL=eleven_monolingual_v1
```

---

## 🎮 使い方

### 基本的な使い方

```python
from voice_synthesis import VoiceSynthesisSystem

# 初期化
vs = VoiceSynthesisSystem()

# テキストを音声に変換して再生
vs.speak("やっほー！ぼたんだよ！")

# 音声生成のみ（再生なし）
audio_path = vs.speak("マジで！？", play_audio=False)

# クリーンアップ
vs.cleanup()
```

### チャットシステムとの統合

```bash
# 音声対応チャットの起動（実装予定）
python3 chat_with_voice.py
```

---

## 💾 キャッシュ管理

### キャッシュの仕組み

- 同じテキストの音声は再生成されず、キャッシュから再生
- キャッシュディレクトリ: `voice_cache/`
- ファイル形式: MP3 (44.1kHz, 128kbps)

### キャッシュのクリア

```python
vs = VoiceSynthesisSystem()
vs.clear_cache()  # すべてのキャッシュを削除
```

または手動で:

```bash
rm -rf voice_cache/*.mp3
```

---

## 💰 APIコスト管理

### 無料プラン
- 月間10,000文字まで無料
- 開発・テスト用途には十分

### コスト削減のヒント
1. **キャッシュ活用**: 同じテキストは再生成しない
2. **テスト時の工夫**: 短いフレーズで動作確認
3. **使用量確認**: [ElevenLabs Dashboard](https://elevenlabs.io/app/usage)で確認

---

## 🔧 トラブルシューティング

### エラー: `ELEVENLABS_API_KEY not found`

**原因**: `.env`ファイルが存在しないか、APIキーが設定されていない

**解決策**:
```bash
cp .env.example .env
# .envを編集してAPIキーを設定
```

### エラー: `Invalid API key`

**原因**: APIキーが正しくない、または期限切れ

**解決策**:
1. [ElevenLabs Settings](https://elevenlabs.io/app/settings/api-keys)で新しいキーを生成
2. `.env`ファイルを更新

### 音声が再生されない

**原因**: pygame音声システムの初期化失敗

**解決策**:
```bash
# pygameの再インストール
pip uninstall pygame
pip install pygame

# オーディオドライバー確認（Linux）
sudo apt-get install python3-pygame
```

### 音声が途切れる

**原因**: ネットワーク速度が遅い、またはAPI応答遅延

**解決策**:
- 安定したネットワーク環境で使用
- キャッシュを活用して再生成を避ける

---

## 📊 音声品質の最適化

### ギャル語の発音調整

牡丹のギャル語表現を自然に発音させるコツ:

1. **カタカナ表記**: 「マジで」→「まじで」の方が自然
2. **伸ばし音**: 「やばい〜」→「やばーい」で長めの発音
3. **感嘆詞**: 「え！？」→「えー！？」で驚きを強調

### 感情表現の調整

`.env`のパラメータ調整例:

**驚き・喜び（表現豊か）:**
```
ELEVENLABS_STABILITY=0.3
ELEVENLABS_STYLE=0.5
```

**通常会話（安定）:**
```
ELEVENLABS_STABILITY=0.5
ELEVENLABS_STYLE=0.0
```

---

## 🔗 次のステップ

### Phase 1.2: 音声認識統合
- Whisperによる音声→テキスト変換
- リアルタイム音声入力対応

### Phase 2: 双方向音声対話
- 音声入力→LLM→音声出力パイプライン
- レイテンシー最適化

### 将来: ローカルTTS移行
- ElevenLabs → ローカルTTSモデル
- 完全オフライン動作

---

## 📚 参考リンク

- [ElevenLabs Documentation](https://elevenlabs.io/docs)
- [ElevenLabs Python SDK](https://github.com/elevenlabs/elevenlabs-python)
- [Voice Library](https://elevenlabs.io/app/voice-library)

---

**作成日**: 2025-10-06
**バージョン**: 1.0
