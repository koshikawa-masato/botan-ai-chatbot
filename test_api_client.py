#!/usr/bin/env python3
"""
Botan API Test Client
Docker APIのテスト用クライアント
"""

import requests
import json
import sys

API_BASE = "http://localhost:8000"

def test_health():
    """ヘルスチェック"""
    print("\n=== Health Check ===")
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_config():
    """設定取得"""
    print("\n=== Get Config ===")
    response = requests.get(f"{API_BASE}/api/config")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_chat(message: str, enable_voice: bool = False, enable_reflection: bool = False):
    """チャットテスト"""
    print(f"\n=== Chat Test ===")
    print(f"Message: {message}")
    print(f"Voice: {enable_voice}, Reflection: {enable_reflection}")

    payload = {
        "message": message,
        "user_id": "test_user",
        "enable_voice": enable_voice,
        "enable_reflection": enable_reflection
    }

    response = requests.post(
        f"{API_BASE}/api/chat",
        json=payload,
        timeout=60
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n牡丹: {data['response']}")

        if data.get('audio_url'):
            print(f"🔊 Audio: {data['audio_url']}")

        if data.get('reflection'):
            print(f"\n💭 Reflection:")
            print(f"  {json.dumps(data['reflection'], indent=2, ensure_ascii=False)}")

        if data.get('reasoning'):
            print(f"\n🧠 Reasoning:")
            print(f"  {json.dumps(data['reasoning'], indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.text}")

def test_stats():
    """統計取得"""
    print("\n=== Stats ===")
    response = requests.get(f"{API_BASE}/api/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def main():
    print("=" * 60)
    print("Botan API Test Client")
    print("=" * 60)

    # ヘルスチェック
    try:
        test_health()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nAPI server is not running. Start it with:")
        print("  docker-compose up -d")
        sys.exit(1)

    # 設定取得
    test_config()

    # チャットテスト
    test_chat("やっほー！", enable_voice=False, enable_reflection=False)
    test_chat("今日の天気は？", enable_voice=False, enable_reflection=True)

    # 統計
    test_stats()

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
