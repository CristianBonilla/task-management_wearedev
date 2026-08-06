import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.wearedev.taskmanager',
  appName: 'Task Manager',
  webDir: 'www',
  android: {
    // Allow cleartext traffic so the emulator can reach the local Django server.
    allowMixedContent: true,
  },
};

export default config;
