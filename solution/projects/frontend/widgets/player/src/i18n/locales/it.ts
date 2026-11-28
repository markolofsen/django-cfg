import type { PlayerCopy } from "../types";

export const it: PlayerCopy = {
  transport: {
    play: "Riproduci",
    pause: "Pausa",
    playFromCover: "Riproduci il brano",
    pauseFromCover: "Metti in pausa il brano",
    dismiss: "Ferma e chiudi",
    ended: "Terminato",
  },
  controls: {
    seek: "Scorri il brano",
    volume: "Volume",
    mute: "Disattiva l'audio",
    unmute: "Riattiva l'audio",
  },
  info: {
    label: "Dettagli del file",
    artist: "Artista",
    album: "Album",
    machine: "Macchina",
    machineUnknown: "Macchina sconosciuta",
    copyPath: "Copia percorso",
    revealFolder: "Apri cartella",
    share: "Copia link",
  },
  dock: {
    label: "In riproduzione",
    expand: "Apri il lettore",
    openInFiles: "Apri nei file",
    showDetails: "Mostra dettagli",
    hideDetails: "Nascondi dettagli",
  },
  stage: {
    label: "Lettore",
    empty: "Non è in riproduzione nulla",
    minimize: "Riduci nella barra",
  },
  failure: {
    machineUnreachable: "{{machine}} è andata offline: riproduzione interrotta",
    machineUnreachableUnnamed: "La macchina è andata offline: riproduzione interrotta",
    refused: "Il relay ha rifiutato questo file: riproduzione interrotta",
    unknown: "Riproduzione interrotta in modo imprevisto",
    blocked: "Premi riproduci per iniziare: il browser richiede prima un clic",
  },
};
