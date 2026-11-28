import type { PlayerCopy } from "../types";

/**
 * English, the schema of record. Every other dictionary is typed against
 * `PlayerCopy`, so this file decides what the others must carry.
 */
export const en: PlayerCopy = {
  transport: {
    play: "Play",
    pause: "Pause",
    playFromCover: "Play this track",
    pauseFromCover: "Pause this track",
    dismiss: "Stop and close",
    ended: "Finished",
  },
  controls: {
    seek: "Seek",
    volume: "Volume",
    mute: "Mute",
    unmute: "Unmute",
  },
  info: {
    label: "File details",
    artist: "Artist",
    album: "Album",
    machine: "Machine",
    machineUnknown: "Unknown machine",
    copyPath: "Copy path",
    revealFolder: "Open folder",
    share: "Copy link",
  },
  dock: {
    label: "Now playing",
    expand: "Open player",
    openInFiles: "Open in files",
    showDetails: "Show details",
    hideDetails: "Hide details",
  },
  stage: {
    label: "Player",
    empty: "Nothing is playing",
    minimize: "Minimize to footer",
  },
  failure: {
    machineUnreachable: "{{machine}} went offline — playback stopped",
    machineUnreachableUnnamed: "The machine went offline — playback stopped",
    refused: "The relay refused this file — playback stopped",
    unknown: "Playback stopped unexpectedly",
    blocked: "Press play to start — your browser needs a click first",
  },
};
