import type { PlayerCopy } from "../types";

export const ru: PlayerCopy = {
  transport: {
    play: "Воспроизвести",
    pause: "Пауза",
    playFromCover: "Воспроизвести трек",
    pauseFromCover: "Приостановить трек",
    dismiss: "Остановить и закрыть",
    ended: "Завершено",
  },
  controls: {
    seek: "Перемотка",
    volume: "Громкость",
    mute: "Выключить звук",
    unmute: "Включить звук",
  },
  info: {
    label: "Сведения о файле",
    artist: "Исполнитель",
    album: "Альбом",
    machine: "Машина",
    machineUnknown: "Неизвестная машина",
    copyPath: "Скопировать путь",
    revealFolder: "Открыть папку",
    share: "Скопировать ссылку",
  },
  dock: {
    label: "Сейчас играет",
    expand: "Открыть плеер",
    openInFiles: "Открыть в файлах",
    showDetails: "Показать подробности",
    hideDetails: "Скрыть подробности",
  },
  stage: {
    label: "Плеер",
    empty: "Ничего не воспроизводится",
    minimize: "Свернуть в панель",
  },
  failure: {
    machineUnreachable: "{{machine}} — машина отключилась, воспроизведение остановлено",
    machineUnreachableUnnamed: "Машина отключилась, воспроизведение остановлено",
    refused: "Сервер отклонил этот файл, воспроизведение остановлено",
    unknown: "Воспроизведение неожиданно прервалось",
    blocked: "Нажмите «Воспроизвести» — браузер ждёт вашего действия",
  },
};
