import type { PlayerCopy } from "../types";

export const zh: PlayerCopy = {
  transport: {
    play: "播放",
    pause: "暂停",
    playFromCover: "播放此曲目",
    pauseFromCover: "暂停此曲目",
    dismiss: "停止并关闭",
    ended: "已结束",
  },
  controls: {
    seek: "跳转播放位置",
    volume: "音量",
    mute: "静音",
    unmute: "取消静音",
  },
  info: {
    label: "文件详情",
    artist: "艺术家",
    album: "专辑",
    machine: "机器",
    machineUnknown: "未知机器",
    copyPath: "复制路径",
    revealFolder: "打开文件夹",
    share: "复制链接",
  },
  dock: {
    label: "正在播放",
    expand: "打开播放器",
    openInFiles: "在文件中打开",
    showDetails: "显示详情",
    hideDetails: "隐藏详情",
  },
  stage: {
    label: "播放器",
    empty: "当前没有播放内容",
    minimize: "缩小到底栏",
  },
  failure: {
    machineUnreachable: "{{machine}} 已离线，播放已停止",
    machineUnreachableUnnamed: "该机器已离线，播放已停止",
    refused: "中继拒绝了此文件，播放已停止",
    unknown: "播放意外停止",
    blocked: "点击播放开始 — 浏览器需要先获得一次点击",
  },
};
