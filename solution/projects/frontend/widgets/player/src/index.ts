/**
 * One element that plays audio and video; three surfaces that borrow it.
 *
 * Every layer is importable alone by subpath, so a host mounting only a
 * transcript row does not pull the dock.
 */
export {
  MediaElement,
  type MediaElementProps,
  failureFromElement,
  failureFromPlayRejection,
} from "./element";
export {
  MediaButton,
  type MediaButtonProps,
  parentFolderLabel,
  PlayerDock,
  type PlayerDockProps,
  PlayerInfo,
  type PlayerInfoProps,
  PlayerStage,
  type PlayerStageProps,
  TrackCover,
  type TrackCoverProps,
} from "./surfaces";
export {
  canOpenStage,
  failureText,
  playedFraction,
  trackFromLink,
  type LinkResolution,
  type PlayerSurface,
  type PlayerView,
} from "./model";
export {
  PLAYER_DICTIONARIES,
  fill,
  usePlayerCopy,
  type ControlsCopy,
  type DockCopy,
  type FailureCopy,
  type InfoCopy,
  type PlayerCopy,
  type StageCopy,
  type TransportCopy,
} from "./i18n";
export {
  machineTrack,
  mediaTrackId,
  mediaTitleFromPath,
  type MachineTrackInput,
  type MediaDetail,
  type MediaFailure,
  type MediaKind,
  type MediaTrack,
} from "./domain";
