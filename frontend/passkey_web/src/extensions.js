// getTimeAndTimezone returns Time and Timezone
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

// Function registry
const functionRegistry = Object.freeze({
  timeInfo: getTimeAndTimezone,
  deviceInfo: getDeviceInfo,
});

// Executor
// Returns undefined if key does not exist
const executeFunctionByKey = (key, ...args) => functionRegistry[key?.trim()]?.(...args);

export const invokeExtensionFunctions = ({ customData = [] }) => {
  if (!Array.isArray(customData) || customData.length === 0) {
    return { customData: [] };
  }

  const response = customData.map(({ name }) => {
    try {
      return { name, value: executeFunctionByKey(name) };
    } catch (err) {
      return { name, error: String(err) };
    }
  });
  return { customData: response };
};
