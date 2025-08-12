// devLogger.js
const isDev = import.meta.env?.DEV;
let ws;

/**
 * Extract caller info from the stack trace.
 */
function getCallerInfo() {
  const err = new Error();
  const stack = err.stack?.split('\n') || [];
  // Typical stack: ["Error", " at functionName (fileURL:line:col)", ...]
  const callerLine = stack[3] || ''; // index 3 skips getCallerInfo + devLog itself
  const match =
    callerLine.match(/at\s+(.*?)\s+\((.*):(\d+):(\d+)\)/) ||
    callerLine.match(/at\s+(.*):(\d+):(\d+)/);

  if (match) {
    const functionName = match[1] || '<anonymous>';
    const filePath = match[2] || match[1];
    const fileName = filePath.split('/').pop();
    return { functionName, fileName };
  }
  return { functionName: '<unknown>', fileName: '<unknown>' };
}

/**
 * Initialize the dev terminal logger.
 */
export function initDevLogger() {
  if (!isDev) return;
  ws = new WebSocket(`${location.origin.replace(/^http/, 'ws')}/__devlog`);
}

/**
 * Send a log message to the dev server.
 * @param {"debug"|"info"|"warn"|"error"} level
 * @param {string} message
 * @param {any} [meta]
 */
export function devLog(level, message, meta) {
  if (!isDev || !ws || ws.readyState !== WebSocket.OPEN) return;
  const { functionName, fileName } = getCallerInfo();
  ws.send(JSON.stringify({ level, message, meta, fileName, functionName }));
}
