import type { PlayerCopy } from "../types";

export const da: PlayerCopy = {
  transport: {
    play: "Afspil",
    pause: "Pause",
    playFromCover: "Afspil nummeret",
    pauseFromCover: "Sæt nummeret på pause",
    dismiss: "Stop og luk",
    ended: "Afsluttet",
  },
  controls: {
    seek: "Søg i sporet",
    volume: "Lydstyrke",
    mute: "Slå lyden fra",
    unmute: "Slå lyden til",
  },
  info: {
    label: "Filoplysninger",
    artist: "Kunstner",
    album: "Album",
    machine: "Maskine",
    machineUnknown: "Ukendt maskine",
    copyPath: "Kopiér sti",
    revealFolder: "Åbn mappe",
    share: "Kopiér link",
  },
  dock: {
    label: "Afspilles nu",
    expand: "Åbn afspilleren",
    openInFiles: "Åbn i filer",
    showDetails: "Vis detaljer",
    hideDetails: "Skjul detaljer",
  },
  stage: {
    label: "Afspiller",
    empty: "Der afspilles ikke noget",
    minimize: "Formindsk til linjen",
  },
  failure: {
    machineUnreachable: "{{machine}} gik offline — afspilning stoppet",
    machineUnreachableUnnamed: "Maskinen gik offline — afspilning stoppet",
    refused: "Relayet afviste denne fil — afspilning stoppet",
    unknown: "Afspilningen stoppede uventet",
    blocked: "Tryk på afspil for at starte — din browser kræver et klik først",
  },
};
