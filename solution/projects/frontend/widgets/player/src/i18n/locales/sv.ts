import type { PlayerCopy } from "../types";

export const sv: PlayerCopy = {
  transport: {
    play: "Spela",
    pause: "Paus",
    playFromCover: "Spela upp spåret",
    pauseFromCover: "Pausa spåret",
    dismiss: "Stoppa och stäng",
    ended: "Avslutad",
  },
  controls: {
    seek: "Sök i spåret",
    volume: "Volym",
    mute: "Stäng av ljudet",
    unmute: "Slå på ljudet",
  },
  info: {
    label: "Filinformation",
    artist: "Artist",
    album: "Album",
    machine: "Maskin",
    machineUnknown: "Okänd maskin",
    copyPath: "Kopiera sökväg",
    revealFolder: "Öppna mapp",
    share: "Kopiera länk",
  },
  dock: {
    label: "Spelas nu",
    expand: "Öppna spelaren",
    openInFiles: "Öppna i filer",
    showDetails: "Visa detaljer",
    hideDetails: "Dölj detaljer",
  },
  stage: {
    label: "Spelare",
    empty: "Inget spelas",
    minimize: "Förminska till listen",
  },
  failure: {
    machineUnreachable: "{{machine}} kopplades från — uppspelningen stoppades",
    machineUnreachableUnnamed: "Maskinen kopplades från — uppspelningen stoppades",
    refused: "Reläet avvisade den här filen — uppspelningen stoppades",
    unknown: "Uppspelningen stoppades oväntat",
    blocked: "Tryck på spela upp för att börja — din webbläsare kräver ett klick först",
  },
};
