import type { PlayerCopy } from "../types";

export const de: PlayerCopy = {
  transport: {
    play: "Abspielen",
    pause: "Pause",
    playFromCover: "Titel abspielen",
    pauseFromCover: "Titel pausieren",
    dismiss: "Anhalten und schließen",
    ended: "Beendet",
  },
  controls: {
    seek: "Im Titel springen",
    volume: "Lautstärke",
    mute: "Stummschalten",
    unmute: "Stummschaltung aufheben",
  },
  info: {
    label: "Dateiinformationen",
    artist: "Künstler",
    album: "Album",
    machine: "Rechner",
    machineUnknown: "Unbekannter Rechner",
    copyPath: "Pfad kopieren",
    revealFolder: "Ordner öffnen",
    share: "Link kopieren",
  },
  dock: {
    label: "Aktuelle Wiedergabe",
    expand: "Player öffnen",
    openInFiles: "In Dateien öffnen",
    showDetails: "Details anzeigen",
    hideDetails: "Details ausblenden",
  },
  stage: {
    label: "Player",
    empty: "Es wird nichts abgespielt",
    minimize: "In die Fußzeile verkleinern",
  },
  failure: {
    machineUnreachable: "{{machine}} ist offline gegangen — Wiedergabe gestoppt",
    machineUnreachableUnnamed: "Der Rechner ist offline gegangen — Wiedergabe gestoppt",
    refused: "Das Relay hat diese Datei abgelehnt — Wiedergabe gestoppt",
    unknown: "Wiedergabe unerwartet gestoppt",
    blocked: "Zum Starten auf Wiedergabe klicken — Ihr Browser verlangt erst einen Klick",
  },
};
