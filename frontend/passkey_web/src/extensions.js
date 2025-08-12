// getTimeAndTimezone returns Time and Timezone
import { callExtension } from './api/extensions.js';

const getTimeAndTimezone = () => ({
  time: new Date().toISOString(),
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
});

// getDeviceInfo returns Device Information
const getDeviceInfo = () => ({
  userAgent: navigator.userAgent,
  language: navigator.language,
  online: navigator.onLine,
  cookieEnabled: navigator.cookieEnabled,
  screen: { width: screen.width, height: screen.height },
});

const someOtherExtension = async (metadata) => {
  if (metadata.destination && metadata.destination === 'EXTN' && metadata.path) {
    const path = `extensions/${metadata.path}`;
    const payload = { name: 'someOtherExtension', metadata };
    await callExtension(path, payload);
    return { status: 'ok', URL: path };
  }

  return { status: 'error', Metadata: JSON.stringify(metadata) };
};

// Function registry
const functionRegistry = Object.freeze({
  timeInfo: getTimeAndTimezone,
  deviceInfo: getDeviceInfo,
  someOtherExtension,
});

// Executor
// Returns undefined if key does not exist
const executeFunctionByKey = (key, ...args) => functionRegistry[key?.trim()]?.(...args);

export const invokeExtensionFunctions = ({ customData = [] }) => {
  if (!Array.isArray(customData) || customData.length === 0) {
    return { customData: [] };
  }

  const response = customData.map(({ name, metadata = {} }) => {
    try {
      return { name, value: executeFunctionByKey(name, metadata) };
    } catch (err) {
      return { name, error: String(err) };
    }
  });

  return { customData: response };
};
