#!/bin/bash
# One-click setup for Bluetooth HID controller

echo "🔧 Setting up Steam Deck as Bluetooth Controller..."
echo "=============================================="

# Check if running on Steam Deck
if [ ! -f /etc/os-release ] || ! grep -q "SteamOS" /etc/os-release; then
    echo "⚠️  Warning: This script is designed for Steam Deck/SteamOS"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi

# Enable Bluetooth if disabled
echo "📡 Checking Bluetooth status..."
if ! systemctl is-active --quiet bluetooth; then
    echo "Enabling Bluetooth service..."
    sudo systemctl enable --now bluetooth
fi

# Install required packages
echo "📦 Installing dependencies..."
sudo pacman -S --noconfirm bluez bluez-utils bluez-plugins
sudo pip install dbus-python pybluez

# Create systemd service for HID emulation
echo "⚙️  Setting up HID emulation service..."
sudo cp systemd/hid-emulator.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable HID over Bluetooth
echo "🔌 Configuring Bluetooth HID profile..."
sudo bash -c 'cat > /etc/bluetooth/input.conf << EOF
# Enable HID profile
[General]
UserspaceHID=true
ClassicBondedOnly=true

[Policy]
AutoEnable=true
EOF'

# Create pairing helper script
echo "📝 Creating pairing helper..."
sudo bash -c 'cat > /usr/local/bin/deck-pair-helper << EOF
#!/bin/bash
# Simple Bluetooth pairing helper for Steam Deck controller

echo "Put your PC in Bluetooth pairing mode first!"
echo "Then press Enter to make Steam Deck discoverable..."
read

bluetoothctl discoverable on
bluetoothctl pairable on
echo "Steam Deck is now discoverable as 'Steam Deck Controller'"
echo "Pair with it from your PC within 30 seconds..."

sleep 30
bluetoothctl discoverable off
echo "Done! If pairing failed, run this script again."
EOF'

sudo chmod +x /usr/local/bin/deck-pair-helper

# Create easy-to-use start script
echo "🚀 Creating start script..."
cat > ~/Desktop/Start_Controller.sh << 'EOF'
#!/bin/bash
cd ~/homebrew/plugins/decky-bluetooth-controller
python main.py --start
EOF
chmod +x ~/Desktop/Start_Controller.sh

echo ""
echo "✅ Installation complete!"
echo ""
echo "Quick Start Guide:"
echo "1. Open the Decky plugin (named 'Deck Controller')"
echo "2. Click 'Make Discoverable'"
echo "3. On your PC:"
echo "   - Open Bluetooth settings"
echo "   - Click 'Add Device'"
echo "   - Look for 'Steam Deck Controller'"
echo "   - Pair without a PIN (or use 0000)"
echo ""
echo "🎮 Your Steam Deck is now a Bluetooth gamepad!"
echo ""