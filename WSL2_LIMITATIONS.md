# WSL2環境での制約事項

**更新日**: 2025-10-06

---

## 音声機能の制約

### 1. フィラー音声（pygame.mixer.Sound）

**問題**: WSL2環境でフィラー音声が再生されない

**原因**:
- `pygame.mixer.Sound` がWSL2のPulseAudio経由で正常動作しない
- Sound再生時にブロッキングまたは無音になる
- `pygame.mixer.music` は正常動作（メイン音声は問題なし）

**技術的背景**:
```
Windows環境:
  pygame.mixer.Sound → Windows Audio → 正常再生 ✅

WSL2環境:
  pygame.mixer.Sound → PulseAudio → /mnt/wslg/PulseServer → 問題発生 ❌
```

**対応**:
- WSL2環境ではフィラー音声を**無効化**
- 視覚的インジケーター（🤔）のみ表示
- Windows PowerShell環境では正常動作

**コード実装**:
```python
if self.voice_system.is_wsl:
    print("   🤔 ", end="", flush=True)  # WSL2: 音声なし
else:
    filler_sound = pygame.mixer.Sound(filler_path)
    filler_channel = filler_sound.play(loops=-1)  # Windows: 音声あり
```

---

### 2. 音声バッファサイズ

**問題**: 長いセリフで音切れが発生

**解決済み**: バッファサイズを環境別に最適化

| 環境 | バッファサイズ | レイテンシー |
|------|--------------|-------------|
| Windows | 2048サンプル | 46.4ms |
| WSL2 | 4096サンプル | 92.9ms |

詳細: `AUDIO_BUFFER_ANALYSIS.md` 参照

---

## 機能比較表

| 機能 | Windows PowerShell | WSL2 |
|------|-------------------|------|
| メイン音声再生 | ✅ 完全対応 | ✅ 完全対応 |
| フィラー音声 | ✅ 再生可能 | ❌ 無効化 |
| 音声生成速度 | ⚡ 高速 | ⚡ 高速 |
| バッファ安定性 | ✅ 安定 | ✅ 安定（4096） |
| 反射＋推論 | ✅ 完全対応 | ✅ 完全対応 |

---

## 推奨環境

### 最高のユーザー体験

**Windows PowerShell + 音声 + 反射＋推論**
- フィラー音声: ✅ あり
- メイン音声: ✅ 高品質
- 応答品質: ✅ 最高

### WSL2での最適設定

**WSL2 + 音声 + 反射＋推論**
- フィラー音声: ❌ なし（視覚的インジケーターのみ）
- メイン音声: ✅ 高品質
- 応答品質: ✅ 最高

---

## 回避策

### フィラー音声をWSL2で実現する方法（将来的）

1. **外部音声プレーヤーの使用**
   ```bash
   sudo apt install mpg123
   mpg123 -q filler.mp3 &
   ```

2. **テキスト読み上げの代替**
   ```bash
   espeak "えーっとね" &
   ```

3. **音声ファイルの事前合成**
   - フィラー + メイン音声を結合
   - 1つのファイルとして再生

---

## まとめ

**WSL2での制約**:
- フィラー音声が技術的に制限される
- メイン音声は完全に動作
- 視覚的フィードバックで代替

**推奨**:
- フィラー音声が必要: Windows PowerShell環境を使用
- WSL2環境: メイン音声のみで十分高品質な体験

**将来的な改善**:
- WSL2でのSound再生問題の調査継続
- 代替実装の検討（外部プレーヤーなど）
