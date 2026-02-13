import time
import base64
import random
from base_driver import ScannerDriver
from typing import Dict, Any, Optional

class MockDriver(ScannerDriver):
    """
    Simulates a biometric scanner for development without hardware.
    """
    
    def __init__(self):
        self._connected = False
        self._device_name = "Mock Scanner (Dev)"
        self._serial = "MOCK-12345-XYZ"

    def connect(self) -> bool:
        print(f"[{self._device_name}] Connecting...")
        time.sleep(0.5) # Simulate init time
        self._connected = True
        print(f"[{self._device_name}] Connected!")
        return True

    def disconnect(self):
        print(f"[{self._device_name}] Disconnecting...")
        self._connected = False

    def get_status(self) -> str:
        return 'ONLINE' if self._connected else 'OFFLINE'

    def get_device_info(self) -> Dict[str, Any]:
        return {
            'device_name': self._device_name,
            'driver_version': '0.1.0-mock',
            'serial_number': self._serial,
            'type': 'fingerprint' # or face
        }

    def capture_fingerprint(self, timeout_seconds=10) -> Optional[str]:
        """
        Simulates waiting for a finger. 
        In a real GUI app, we might wait for a keypress or button.
        For this backend script, we'll just simulate a delay and random success.
        """
        if not self._connected:
            return None
            
        print(f"[{self._device_name}] Waiting for finger... (Simulated delay)")
        
        # Simulate user delay
        time.sleep(2) 
        
        # Generate dummy high-quality template data
        # In reality this would be bytes from the device
        dummy_data = f"MOCK_TEMPLATE_{random.randint(1000,9999)}_{time.time()}"
        encoded_data = base64.b64encode(dummy_data.encode('utf-8')).decode('utf-8')
        
        print(f"[{self._device_name}] Captured!")
        return encoded_data
