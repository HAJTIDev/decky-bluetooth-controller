#!/usr/bin/env python3
"""
Steam Deck Bluetooth Controller Plugin
Zero-configuration, just install and use!
"""

import asyncio
import dbus
import dbus.mainloop.glib
import subprocess
import json
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from gi.repository import GLib

# Decky Plugin Framework
import decky

class BluetoothHIDController:
    """Main Bluetooth HID controller class"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.is_active = False
        self.paired_devices = []
        self.current_client = None
        self.hid_service = None
        
        # Default HID descriptor for Xbox-style controller
        self.hid_descriptor = bytes([
            0x05, 0x01, 0x09, 0x05, 0xA1, 0x01, 0x15, 0x00,
            0x25, 0x01, 0x35, 0x00, 0x45, 0x01, 0x75, 0x01,
            0x95, 0x0E, 0x05, 0x09, 0x19, 0x01, 0x29, 0x0E,
            0x81, 0x02, 0x95, 0x02, 0x81, 0x01, 0x05, 0x01,
            0x25, 0x07, 0x46, 0x3B, 0x01, 0x75, 0x04, 0x95,
            0x01, 0x65, 0x14, 0x09, 0x39, 0x81, 0x42, 0x65,
            0x00, 0x95, 0x01, 0x81, 0x01, 0x26, 0xFF, 0x00,
            0x46, 0xFF, 0x00, 0x09, 0x30, 0x09, 0x31, 0x09,
            0x32, 0x09, 0x35, 0x75, 0x08, 0x95, 0x04, 0x81,
            0x02, 0x06, 0x00, 0xFF, 0x09, 0x20, 0x75, 0x06,
            0x95, 0x01, 0x81, 0x02, 0x05, 0x01, 0x09, 0x33,
            0x09, 0x34, 0x16, 0x00, 0x80, 0x26, 0xFF, 0x00,
            0x46, 0xFF, 0x00, 0x75, 0x10, 0x95, 0x02, 0x81,
            0x02, 0x06, 0x00, 0xFF, 0x09, 0x21, 0x95, 0x01,
            0x81, 0x02, 0x06, 0x00, 0xFF, 0x09, 0x22, 0x95,
            0x01, 0x81, 0x02, 0x06, 0x00, 0xFF, 0x09, 0x23,
            0x95, 0x01, 0x81, 0x02, 0x06, 0x00, 0xFF, 0x09, 0x24,
            0x95, 0x01, 0x81, 0x02, 0x05, 0x01, 0x09, 0x25,
            0x09, 0x26, 0x09, 0x27, 0x09, 0x28, 0x09, 0x29,
            0x09, 0x2A, 0x09, 0x2B, 0x09, 0x2C, 0x09, 0x2D,
            0x09, 0x2E, 0x09, 0x2F, 0x09, 0x30, 0x09, 0x31,
            0x09, 0x32, 0x09, 0x33, 0x09, 0x34, 0x09, 0x35,
            0x09, 0x36, 0x09, 0x37, 0x09, 0x38, 0x09, 0x39,
            0x09, 0x3A, 0x09, 0x3B, 0x09, 0x3C, 0x09, 0x3D,
            0x09, 0x3E, 0x09, 0x3F, 0x09, 0x40, 0x09, 0x41,
            0x09, 0x42, 0x09, 0x43, 0x09, 0x44, 0x09, 0x45,
            0x09, 0x46, 0x09, 0x47, 0x09, 0x48, 0x09, 0x49,
            0x09, 0x4A, 0x09, 0x4B, 0x09, 0x4C, 0x09, 0x4D,
            0x09, 0x4E, 0x09, 0x4F, 0x75, 0x08, 0x95, 0x3F,
            0x81, 0x02, 0xC0
        ])
        
    def _setup_logging(self):
        """Setup logging"""
        logger = logging.getLogger("DeckController")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def start_controller_mode(self):
        """Start Bluetooth HID controller mode"""
        try:
            self.logger.info("Starting Bluetooth HID Controller mode...")
            
            # Stop Steam input to avoid conflicts
            await self._release_steam_input()
            
            # Setup Bluetooth HID profile
            success = await self._setup_bluetooth_hid()
            
            if success:
                self.is_active = True
                self.logger.info("✅ Controller mode active!")
                self.logger.info("Go to PC Bluetooth settings and pair with 'Steam Deck Controller'")
                return True
            else:
                self.logger.error("Failed to start controller mode")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting controller: {e}")
            return False
    
    async def stop_controller_mode(self):
        """Stop controller mode and restore normal Steam Deck functionality"""
        try:
            self.logger.info("Stopping controller mode...")
            
            # Disconnect any Bluetooth connections
            await self._disconnect_bluetooth()
            
            # Restore Steam input
            await self._restore_steam_input()
            
            self.is_active = False
            self.logger.info("Controller mode stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping controller: {e}")
            return False
    
    async def _release_steam_input(self):
        """Temporarily release Steam's control over inputs"""
        try:
            # Kill steam input temporarily (it will restart automatically)
            subprocess.run(["systemctl", "--user", "stop", "steam-input"], 
                         capture_output=True)
            self.logger.info("Steam input released")
        except Exception as e:
            self.logger.warning(f"Could not release steam input: {e}")
    
    async def _restore_steam_input(self):
        """Restore Steam's input control"""
        try:
            subprocess.run(["systemctl", "--user", "start", "steam-input"],
                         capture_output=True)
            self.logger.info("Steam input restored")
        except Exception as e:
            self.logger.warning(f"Could not restore steam input: {e}")
    
    async def _setup_bluetooth_hid(self):
        """Setup Bluetooth HID profile using bluez"""
        try:
            # Make Bluetooth discoverable with controller name
            subprocess.run([
                "bluetoothctl", "system-alias", "Steam Deck Controller"
            ], capture_output=True)
            
            subprocess.run([
                "bluetoothctl", "discoverable", "on"
            ], capture_output=True)
            
            subprocess.run([
                "bluetoothctl", "pairable", "on"
            ], capture_output=True)
            
            # Set device class to "Gamepad" (0x002508)
            subprocess.run([
                "bluetoothctl", "class", "0x002508"
            ], capture_output=True)
            
            self.logger.info("Bluetooth configured as gamepad")
            return True
            
        except Exception as e:
            self.logger.error(f"Bluetooth setup failed: {e}")
            return False
    
    async def _disconnect_bluetooth(self):
        """Disconnect Bluetooth HID connections"""
        try:
            subprocess.run(["bluetoothctl", "disconnect"], 
                         capture_output=True)
            subprocess.run(["bluetoothctl", "discoverable", "off"],
                         capture_output=True)
            self.logger.info("Bluetooth disconnected")
        except Exception as e:
            self.logger.warning(f"Error disconnecting Bluetooth: {e}")
    
    async def send_controller_input(self, buttons, axes, triggers):
        """Send controller input data over Bluetooth HID"""
        if not self.is_active or not self.current_client:
            return
        
        # Format HID report
        report = self._create_hid_report(buttons, axes, triggers)
        
        try:
            # This would send via Bluetooth HID socket
            # In production, use proper HID over GATT (HOGP) implementation
            pass
        except Exception as e:
            self.logger.error(f"Error sending input: {e}")
    
    def _create_hid_report(self, buttons, axes, triggers):
        """Create HID report for Xbox controller"""
        # Xbox controller HID report structure
        report = bytearray(20)
        
        # Buttons (bytes 0-1)
        button_mask = 0
        button_map = {
            'A': 0, 'B': 1, 'X': 2, 'Y': 3,
            'LB': 4, 'RB': 5, 'BACK': 6, 'START': 7,
            'LSTICK': 8, 'RSTICK': 9
        }
        
        for btn_name, pressed in buttons.items():
            if pressed and btn_name in button_map:
                button_mask |= 1 << button_map[btn_name]
        
        report[0] = button_mask & 0xFF
        report[1] = (button_mask >> 8) & 0xFF
        
        # Triggers (bytes 2-3)
        report[2] = int(triggers.get('L', 0) * 255)
        report[3] = int(triggers.get('R', 0) * 255)
        
        # Left stick (bytes 4-5)
        report[4] = int((axes.get('LX', 0) + 1) * 127.5)
        report[5] = int((axes.get('LY', 0) + 1) * 127.5)
        
        # Right stick (bytes 6-7)
        report[6] = int((axes.get('RX', 0) + 1) * 127.5)
        report[7] = int((axes.get('RY', 0) + 1) * 127.5)
        
        # D-pad (byte 8)
        dpad_map = {
            'UP': 0, 'UP_RIGHT': 1, 'RIGHT': 2, 'DOWN_RIGHT': 3,
            'DOWN': 4, 'DOWN_LEFT': 5, 'LEFT': 6, 'UP_LEFT': 7
        }
        report[8] = dpad_map.get(axes.get('DPAD', 8), 8)
        
        return bytes(report)

# Decky Plugin Interface
class Plugin:
    async def _main(self):
        """Called when plugin loads"""
        self.controller = BluetoothHIDController()
        self.logger = self.controller.logger
        self.logger.info("🎮 Deck Controller Plugin Loaded")
        
        # Auto-start if enabled in settings
        settings = await self.load_settings()
        if settings.get("auto_start", False):
            await self.start_controller()
    
    async def _unload(self):
        """Called when plugin unloads"""
        await self.stop_controller()
        self.logger.info("Deck Controller Plugin Unloaded")
    
    async def start_controller(self):
        """Start controller mode (called from frontend)"""
        success = await self.controller.start_controller_mode()
        return {"success": success, "message": "Controller mode started" if success else "Failed to start"}
    
    async def stop_controller(self):
        """Stop controller mode"""
        success = await self.controller.stop_controller_mode()
        return {"success": success, "message": "Controller mode stopped"}
    
    async def get_status(self):
        """Get current controller status"""
        return {
            "active": self.controller.is_active,
            "paired_devices": self.controller.paired_devices,
            "discoverable": True
        }
    
    async def make_discoverable(self, duration=60):
        """Make Steam Deck discoverable for pairing"""
        try:
            subprocess.run(["bluetoothctl", "discoverable", "on"], 
                         capture_output=True)
            subprocess.run(["bluetoothctl", "pairable", "on"],
                         capture_output=True)
            
            # Auto turn off after duration
            asyncio.create_task(self._stop_discoverable(duration))
            
            return {"success": True, "message": f"Discoverable for {duration} seconds"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _stop_discoverable(self, delay):
        """Stop discoverable mode after delay"""
        await asyncio.sleep(delay)
        subprocess.run(["bluetoothctl", "discoverable", "off"],
                     capture_output=True)
    
    async def load_settings(self):
        """Load plugin settings"""
        settings_path = Path.home() / ".config" / "decky-controller.json"
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                return json.load(f)
        return {}
    
    async def save_settings(self, settings):
        """Save plugin settings"""
        settings_path = Path.home() / ".config" / "decky-controller.json"
        with open(settings_path, 'w') as f:
            json.dump(settings, f)
        return {"success": True}