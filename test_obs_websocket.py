#!/usr/bin/env python3
"""
OBS WebSocket Connection Test
"""
import asyncio
import websockets
import json
import time

async def test_obs_connection():
    """Test 1: OBS WebSocket connection"""
    print("=" * 50)
    print("Test 1: OBS WebSocket Connection")
    print("=" * 50)

    uri = "ws://localhost:8000/ws/obs"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to {uri}")

            # Send connection message
            connect_msg = {
                "type": "obs_connect",
                "timestamp": time.time()
            }
            await websocket.send(json.dumps(connect_msg))
            print(f"📤 Sent: {connect_msg}")

            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            print(f"📥 Received: {data}")

            if data.get("type") == "connected":
                print("✅ Connection confirmed")
            else:
                print("⚠️ Unexpected response")

    except asyncio.TimeoutError:
        print("❌ Connection timeout")
    except Exception as e:
        print(f"❌ Error: {e}")

    print()

async def test_subtitle_broadcast():
    """Test 2: Subtitle broadcast from chat to OBS"""
    print("=" * 50)
    print("Test 2: Subtitle Broadcast (Chat → OBS)")
    print("=" * 50)

    obs_uri = "ws://localhost:8000/ws/obs"
    chat_uri = "ws://localhost:8000/ws/chat"

    try:
        # Connect OBS client
        async with websockets.connect(obs_uri) as obs_ws:
            print(f"✅ OBS connected to {obs_uri}")

            # Send OBS connection message
            await obs_ws.send(json.dumps({
                "type": "obs_connect",
                "timestamp": time.time()
            }))

            # Wait for connection confirmation
            await asyncio.wait_for(obs_ws.recv(), timeout=3.0)
            print("✅ OBS connection confirmed")

            # Connect chat client
            async with websockets.connect(chat_uri) as chat_ws:
                print(f"✅ Chat connected to {chat_uri}")

                # Send chat message
                chat_msg = {
                    "type": "chat",
                    "message": "OBSテスト：字幕表示されるかな？",
                    "user_id": "test_user",
                    "enable_voice": False,
                    "enable_reflection": False,
                    "timestamp": time.time()
                }
                await chat_ws.send(json.dumps(chat_msg))
                print(f"📤 Chat sent: {chat_msg['message']}")

                # Wait for chat response
                chat_response = await asyncio.wait_for(chat_ws.recv(), timeout=30.0)
                chat_data = json.loads(chat_response)
                print(f"📥 Chat response: {chat_data.get('response', 'No response')}")

                # Wait for subtitle broadcast to OBS
                print("⏳ Waiting for subtitle broadcast to OBS...")
                subtitle_data = await asyncio.wait_for(obs_ws.recv(), timeout=10.0)
                subtitle = json.loads(subtitle_data)
                print(f"📥 OBS received subtitle: {subtitle}")

                if subtitle.get("type") == "subtitle":
                    print(f"✅ Subtitle text: {subtitle.get('text')}")
                    print(f"✅ Speaker: {subtitle.get('speaker')}")
                else:
                    print("⚠️ Unexpected subtitle format")

    except asyncio.TimeoutError:
        print("❌ Timeout waiting for subtitle")
    except Exception as e:
        print(f"❌ Error: {e}")

    print()

async def test_multiple_obs_clients():
    """Test 3: Multiple OBS clients receiving same subtitle"""
    print("=" * 50)
    print("Test 3: Multiple OBS Clients")
    print("=" * 50)

    obs_uri = "ws://localhost:8000/ws/obs"
    chat_uri = "ws://localhost:8000/ws/chat"

    try:
        # Connect 2 OBS clients
        async with websockets.connect(obs_uri) as obs1, \
                   websockets.connect(obs_uri) as obs2:

            print("✅ OBS Client 1 connected")
            print("✅ OBS Client 2 connected")

            # Send connection messages
            for obs_ws in [obs1, obs2]:
                await obs_ws.send(json.dumps({
                    "type": "obs_connect",
                    "timestamp": time.time()
                }))
                await asyncio.wait_for(obs_ws.recv(), timeout=3.0)

            print("✅ Both OBS clients confirmed")

            # Connect chat client and send message
            async with websockets.connect(chat_uri) as chat_ws:
                chat_msg = {
                    "type": "chat",
                    "message": "複数OBSクライアントテスト",
                    "user_id": "test_user",
                    "timestamp": time.time()
                }
                await chat_ws.send(json.dumps(chat_msg))
                print("📤 Chat message sent")

                # Wait for chat response
                await asyncio.wait_for(chat_ws.recv(), timeout=30.0)

                # Both OBS clients should receive subtitle
                subtitle1 = await asyncio.wait_for(obs1.recv(), timeout=10.0)
                subtitle2 = await asyncio.wait_for(obs2.recv(), timeout=10.0)

                data1 = json.loads(subtitle1)
                data2 = json.loads(subtitle2)

                print(f"📥 OBS 1 received: {data1.get('text', 'No text')}")
                print(f"📥 OBS 2 received: {data2.get('text', 'No text')}")

                if data1.get('text') == data2.get('text'):
                    print("✅ Both clients received same subtitle")
                else:
                    print("⚠️ Subtitle mismatch")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()

async def main():
    """Run all tests"""
    print("\n🎬 OBS WebSocket Integration Tests\n")

    await test_obs_connection()
    await test_subtitle_broadcast()
    await test_multiple_obs_clients()

    print("=" * 50)
    print("✅ All tests completed")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
