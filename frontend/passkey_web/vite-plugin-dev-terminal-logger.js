// vite-plugin-dev-terminal-logger.js
import { WebSocketServer } from "ws";
export function devTerminalLogger() {
  let wss;

  return {
    name: "vite:dev-terminal-logger",
    apply: "serve",
    configureServer(server) {
      wss = new WebSocketServer({ noServer: true });

      server.httpServer.on("upgrade", (req, socket, head) => {
        if (req.url !== "/__devlog") return;
        wss.handleUpgrade(req, socket, head, (ws) => {
          ws.on("message", (raw) => {
            try {
              const {
                level = "INFO",
                message = "",
                meta = null,
                fileName = "<unknown>",
                functionName = "<unknown>",
              } = JSON.parse(raw);

              const stamp = new Date().toISOString().replace("T", " ").split(".")[0];
              const upperLevel = level.toUpperCase();
              const location = `[[CLIENT]] [${fileName}:${functionName}]`;
              const line = `${stamp} ${upperLevel} ${location} => ${message}`;

              switch (upperLevel) {
                case "ERROR":
                  console.error(line, meta || "");
                  break;
                case "WARN":
                  console.warn(line, meta || "");
                  break;
                case "DEBUG":
                  console.debug(line, meta || "");
                  break;
                default:
                  console.log(line, meta || "");
              }
            } catch (err) {
              console.error("[vite:dev-terminal-logger] Failed to parse log:", err);
            }
          });
        });
      });
    },
  };
}
