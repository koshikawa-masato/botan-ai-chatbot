# WSL2音声バッファ問題の分析と解決

**報告日**: 2025-10-06
**問題**: WSL2環境で長いセリフの音声再生時にバッファオーバーフローが発生

---

## 問題の症状

### 発生条件
- ✅ WSL2環境で発生
- ❌ Windows PowerShell環境では発生しない
- 📝 長いセリフ（10秒以上）で顕著

### 具体的な症状
- 音声生成に時間がかかる
- 会話の途中で音声バッファがあふれる
- 音が途切れる、おかしくなる

---

## 根本原因の分析

### 1. **オーディオアーキテクチャの違い**

#### Windows PowerShell (ネイティブ実行)
```
Python → pygame → SDL2 → Windows Audio API
                            ↓
                      直接オーディオデバイス
```
- **遅延**: 低い（5-10ms）
- **バッファリング**: シンプル
- **問題**: なし

#### WSL2環境
```
Python → pygame → SDL2 → PulseAudio → /mnt/wslg/PulseServer
                                        ↓
                                  Windows Audio API
                                        ↓
                                  オーディオデバイス
```
- **遅延**: 高い（30-100ms以上）
- **バッファリング**: 多段階
- **問題**: 小さいバッファでアンダーラン発生

### 2. **バッファサイズの問題**

**改善前の設定:**
```python
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
```

- バッファサイズ: **512サンプル**
- レイテンシー: **11.6ms** (512 / 44100 * 1000)
- WSL2での問題: PulseAudio経由の遅延に対して小さすぎる

**音声ファイルサイズ:**
- 短いセリフ: 37KB (約2秒)
- 長いセリフ: 226KB (約10-15秒)

### 3. **なぜWindows PowerShellでは起こらないのか**

| 項目 | Windows PowerShell | WSL2 |
|------|-------------------|------|
| オーディオ経路 | 直接アクセス | PulseAudio経由 |
| 遅延 | 5-10ms | 30-100ms+ |
| バッファ要件 | 小さくてOK | 大きい必要 |
| カーネル | Windows NT | Linux (WSL2) |
| オーディオAPI | Windows Audio | ALSA/PulseAudio |

**Windows環境の優位性:**
- ネイティブWindows AudioAPIへの直接アクセス
- カーネルレベルでの最適化
- 低レイテンシー保証

**WSL2の制約:**
- Linux → Windows のクロスボーダー通信
- PulseAudioサーバー経由の追加オーバーヘッド
- ネットワークソケット経由のオーディオ転送

---

## 解決策

### 実装した改善

#### 1. **環境検出とバッファサイズの動的調整**

```python
def _is_wsl_environment(self):
    """Check if running in WSL2 environment"""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except:
        return False

# バッファサイズの動的設定
buffer_size = 4096 if self.is_wsl else 2048
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=buffer_size)
```

**バッファサイズ比較:**

| 環境 | バッファ (改善前) | バッファ (改善後) | レイテンシー |
|------|-----------------|-----------------|-------------|
| Native | 512 samples | 2048 samples | 46.4ms |
| WSL2 | 512 samples | **4096 samples** | **92.9ms** |

**改善効果:**
- WSL2でのバッファ: **8倍に増加** (512 → 4096)
- レイテンシー: 11.6ms → 92.9ms (許容範囲)
- バッファアンダーラン: **解消**

#### 2. **前の音声完了待機**

```python
def play_audio_async(self, audio_path: str):
    # Wait for previous playback to complete (prevent buffer overflow)
    if self.is_playing and self.playback_thread and self.playback_thread.is_alive():
        # In WSL2, ensure previous audio fully completes before starting new one
        self.playback_thread.join(timeout=30.0)  # Wait up to 30s for long audio

    # Start new playback thread
    self.is_playing = True
    self.playback_thread = threading.Thread(...)
    self.playback_thread.start()
```

**効果:**
- 前の音声が完全に終了してから次を再生
- バッファの衝突を防止
- 長いセリフ（15秒以上）でも安定

---

## 技術的詳細

### PulseAudioのオーバーヘッド

WSL2では、`/mnt/wslg/PulseServer` 経由でWindows Audioにアクセス:

```bash
$ echo $PULSE_SERVER
/mnt/wslg/PulseServer

$ ls -l /mnt/wslg/PulseServer
srw-rw-rw- 1 root root 0 Oct  6 15:30 /mnt/wslg/PulseServer
```

このソケット経由の通信が追加遅延を生む。

### バッファ計算

**レイテンシー計算式:**
```
レイテンシー(ms) = (バッファサイズ / サンプリングレート) * 1000
```

**例:**
- 512サンプル @ 44100Hz = 11.6ms
- 4096サンプル @ 44100Hz = 92.9ms

**WSL2での推奨値:**
- 最小: 2048サンプル (46.4ms)
- 推奨: **4096サンプル** (92.9ms)
- 長い音声: 8192サンプル (185.8ms)

---

## 検証結果

### テスト環境
- OS: WSL2 (Linux 6.6.87.2-microsoft-standard-WSL2)
- Python: 3.12.3
- pygame: 2.6.1
- SDL: 2.28.4

### テストケース

| セリフ長 | ファイルサイズ | 改善前 | 改善後 |
|---------|-------------|--------|--------|
| 短い (2秒) | 37KB | ✅ OK | ✅ OK |
| 中程度 (5秒) | 79KB | ⚠️ 時々途切れ | ✅ OK |
| 長い (10秒) | 156KB | ❌ 途切れる | ✅ OK |
| 最長 (15秒) | 226KB | ❌ 大きく途切れる | ✅ OK |

### パフォーマンス影響

**レイテンシー増加:**
- 改善前: 11.6ms
- 改善後: 92.9ms
- 差分: **+81.3ms**

**体感への影響:**
- 人間の音声知覚閾値: 約50-100ms
- 92.9msは**許容範囲内**
- 音質の安定性 > わずかな遅延

---

## 今後の改善案

### 1. **ストリーミング再生の実装**
現在は全ファイルをダウンロード後に再生。
将来的にはチャンク単位でストリーミング再生を検討。

### 2. **音声分割**
15秒以上の長いセリフを複数の短いチャンクに分割。

### 3. **キャッシュの事前ロード**
頻出フレーズは事前にメモリにロード。

### 4. **WSL2専用の最適化**
- PulseAudioの設定チューニング
- より大きいバッファ（8192サンプル）の検討

---

## まとめ

### 問題の本質
WSL2のPulseAudio → Windows Audio経由の遅延に対し、
小さいバッファサイズ（512サンプル）が不適切だった。

### 解決方法
- **環境検出**: WSL2を自動検出
- **動的バッファ調整**: 4096サンプルに増加（8倍）
- **再生同期**: 前の音声完了を待機

### 効果
- ✅ 長いセリフでも音切れなし
- ✅ バッファオーバーフロー解消
- ✅ Windows環境との互換性維持
- ⚠️ レイテンシー増加（+81ms、許容範囲）

### Windows vs WSL2 比較

| 項目 | Windows PowerShell | WSL2 |
|------|-------------------|------|
| バッファサイズ | 2048 | 4096 |
| レイテンシー | 46.4ms | 92.9ms |
| 音質 | 完璧 | 完璧 |
| 長いセリフ | 問題なし | **改善後: 問題なし** |

---

**結論**: WSL2環境特有のオーディオアーキテクチャに適応したバッファ設定により、
Windows PowerShellと同等の音声品質を実現。
