#!/usr/bin/env python3
import socket
import json
import threading
import time
from typing import Dict, Any
import pygame
import sys

class VirtualController:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        # Initialize virtual joystick (requires vgamepad or similar on Windows)
        # On Linux, you can use uinput or evdev
        print("Virtual Controller Initialized")
        
    def update_inputs(self, data: Dict[str, Any]):
        """Update virtual controller with new inputs"""
        try:
            # Map Steam Deck inputs to virtual controller
            buttons = data.get('buttons', {})
            sticks = data.get('sticks', {})
            triggers = data.get('triggers', {})
            
            # TODO: Implement actual controller emulation
            # This would use pygame or platform-specific libraries
            
            print(f"Inputs: Buttons={buttons}, Sticks={sticks}, Triggers={triggers}")
            
        except Exception as e:
            print(f"Error updating inputs: {e}")

class PCReceiver:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.controller = VirtualController()
        self.connected = False
        self.client_socket = None
        
    def start(self):
        """Start the receiver server"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(1)
        
        print(f"PC Receiver listening on {self.host}:{self.port}")
        
        while True:
            try:
                client, address = server.accept()
                print(f"Connection from {address}")
                
                # Handle client in a new thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except KeyboardInterrupt:
                print("Shutting down...")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        server.close()
    
    def handle_client(self, client, address):
        """Handle individual client connection"""
        self.connected = True
        self.client_socket = client
        
        try:
            while self.connected:
                # Receive data
                data = client.recv(1024)
                if not data:
                    break
                
                # Process each line (JSON per line)
                lines = data.decode().strip().split('\n')
                for line in lines:
                    if line:
                        self.process_message(line)
        
        except Exception as e:
            print(f"Client error {address}: {e}")
        finally:
            self.connected = False
            client.close()
            print(f"Client {address} disconnected")
    
    def process_message(self, message: str):
        """Process incoming JSON message"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'handshake':
                # Send acknowledgment
                response = json.dumps({
                    "status": "ok",
                    "message": "Connected successfully"
                })
                self.client_socket.send(response.encode() + b'\n')
                print("Handshake complete")
                
            elif msg_type == 'input':
                # Update virtual controller
                self.controller.update_inputs(data)
                
        except json.JSONDecodeError:
            print(f"Invalid JSON: {message}")
        except Exception as e:
            print(f"Error processing message: {e}")

if __name__ == "__main__":
    receiver = PCReceiver()
    print("""
    Steam Deck PC Controller Receiver
    =================================
    Make sure:
    1. Firewall allows connections on port 8888
    2. Steam Deck and PC are on same network
    3. Enter PC's IP address in Decky plugin
    
    Starting receiver...
    """)
    receiver.start()