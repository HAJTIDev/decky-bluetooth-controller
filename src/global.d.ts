declare global {
  interface Window {
    DeckyPluginLoader: {
      callServerMethod: (method: string, args: any) => Promise<any>;
    };
    closeModal: () => void;
  }
}

export {};
