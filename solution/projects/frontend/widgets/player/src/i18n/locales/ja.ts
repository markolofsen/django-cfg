import type { PlayerCopy } from "../types";

export const ja: PlayerCopy = {
  transport: {
    play: "再生",
    pause: "一時停止",
    playFromCover: "この曲を再生",
    pauseFromCover: "この曲を一時停止",
    dismiss: "停止して閉じる",
    ended: "終了しました",
  },
  controls: {
    seek: "再生位置",
    volume: "音量",
    mute: "ミュート",
    unmute: "ミュート解除",
  },
  info: {
    label: "ファイル情報",
    artist: "アーティスト",
    album: "アルバム",
    machine: "マシン",
    machineUnknown: "不明なマシン",
    copyPath: "パスをコピー",
    revealFolder: "フォルダを開く",
    share: "リンクをコピー",
  },
  dock: {
    label: "再生中",
    expand: "プレーヤーを開く",
    openInFiles: "ファイルで開く",
    showDetails: "詳細を表示",
    hideDetails: "詳細を非表示",
  },
  stage: {
    label: "プレーヤー",
    empty: "再生中の項目はありません",
    minimize: "フッターに縮小",
  },
  failure: {
    machineUnreachable: "{{machine}} がオフラインになりました。再生を停止しました",
    machineUnreachableUnnamed: "マシンがオフラインになりました。再生を停止しました",
    refused: "リレーがこのファイルを拒否しました。再生を停止しました",
    unknown: "再生が予期せず停止しました",
    blocked: "再生を押して開始してください — ブラウザーが操作を求めています",
  },
};
