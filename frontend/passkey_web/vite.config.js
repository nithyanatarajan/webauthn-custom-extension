import { defineConfig } from "vite";
import { devTerminalLogger } from "./vite-plugin-dev-terminal-logger.js";

export default defineConfig({
  plugins: [devTerminalLogger()],
});
