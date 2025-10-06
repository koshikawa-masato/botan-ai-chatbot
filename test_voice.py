#!/usr/bin/env python3
"""
Voice Service Test Script
音声合成機能のテスト
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"
VOICE_BASE = "http://localhost:8002"

def test_voice_health():
    """Voice Serviceのヘルスチェック"""
    print("\n=== Voice Service Health Check ===")
    response = requests.get(f"{VOICE_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200

def test_voice_stats():
    """Voice Serviceの統計情報"""
    print("\n=== Voice Service Stats ===")
    response = requests.get(f"{VOICE_BASE}/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200

def test_voice_synthesize_direct():
    """Voice Serviceに直接リクエスト"""
    print("\n=== Direct Voice Synthesis Test ===")

    test_text = "やっほー！オジサン！マジで元気？"
    print(f"Text: {test_text}")

    response = requests.post(
        f"{VOICE_BASE}/synthesize",
        json={
            "text": test_text,
            "filename": "test_direct.mp3"
        }
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")

        # 音声ファイル取得テスト
        filename = result.get("filename")
        if filename:
            print(f"\n音声ファイル取得中: {filename}")
            audio_response = requests.get(f"{VOICE_BASE}/audio/{filename}")
            print(f"Audio Status: {audio_response.status_code}")
            print(f"Audio Size: {len(audio_response.content)} bytes")

            # WSL環境なのでファイル保存のみ
            output_path = f"/tmp/{filename}"
            with open(output_path, "wb") as f:
                f.write(audio_response.content)
            print(f"Saved to: {output_path}")
            print("(WSL環境のため自動再生はできません)")

            return True
    else:
        print(f"Error: {response.text}")
        return False

def test_voice_through_api():
    """API Gateway経由で音声合成付きチャット"""
    print("\n=== Voice Chat through API Gateway ===")

    response = requests.post(
        f"{API_BASE}/api/chat",
        json={
            "message": "今日はいい天気だね！",
            "enable_voice": True,
            "enable_reflection": False
        }
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"\n牡丹: {result.get('response')}")

        if result.get('audio_url'):
            print(f"\n音声URL: {result.get('audio_url')}")

            # 音声ファイルダウンロード
            audio_url = result.get('audio_url')
            if audio_url.startswith('/'):
                # 相対URLを絶対URLに変換
                audio_url = f"{API_BASE}{audio_url}"

            audio_response = requests.get(audio_url)
            print(f"Audio Status: {audio_response.status_code}")
            print(f"Audio Size: {len(audio_response.content)} bytes")

            # ファイル保存
            output_path = f"/tmp/botan_chat_{int(time.time())}.mp3"
            with open(output_path, "wb") as f:
                f.write(audio_response.content)
            print(f"Saved to: {output_path}")

            return True
        else:
            print("Warning: No audio URL in response")
            return False
    else:
        print(f"Error: {response.text}")
        return False

def main():
    print("=" * 60)
    print("Botan Voice Service Test")
    print("=" * 60)

    results = {
        "health": test_voice_health(),
        "stats": test_voice_stats(),
        "direct_synthesis": test_voice_synthesize_direct(),
        "api_voice_chat": test_voice_through_api()
    }

    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s}: {status}")

    all_passed = all(results.values())
    print("\n" + ("✅ All tests passed!" if all_passed else "❌ Some tests failed"))
    print("=" * 60)

if __name__ == "__main__":
    main()
