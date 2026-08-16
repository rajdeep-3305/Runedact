export const isMac =
  typeof navigator !== "undefined" && /Mac|iPhone|iPad/.test(navigator.platform);

export const runKeyLabel = isMac ? "⌘↵" : "Ctrl+↵";
