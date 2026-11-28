import type { PlayerCopy } from "../types";

export const no: PlayerCopy = {
  transport: {
    play: "Spill av",
    pause: "Pause",
    playFromCover: "Spill av sporet",
    pauseFromCover: "Sett sporet på pause",
    dismiss: "Stopp og lukk",
    ended: "Fullført",
  },
  controls: {
    seek: "Naviger i sporet",
    volume: "Volum",
    mute: "Slå av lyden",
    unmute: "Slå på lyden",
  },
  info: {
    label: "Fildetaljer",
    artist: "Artist",
    album: "Album",
    machine: "Maskin",
    machineUnknown: "Ukjent maskin",
    copyPath: "Kopier sti",
    revealFolder: "Åpne mappe",
    share: "Kopier lenke",
  },
  dock: {
    label: "Spilles av nå",
    expand: "Åpne spilleren",
    openInFiles: "Åpne i filer",
    showDetails: "Vis detaljer",
    hideDetails: "Skjul detaljer",
  },
  stage: {
    label: "Spiller",
    empty: "Ingenting spilles av",
    minimize: "Forminsk til linjen",
  },
  failure: {
    machineUnreachable: "{{machine}} kobler fra — avspilling stoppet",
    machineUnreachableUnnamed: "Maskinen kobler fra — avspilling stoppet",
    refused: "Reléet avviste denne filen — avspilling stoppet",
    unknown: "Avspillingen stoppet uventet",
    blocked: "Trykk på spill av for å starte — nettleseren krever et klikk først",
  },
};
