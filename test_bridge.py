import asyncio
import websockets
import json

async def test():
    uri = "ws://localhost:15432"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to Bridge")
            
            # Test STATUS
            await websocket.send(json.dumps({"command": "STATUS"}))
            response = await websocket.recv()
            print(f"Response: {response}")
            
            data = json.loads(response)
            if data.get('status') == 'ONLINE':
                print("Bridge is ONLINE and ready.")
            else:
                print("Bridge is connected but status is weird.")

            # Test CAPTURE (Mock)
            print("Testing Capture...")
            await websocket.send(json.dumps({"command": "CAPTURE"}))
            
            # Expect CAPTURING
            msg1 = await websocket.recv()
            print(f"Msg1: {msg1}")
            
            # Expect SUCCESS (after delay)
            msg2 = await websocket.recv()
            print(f"Msg2: {msg2} (truncated data)")
            
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
