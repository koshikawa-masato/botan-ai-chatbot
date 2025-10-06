#!/usr/bin/env python3
"""
WebSocket Test Client
リアルタイム対話のテスト
"""

import asyncio
import websockets
import json
import time
from datetime import datetime

WS_URL = "ws://localhost:8000/ws/chat"

async def test_basic_websocket():
    """基本的なWebSocket接続テスト"""
    print("\n" + "="*60)
    print("WebSocket Basic Connection Test")
    print("="*60)

    try:
        async with websockets.connect(WS_URL) as websocket:
            print(f"✅ Connected to {WS_URL}")

            # テストメッセージ送信
            test_messages = [
                "やっほー！",
                "今日は何する？",
                "牡丹って名前かわいいね"
            ]

            for msg in test_messages:
                # メッセージ送信
                message_data = {
                    "type": "chat",
                    "message": msg,
                    "user_id": "test_user",
                    "timestamp": time.time()
                }

                print(f"\n→ User: {msg}")
                await websocket.send(json.dumps(message_data))

                # レスポンス受信
                response = await websocket.recv()
                response_data = json.loads(response)

                print(f"← Botan: {response_data.get('response')}")
                if response_data.get('audio_url'):
                    print(f"   🔊 Audio: {response_data.get('audio_url')}")

                # 少し待つ
                await asyncio.sleep(1)

            print("\n✅ Basic WebSocket test completed")
            return True

    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

async def test_concurrent_messages():
    """複数メッセージの連続送信テスト"""
    print("\n" + "="*60)
    print("WebSocket Concurrent Messages Test")
    print("="*60)

    try:
        async with websockets.connect(WS_URL) as websocket:
            print(f"✅ Connected to {WS_URL}")

            messages = [
                "ねえねえ",
                "聞いてる？",
                "返事して〜！"
            ]

            # 連続送信
            print("\n連続メッセージ送信中...")
            for i, msg in enumerate(messages, 1):
                message_data = {
                    "type": "chat",
                    "message": msg,
                    "user_id": "test_user",
                    "sequence": i,
                    "timestamp": time.time()
                }

                print(f"{i}. → {msg}")
                await websocket.send(json.dumps(message_data))
                await asyncio.sleep(0.1)  # わずかな遅延

            # レスポンスを受信
            print("\nレスポンス受信中...")
            for i in range(len(messages)):
                response = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=5.0
                )
                response_data = json.loads(response)
                print(f"{i+1}. ← {response_data.get('response')}")

            print("\n✅ Concurrent messages test completed")
            return True

    except asyncio.TimeoutError:
        print("❌ Timeout waiting for response")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_long_connection():
    """長時間接続の安定性テスト"""
    print("\n" + "="*60)
    print("WebSocket Long Connection Test")
    print("="*60)

    try:
        async with websockets.connect(WS_URL) as websocket:
            print(f"✅ Connected to {WS_URL}")

            duration = 10  # 10秒間
            start_time = time.time()
            message_count = 0

            print(f"\n{duration}秒間の接続テスト開始...")

            while time.time() - start_time < duration:
                elapsed = int(time.time() - start_time)

                # メッセージ送信
                message_data = {
                    "type": "chat",
                    "message": f"テストメッセージ #{message_count + 1}",
                    "user_id": "test_user",
                    "timestamp": time.time()
                }

                await websocket.send(json.dumps(message_data))
                message_count += 1

                # レスポンス受信
                response = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=3.0
                )

                print(f"[{elapsed}s] Message #{message_count} - OK")

                # 2秒待つ
                await asyncio.sleep(2)

            print(f"\n✅ 接続安定性テスト完了: {message_count}メッセージ送受信")
            return True

    except Exception as e:
        print(f"❌ Error after {message_count} messages: {e}")
        return False

async def test_voice_enabled_websocket():
    """音声合成有効でのWebSocketテスト"""
    print("\n" + "="*60)
    print("WebSocket with Voice Synthesis Test")
    print("="*60)

    try:
        async with websockets.connect(WS_URL) as websocket:
            print(f"✅ Connected to {WS_URL}")

            # 音声合成リクエスト
            message_data = {
                "type": "chat",
                "message": "マジで？超うれしい！",
                "user_id": "test_user",
                "enable_voice": True,
                "timestamp": time.time()
            }

            print(f"\n→ User: {message_data['message']}")
            print("   (音声合成有効)")

            await websocket.send(json.dumps(message_data))

            # レスポンス受信（音声生成があるので長めに待つ）
            response = await asyncio.wait_for(
                websocket.recv(),
                timeout=60.0
            )
            response_data = json.loads(response)

            print(f"← Botan: {response_data.get('response')}")

            if response_data.get('audio_url'):
                print(f"   🔊 Audio URL: {response_data.get('audio_url')}")
                print("   ✅ 音声ファイル生成成功")
            else:
                print("   ⚠️ 音声URLなし（実装待ち）")

            return True

    except asyncio.TimeoutError:
        print("❌ Timeout - 音声生成に時間がかかりすぎています")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_multiple_clients():
    """複数クライアント同時接続テスト"""
    print("\n" + "="*60)
    print("Multiple Clients Connection Test")
    print("="*60)

    async def client_session(client_id, message):
        try:
            async with websockets.connect(WS_URL) as websocket:
                print(f"  Client {client_id}: Connected")

                message_data = {
                    "type": "chat",
                    "message": message,
                    "user_id": f"client_{client_id}",
                    "timestamp": time.time()
                }

                await websocket.send(json.dumps(message_data))

                response = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=5.0
                )
                response_data = json.loads(response)

                print(f"  Client {client_id}: ← {response_data.get('response')}")
                return True

        except Exception as e:
            print(f"  Client {client_id}: ❌ {e}")
            return False

    try:
        # 3つのクライアントを同時接続
        tasks = [
            client_session(1, "やっほー！"),
            client_session(2, "元気？"),
            client_session(3, "今日いい天気だね")
        ]

        print("\n3クライアント同時接続中...")
        results = await asyncio.gather(*tasks)

        success_count = sum(results)
        print(f"\n✅ {success_count}/3 クライアント成功")

        return all(results)

    except Exception as e:
        print(f"❌ Multiple clients test failed: {e}")
        return False

async def main():
    """全テストを実行"""
    print("="*60)
    print("Botan WebSocket Test Suite")
    print("="*60)

    tests = [
        ("Basic Connection", test_basic_websocket),
        ("Concurrent Messages", test_concurrent_messages),
        ("Voice Enabled", test_voice_enabled_websocket),
        ("Multiple Clients", test_multiple_clients),
        ("Long Connection", test_long_connection),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False

        # テスト間の待機
        await asyncio.sleep(1)

    # 結果サマリー
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:25s}: {status}")

    total = len(results)
    passed = sum(results.values())

    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
