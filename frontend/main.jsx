import { useState, useEffect, useCallback } from "react";
import {
  PanelSection,
  PanelSectionRow,
  ButtonItem,
  ToggleField,
  DialogButton,
  ProgressBarWithInfo,
  showModal,
  ModalRoot,
  Navigation,
  SidebarNavigation,
  SidebarNavigationPage,
  Focusable,
  staticClasses
} from "decky-frontend-lib";
import { FaGamepad, FaBluetooth, FaCog, FaQuestionCircle } from "react-icons/fa";

// Import styles
import "./style.css";

const Main = () => {
  const [controllerActive, setControllerActive] = useState(false);
  const [isDiscoverable, setIsDiscoverable] = useState(false);
  const [pairedDevices, setPairedDevices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [autoStart, setAutoStart] = useState(false);
  const [currentPage, setCurrentPage] = useState("main");

  // Load initial status
  useEffect(() => {
    loadStatus();
    loadSettings();
  }, []);

  const loadStatus = async () => {
    try {
      const result = await callPluginMethod("get_status", {});
      if (result.success) {
        setControllerActive(result.result.active);
        setPairedDevices(result.result.paired_devices || []);
        setIsDiscoverable(result.result.discoverable);
      }
    } catch (error) {
      console.error("Error loading status:", error);
    }
  };

  const loadSettings = async () => {
    try {
      const result = await callPluginMethod("load_settings", {});
      if (result.success) {
        setAutoStart(result.result.auto_start || false);
      }
    } catch (error) {
      console.error("Error loading settings:", error);
    }
  };

  const saveSettings = async () => {
    await callPluginMethod("save_settings", {
      settings: { auto_start: autoStart }
    });
  };

  const toggleController = async () => {
    setLoading(true);
    try {
      if (controllerActive) {
        const result = await callPluginMethod("stop_controller", {});
        if (result.success) {
          setControllerActive(false);
          showSuccessModal("Controller mode stopped", "Steam Deck controls restored.");
        }
      } else {
        const result = await callPluginMethod("start_controller", {});
        if (result.success) {
          setControllerActive(true);
          showSuccessModal("Controller mode active!", "Go to PC Bluetooth settings and pair with 'Steam Deck Controller'");
        }
      }
    } catch (error) {
      console.error("Error toggling controller:", error);
      showErrorModal("Error", error.message || "Failed to toggle controller mode");
    } finally {
      setLoading(false);
      loadStatus();
    }
  };

  const makeDiscoverable = async () => {
    setLoading(true);
    try {
      const result = await callPluginMethod("make_discoverable", { duration: 60 });
      if (result.success) {
        setIsDiscoverable(true);
        showSuccessModal("Discoverable Mode", "Steam Deck is now discoverable for 60 seconds.\n\nOn your PC:\n1. Open Bluetooth Settings\n2. Add new device\n3. Look for 'Steam Deck Controller'\n4. Pair (no PIN required)");
        
        // Auto stop discoverable after 60s
        setTimeout(() => {
          setIsDiscoverable(false);
        }, 60000);
      }
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  const showSuccessModal = (title, message) => {
    showModal(
      <ModalRoot>
        <div style={{ padding: "20px", textAlign: "center" }}>
          <div style={{ fontSize: "48px", marginBottom: "20px", color: "#1a9fff" }}>
            ✓
          </div>
          <h2 style={{ marginBottom: "10px" }}>{title}</h2>
          <p style={{ whiteSpace: "pre-line" }}>{message}</p>
          <div style={{ marginTop: "30px" }}>
            <DialogButton onClick={() => window.closeModal()}>OK</DialogButton>
          </div>
        </div>
      </ModalRoot>
    );
  };

  const showErrorModal = (title, message) => {
    showModal(
      <ModalRoot>
        <div style={{ padding: "20px", textAlign: "center" }}>
          <div style={{ fontSize: "48px", marginBottom: "20px", color: "#ff4757" }}>
            ✗
          </div>
          <h2 style={{ marginBottom: "10px" }}>{title}</h2>
          <p>{message}</p>
          <div style={{ marginTop: "30px" }}>
            <DialogButton onClick={() => window.closeModal()}>OK</DialogButton>
          </div>
        </div>
      </ModalRoot>
    );
  };

  const showQuickStartGuide = () => {
    showModal(
      <ModalRoot>
        <div style={{ padding: "20px" }}>
          <h2 style={{ marginBottom: "20px", textAlign: "center" }}>🎮 Quick Start Guide</h2>
          
          <div style={{ marginBottom: "20px" }}>
            <h3>Step 1: Enable Controller</h3>
            <p>Click "Enable Controller Mode" above</p>
          </div>
          
          <div style={{ marginBottom: "20px" }}>
            <h3>Step 2: Make Discoverable</h3>
            <p>Click "Make Discoverable for Pairing"</p>
          </div>
          
          <div style={{ marginBottom: "20px" }}>
            <h3>Step 3: On Your PC</h3>
            <ol style={{ paddingLeft: "20px" }}>
              <li>Open Bluetooth Settings</li>
              <li>Click "Add Device"</li>
              <li>Look for "Steam Deck Controller"</li>
              <li>Pair (no PIN or use 0000)</li>
            </ol>
          </div>
          
          <div style={{ marginBottom: "20px" }}>
            <h3>Step 4: Play!</h3>
            <p>Your PC will see Steam Deck as a gamepad. Launch any game!</p>
          </div>
          
          <div style={{ textAlign: "center", marginTop: "30px" }}>
            <DialogButton onClick={() => window.closeModal()}>Got it!</DialogButton>
          </div>
        </div>
      </ModalRoot>
    );
  };

  const MainPage = () => (
    <div className="controller-main">
      <div className="header-section">
        <div className="status-indicator">
          <div className={`status-dot ${controllerActive ? "active" : "inactive"}`} />
          <span className="status-text">
            {controllerActive ? "Controller Mode Active" : "Ready to Connect"}
          </span>
        </div>
      </div>

      <PanelSection title="Quick Actions">
        <PanelSectionRow>
          <ButtonItem
            layout="below"
            onClick={toggleController}
            disabled={loading}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <FaGamepad size={24} />
              <span>
                {controllerActive ? "Disable Controller Mode" : "Enable Controller Mode"}
              </span>
            </div>
          </ButtonItem>
        </PanelSectionRow>

        <PanelSectionRow>
          <ButtonItem
            layout="below"
            onClick={makeDiscoverable}
            disabled={loading || !controllerActive}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <FaBluetooth size={24} />
              <span>
                {isDiscoverable ? "Currently Discoverable" : "Make Discoverable for Pairing"}
              </span>
            </div>
          </ButtonItem>
        </PanelSectionRow>
      </PanelSection>

      {controllerActive && (
        <PanelSection title="Connection Status">
          <PanelSectionRow>
            <div className="connection-info">
              <p><strong>Device Name:</strong> Steam Deck Controller</p>
              <p><strong>Status:</strong> {isDiscoverable ? "Waiting for PC to pair..." : "Ready to connect"}</p>
              <p><strong>Paired Devices:</strong> {pairedDevices.length}</p>
            </div>
          </PanelSectionRow>
        </PanelSection>
      )}

      {loading && (
        <PanelSectionRow>
          <ProgressBarWithInfo
            label="Processing..."
            description="Please wait"
            sOperationText="Working"
          />
        </PanelSectionRow>
      )}
    </div>
  );

  const SettingsPage = () => (
    <PanelSection title="Settings">
      <PanelSectionRow>
        <ToggleField
          label="Auto-start Controller Mode"
          checked={autoStart}
          onChange={(value) => {
            setAutoStart(value);
            saveSettings();
          }}
          description="Automatically enable controller mode when plugin loads"
        />
      </PanelSectionRow>
      
      <PanelSectionRow>
        <div className="settings-info">
          <p><strong>Device Type:</strong> Xbox 360-compatible gamepad</p>
          <p><strong>Connection:</strong> Bluetooth HID</p>
          <p><strong>Battery Impact:</strong> Low-Medium</p>
        </div>
      </PanelSectionRow>
    </PanelSection>
  );

  return (
    <div className="decky-controller-plugin">
      <div className="plugin-header">
        <h1>🎮 Deck Controller</h1>
        <p className="subtitle">Use Steam Deck as a Bluetooth gamepad for PC</p>
      </div>

      <SidebarNavigation
        title="Deck Controller"
        showTitle={false}
        pages={[
          {
            title: "Controller",
            content: <MainPage />,
            icon: <FaGamepad />,
            hideTitle: true
          },
          {
            title: "Settings",
            content: <SettingsPage />,
            icon: <FaCog />,
            hideTitle: true
          }
        ]}
      />

      <div className="quick-help">
        <ButtonItem
          layout="below"
          onClick={showQuickStartGuide}
          style={{ marginTop: "20px" }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <FaQuestionCircle />
            <span>Quick Start Guide</span>
          </div>
        </ButtonItem>
      </div>
    </div>
  );
};

// Helper function to call plugin methods
async function callPluginMethod(method, args) {
  return window.DeckyPluginLoader.callServerMethod(method, args);
}

export default Main;