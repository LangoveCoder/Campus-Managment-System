import asyncio
import websockets
import json
import os
import importlib
import sys

# Add bridge directory to path so we can import drivers dynamically
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
current_driver = None

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_driver(driver_name):
    """
    Factory to load driver class dynamically.
    """
    try:
        if driver_name == 'mock':
            from drivers.mock import MockDriver
            return MockDriver()
        elif driver_name == 'secugen':
            # Future implementation
            # from drivers.secugen import SecuGenDriver
            # return SecuGenDriver()
            raise NotImplementedError("SecuGen driver not yet implemented")
        elif driver_name == 'zkteco':
             # Future implementation
            raise NotImplementedError("ZKTeco driver not yet implemented")
        else:
            raise ValueError(f"Unknown driver: {driver_name}")
    except Exception as e:
        print(f"Error loading driver {driver_name}: {e}")
        return None

async def handler(websocket):
    global current_driver
    print("Client connected")
    
    try:
        async for message in websocket:
            print(f"Received: {message}")
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'STATUS':
                status = current_driver.get_status() if current_driver else "DRIVER_ERROR"
                await websocket.send(json.dumps({'type': 'STATUS', 'status': status}))
                
            elif command == 'CAPTURE':
                if not current_driver:
                    await websocket.send(json.dumps({'type': 'ERROR', 'message': 'No driver loaded'}))
                    continue
                
                # Notify client we are capturing
                await websocket.send(json.dumps({'type': 'CAPTURING'}))
                
                # Perform capture (blocking call in thread to avoid freezing loop if needed, 
                # but for simplicity/mock we call directly as it sleeps)
                # In real production with blocking DLLs, use loop.run_in_executor
                
                template = await asyncio.to_thread(current_driver.capture_fingerprint, timeout_seconds=10)
                
                if template:
                    await websocket.send(json.dumps({
                        'type': 'CAPTURE_SUCCESS', 
                        'data': template,
                        'format': 'base64'
                    }))
                else:
                    await websocket.send(json.dumps({'type': 'CAPTURE_TIMEOUT'}))
                    
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    global current_driver
    config = load_config()
    driver_name = config.get('driver', 'mock')
    port = config.get('port', 15432)
    
    print(f"Initializing Bridge Server on port {port}...")
    print(f"Loading driver: {driver_name}")
    
    current_driver = get_driver(driver_name)
    if current_driver:
        if current_driver.connect():
            print("Driver connected successfully.")
        else:
            print("Failed to connect to driver.")
    
    async with websockets.serve(handler, "localhost", port):
        print(f"Bridge Server listening on ws://localhost:{port}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        if current_driver:
            current_driver.disconnect()
        print("Server stopped.")
