import type { PlayerCopy } from "../types";

export const fr: PlayerCopy = {
  transport: {
    play: "Lire",
    pause: "Pause",
    playFromCover: "Lire ce morceau",
    pauseFromCover: "Mettre ce morceau en pause",
    dismiss: "Arrêter et fermer",
    ended: "Terminé",
  },
  controls: {
    seek: "Se déplacer dans la piste",
    volume: "Volume",
    mute: "Couper le son",
    unmute: "Rétablir le son",
  },
  info: {
    label: "Détails du fichier",
    artist: "Artiste",
    album: "Album",
    machine: "Machine",
    machineUnknown: "Machine inconnue",
    copyPath: "Copier le chemin",
    revealFolder: "Ouvrir le dossier",
    share: "Copier le lien",
  },
  dock: {
    label: "Lecture en cours",
    expand: "Ouvrir le lecteur",
    openInFiles: "Ouvrir dans les fichiers",
    showDetails: "Afficher les détails",
    hideDetails: "Masquer les détails",
  },
  stage: {
    label: "Lecteur",
    empty: "Aucune lecture en cours",
    minimize: "Réduire dans la barre",
  },
  failure: {
    machineUnreachable: "{{machine}} est hors ligne — lecture arrêtée",
    machineUnreachableUnnamed: "La machine est hors ligne — lecture arrêtée",
    refused: "Le relais a refusé ce fichier — lecture arrêtée",
    unknown: "La lecture s'est arrêtée de façon inattendue",
    blocked: "Appuyez sur lecture pour démarrer — votre navigateur exige d'abord un clic",
  },
};
