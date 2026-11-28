import type { PlayerCopy } from "../types";

export const nl: PlayerCopy = {
  transport: {
    play: "Afspelen",
    pause: "Pauze",
    playFromCover: "Dit nummer afspelen",
    pauseFromCover: "Dit nummer pauzeren",
    dismiss: "Stoppen en sluiten",
    ended: "Voltooid",
  },
  controls: {
    seek: "Door het nummer bewegen",
    volume: "Volume",
    mute: "Dempen",
    unmute: "Dempen opheffen",
  },
  info: {
    label: "Bestandsgegevens",
    artist: "Artiest",
    album: "Album",
    machine: "Machine",
    machineUnknown: "Onbekende machine",
    copyPath: "Pad kopiëren",
    revealFolder: "Map openen",
    share: "Link kopiëren",
  },
  dock: {
    label: "Speelt nu af",
    expand: "Speler openen",
    openInFiles: "Openen in bestanden",
    showDetails: "Details tonen",
    hideDetails: "Details verbergen",
  },
  stage: {
    label: "Speler",
    empty: "Er wordt niets afgespeeld",
    minimize: "Verkleinen naar de balk",
  },
  failure: {
    machineUnreachable: "{{machine}} is offline gegaan — afspelen gestopt",
    machineUnreachableUnnamed: "De machine is offline gegaan — afspelen gestopt",
    refused: "De relay heeft dit bestand geweigerd — afspelen gestopt",
    unknown: "Afspelen is onverwacht gestopt",
    blocked: "Druk op afspelen om te starten — je browser wil eerst een klik",
  },
};
