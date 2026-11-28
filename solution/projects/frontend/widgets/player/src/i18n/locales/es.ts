import type { PlayerCopy } from "../types";

export const es: PlayerCopy = {
  transport: {
    play: "Reproducir",
    pause: "Pausa",
    playFromCover: "Reproducir la pista",
    pauseFromCover: "Pausar la pista",
    dismiss: "Detener y cerrar",
    ended: "Finalizado",
  },
  controls: {
    seek: "Buscar en la pista",
    volume: "Volumen",
    mute: "Silenciar",
    unmute: "Activar el sonido",
  },
  info: {
    label: "Detalles del archivo",
    artist: "Artista",
    album: "Álbum",
    machine: "Máquina",
    machineUnknown: "Máquina desconocida",
    copyPath: "Copiar ruta",
    revealFolder: "Abrir carpeta",
    share: "Copiar enlace",
  },
  dock: {
    label: "Reproduciendo ahora",
    expand: "Abrir reproductor",
    openInFiles: "Abrir en archivos",
    showDetails: "Mostrar detalles",
    hideDetails: "Ocultar detalles",
  },
  stage: {
    label: "Reproductor",
    empty: "No se está reproduciendo nada",
    minimize: "Minimizar a la barra",
  },
  failure: {
    machineUnreachable: "{{machine}} se desconectó: reproducción detenida",
    machineUnreachableUnnamed: "La máquina se desconectó: reproducción detenida",
    refused: "El relé rechazó este archivo: reproducción detenida",
    unknown: "La reproducción se detuvo inesperadamente",
    blocked: "Pulsa reproducir para empezar: tu navegador necesita un clic primero",
  },
};
