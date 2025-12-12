import React from "react";
import { definePlugin } from "decky-frontend-lib";
// @ts-ignore
import Main from "../frontend/main";
//@ts-ignore
export default definePlugin(() => {
  return {
    title: <div>🎮 Deck Controller</div>,
    content: <Main />,
    onDismount: () => {
      // Cleanup if needed
    },
  };
});