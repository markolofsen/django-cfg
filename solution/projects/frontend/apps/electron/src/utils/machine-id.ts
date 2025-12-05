/**
 * Machine ID utilities.
 *
 * Generates deterministic session ID based on machine fingerprint.
 * Same machine = same ID (persists across app restarts).
 */

import { createHash } from 'crypto';
import * as os from 'os';
import { execSync } from 'child_process';

/**
 * Get hardware UUID (platform-specific).
 */
function getHardwareUUID(): string {
  try {
    switch (os.platform()) {
      case 'darwin': {
        // macOS: system_profiler SPHardwareDataType | grep "Hardware UUID"
        const output = execSync(
          'system_profiler SPHardwareDataType | grep "Hardware UUID"',
          { encoding: 'utf8', timeout: 5000 }
        );
        const match = output.match(/Hardware UUID:\s*(.+)/);
        if (match) return match[1].trim();
        break;
      }
      case 'linux': {
        // Linux: /etc/machine-id or /var/lib/dbus/machine-id
        try {
          return execSync('cat /etc/machine-id', { encoding: 'utf8', timeout: 5000 }).trim();
        } catch {
          return execSync('cat /var/lib/dbus/machine-id', { encoding: 'utf8', timeout: 5000 }).trim();
        }
      }
      case 'win32': {
        // Windows: wmic csproduct get UUID
        const output = execSync('wmic csproduct get UUID', { encoding: 'utf8', timeout: 5000 });
        const lines = output.split('\n').filter(line => line.trim() && !line.includes('UUID'));
        if (lines.length > 0) return lines[0].trim();
        break;
      }
    }
  } catch {
    // Fall through to fallback
  }

  // Fallback: use hostname + username
  return `${os.hostname()}-${os.userInfo().username}`;
}

/**
 * Get primary MAC address.
 */
function getPrimaryMAC(): string {
  const interfaces = os.networkInterfaces();

  for (const [name, addrs] of Object.entries(interfaces)) {
    // Skip loopback and virtual interfaces
    if (name.startsWith('lo') || name.startsWith('veth') || name.startsWith('docker')) {
      continue;
    }

    for (const addr of addrs || []) {
      if (addr.mac && addr.mac !== '00:00:00:00:00:00') {
        return addr.mac;
      }
    }
  }

  return 'unknown';
}

/**
 * Generate machine fingerprint.
 * Uses only stable identifiers (no MAC - can change with VPN/network).
 */
export function getMachineFingerprint(): string {
  const parts = [
    getHardwareUUID(),
    os.hostname(),
    os.platform(),
    os.arch(),
  ];

  return parts.join('|');
}

/**
 * Generate deterministic session ID from machine fingerprint.
 * Returns UUID v4 format string.
 */
// Cache the session ID so it's computed once per process
let cachedSessionId: string | null = null;

export function getMachineSessionId(): string {
  if (cachedSessionId) {
    return cachedSessionId;
  }

  const fingerprint = getMachineFingerprint();
  const hash = createHash('sha256').update(fingerprint).digest('hex');

  // Format as UUID v4: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
  // where y is 8, 9, a, or b
  const uuid = [
    hash.slice(0, 8),
    hash.slice(8, 12),
    '4' + hash.slice(13, 16),  // version 4
    ((parseInt(hash.slice(16, 17), 16) & 0x3) | 0x8).toString(16) + hash.slice(17, 20),  // variant
    hash.slice(20, 32),
  ].join('-');

  cachedSessionId = uuid;
  return uuid;
}

/**
 * Get short machine ID (first 8 chars).
 */
export function getShortMachineId(): string {
  return getMachineSessionId().slice(0, 8);
}
