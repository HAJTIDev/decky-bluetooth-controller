import React from "react";
import { definePlugin } from "decky-frontend-lib";
import { FaGamepad } from "react-icons/fa";
// @ts-ignore
import Main from "../frontend/main";
import { IconType } from "react-icons";
//@ts-ignore
export default definePlugin(() => {
  return {
    title: <div>🎮 Deck Controller</div>,
    content: <Main />,
    icon: FaGamepad as IconType,
    onDismount: () => {
      // Cleanup if needed
    },
  };
});