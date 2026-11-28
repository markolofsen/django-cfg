/**
 * Packages module exports
 */

export * from './definitions';
export * from './checker';
export {
  detectPackageManager,
  buildSingleInstallCommand,
  buildInstallCommand,
  installPackages,
  installPackagesWithProgress,
  checkAndInstallPackages,
  resetInstallerPreferences,
  type InstallOptions,
  type InstallProgress,
} from './installer';
export {
  getInstalledVersion,
  checkForUpdates,
  getOutdatedPackages,
  updatePackagesWithProgress,
  checkAndUpdatePackages,
  resetUpdaterPreferences,
  type PackageVersion,
  type UpdateOptions,
} from './updater';
