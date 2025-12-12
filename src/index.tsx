import { definePlugin } from "decky-frontend-lib";
import { FaGamepad } from "react-icons/fa";
import Main from "./main";

export default definePlugin(() => {
  return {
    title: <div>🎮 Deck Controller</div>,
    content: <Main />,
    icon: <FaGamepad />,
    onDismount: () => {
      // Cleanup if needed
    },
  };
});