import type { PlayerCopy } from "../types";

export const ko: PlayerCopy = {
  transport: {
    play: "재생",
    pause: "일시정지",
    playFromCover: "이 트랙 재생",
    pauseFromCover: "이 트랙 일시정지",
    dismiss: "중지하고 닫기",
    ended: "완료됨",
  },
  controls: {
    seek: "재생 위치 이동",
    volume: "음량",
    mute: "음소거",
    unmute: "음소거 해제",
  },
  info: {
    label: "파일 정보",
    artist: "아티스트",
    album: "앨범",
    machine: "머신",
    machineUnknown: "알 수 없는 머신",
    copyPath: "경로 복사",
    revealFolder: "폴더 열기",
    share: "링크 복사",
  },
  dock: {
    label: "재생 중",
    expand: "플레이어 열기",
    openInFiles: "파일에서 열기",
    showDetails: "세부 정보 표시",
    hideDetails: "세부 정보 숨기기",
  },
  stage: {
    label: "플레이어",
    empty: "재생 중인 항목이 없습니다",
    minimize: "하단 바로 축소",
  },
  failure: {
    machineUnreachable: "{{machine}}이(가) 오프라인 상태가 되어 재생이 중지되었습니다",
    machineUnreachableUnnamed: "머신이 오프라인 상태가 되어 재생이 중지되었습니다",
    refused: "릴레이가 이 파일을 거부하여 재생이 중지되었습니다",
    unknown: "재생이 예기치 않게 중지되었습니다",
    blocked: "재생을 눌러 시작하세요 — 브라우저가 먼저 클릭을 요구합니다",
  },
};
