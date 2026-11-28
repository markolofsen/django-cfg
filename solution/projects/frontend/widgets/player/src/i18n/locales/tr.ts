import type { PlayerCopy } from "../types";

export const tr: PlayerCopy = {
  transport: {
    play: "Oynat",
    pause: "Duraklat",
    playFromCover: "Bu parçayı çal",
    pauseFromCover: "Bu parçayı duraklat",
    dismiss: "Durdur ve kapat",
    ended: "Bitti",
  },
  controls: {
    seek: "Parçada gezin",
    volume: "Ses düzeyi",
    mute: "Sesi kapat",
    unmute: "Sesi aç",
  },
  info: {
    label: "Dosya ayrıntıları",
    artist: "Sanatçı",
    album: "Albüm",
    machine: "Makine",
    machineUnknown: "Bilinmeyen makine",
    copyPath: "Yolu kopyala",
    revealFolder: "Klasörü aç",
    share: "Bağlantıyı kopyala",
  },
  dock: {
    label: "Şimdi çalıyor",
    expand: "Oynatıcıyı aç",
    openInFiles: "Dosyalarda aç",
    showDetails: "Ayrıntıları göster",
    hideDetails: "Ayrıntıları gizle",
  },
  stage: {
    label: "Oynatıcı",
    empty: "Hiçbir şey çalmıyor",
    minimize: "Alt çubuğa küçült",
  },
  failure: {
    machineUnreachable: "{{machine}} çevrimdışı oldu — oynatma durduruldu",
    machineUnreachableUnnamed: "Makine çevrimdışı oldu — oynatma durduruldu",
    refused: "Relay bu dosyayı reddetti — oynatma durduruldu",
    unknown: "Oynatma beklenmedik şekilde durdu",
    blocked: "Başlatmak için oynata basın — tarayıcınız önce bir tıklama istiyor",
  },
};
