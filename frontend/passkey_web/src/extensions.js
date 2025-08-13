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

//  This is a call to extension server when there is a destination given as EXTN. This is a sample implementation
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
const getFunctionRegistryElement = (key) => functionRegistry[key?.trim()];

const executeFunctionByKey = (key, ...args) => getFunctionRegistryElement(key)?.(...args);

// invokeExtensionFunctions is used to invoke extension functions registered in the functionRegistry.
export const invokeExtensionFunctions = ({ customData = [] }) => {
  if (!Array.isArray(customData) || customData.length === 0) {
    return { customData: [] };
  }

  const response = customData.map(({ name, metadata = {} }) => {
    if (typeof getFunctionRegistryElement(name) !== 'function') {
      return { name, error: `Unknown extension "${name}"` };
    }
    try {
      return { name, value: executeFunctionByKey(name, metadata) };
    } catch (err) {
      return { name, error: String(err) };
    }
  });

  return { customData: response };
};
