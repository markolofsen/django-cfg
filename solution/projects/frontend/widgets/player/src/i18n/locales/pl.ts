import type { PlayerCopy } from "../types";

export const pl: PlayerCopy = {
  transport: {
    play: "Odtwórz",
    pause: "Pauza",
    playFromCover: "Odtwórz ten utwór",
    pauseFromCover: "Wstrzymaj ten utwór",
    dismiss: "Zatrzymaj i zamknij",
    ended: "Zakończono",
  },
  controls: {
    seek: "Przewiń utwór",
    volume: "Głośność",
    mute: "Wycisz",
    unmute: "Włącz dźwięk",
  },
  info: {
    label: "Szczegóły pliku",
    artist: "Wykonawca",
    album: "Album",
    machine: "Maszyna",
    machineUnknown: "Nieznana maszyna",
    copyPath: "Kopiuj ścieżkę",
    revealFolder: "Otwórz folder",
    share: "Kopiuj link",
  },
  dock: {
    label: "Teraz odtwarzane",
    expand: "Otwórz odtwarzacz",
    openInFiles: "Otwórz w plikach",
    showDetails: "Pokaż szczegóły",
    hideDetails: "Ukryj szczegóły",
  },
  stage: {
    label: "Odtwarzacz",
    empty: "Nic nie jest odtwarzane",
    minimize: "Zwiń do paska",
  },
  failure: {
    machineUnreachable: "{{machine}} przeszła w tryb offline — odtwarzanie zatrzymane",
    machineUnreachableUnnamed: "Maszyna przeszła w tryb offline — odtwarzanie zatrzymane",
    refused: "Relay odrzucił ten plik — odtwarzanie zatrzymane",
    unknown: "Odtwarzanie nieoczekiwanie się zatrzymało",
    blocked: "Naciśnij odtwarzanie, aby zacząć — przeglądarka wymaga najpierw kliknięcia",
  },
};
