from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ScannerDriver(ABC):
    """
    Abstract Base Class for all Biometric Scanner Drivers.
    Any device (SecuGen, ZKTeco, DigitalPersona) must implement this interface.
    """

    @abstractmethod
    def connect(self) -> bool:
        """
        Initialize connection to the hardware.
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Cleanly close the connection.
        """
        pass

    @abstractmethod
    def get_status(self) -> str:
        """
        Return current device status: 'ONLINE', 'OFFLINE', 'BUSY', 'ERROR'.
        """
        pass

    @abstractmethod
    def get_device_info(self) -> Dict[str, Any]:
        """
        Return metadata:
        {
            'device_name': 'SecuGen Hamster Pro 20',
            'driver_version': '1.0.0',
            'serial_number': '...'
        }
        """
        pass

    @abstractmethod
    def capture_fingerprint(self, timeout_seconds=10) -> Optional[str]:
        """
        Blocking call to capture a fingerprint.
        - timeout_seconds: Max time to wait for a finger.
        
        Returns:
            - Base64 encoded template string if successful.
            - None if timed out or failed.
        """
        pass
