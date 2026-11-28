import type { PlayerCopy } from "../types";

export const ptBR: PlayerCopy = {
  transport: {
    play: "Reproduzir",
    pause: "Pausar",
    playFromCover: "Reproduzir esta faixa",
    pauseFromCover: "Pausar esta faixa",
    dismiss: "Parar e fechar",
    ended: "Concluído",
  },
  controls: {
    seek: "Navegar na faixa",
    volume: "Volume",
    mute: "Silenciar",
    unmute: "Ativar o som",
  },
  info: {
    label: "Detalhes do arquivo",
    artist: "Artista",
    album: "Álbum",
    machine: "Máquina",
    machineUnknown: "Máquina desconhecida",
    copyPath: "Copiar caminho",
    revealFolder: "Abrir pasta",
    share: "Copiar link",
  },
  dock: {
    label: "Tocando agora",
    expand: "Abrir o player",
    openInFiles: "Abrir nos arquivos",
    showDetails: "Mostrar detalhes",
    hideDetails: "Ocultar detalhes",
  },
  stage: {
    label: "Player",
    empty: "Nada está tocando",
    minimize: "Minimizar para a barra",
  },
  failure: {
    machineUnreachable: "{{machine}} ficou offline — reprodução interrompida",
    machineUnreachableUnnamed: "A máquina ficou offline — reprodução interrompida",
    refused: "O relay recusou este arquivo — reprodução interrompida",
    unknown: "A reprodução parou inesperadamente",
    blocked: "Toque em reproduzir para começar — seu navegador precisa de um clique antes",
  },
};
