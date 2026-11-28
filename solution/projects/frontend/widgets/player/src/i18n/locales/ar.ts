import type { PlayerCopy } from "../types";

export const ar: PlayerCopy = {
  transport: {
    play: "تشغيل",
    pause: "إيقاف مؤقت",
    playFromCover: "تشغيل المقطع",
    pauseFromCover: "إيقاف المقطع مؤقتًا",
    dismiss: "إيقاف وإغلاق",
    ended: "انتهى",
  },
  controls: {
    seek: "التنقل في المقطع",
    volume: "مستوى الصوت",
    mute: "كتم الصوت",
    unmute: "إلغاء كتم الصوت",
  },
  info: {
    label: "معلومات الملف",
    artist: "الفنان",
    album: "الألبوم",
    machine: "الجهاز",
    machineUnknown: "جهاز غير معروف",
    copyPath: "نسخ المسار",
    revealFolder: "فتح المجلد",
    share: "نسخ الرابط",
  },
  dock: {
    label: "قيد التشغيل الآن",
    expand: "فتح المشغّل",
    openInFiles: "فتح في الملفات",
    showDetails: "إظهار التفاصيل",
    hideDetails: "إخفاء التفاصيل",
  },
  stage: {
    label: "المشغّل",
    empty: "لا يوجد تشغيل حالياً",
    minimize: "تصغير إلى الشريط السفلي",
  },
  failure: {
    machineUnreachable: "{{machine}} أصبح غير متصل — توقف التشغيل",
    machineUnreachableUnnamed: "الجهاز أصبح غير متصل — توقف التشغيل",
    refused: "رفض المُرحِّل هذا الملف — توقف التشغيل",
    unknown: "توقف التشغيل بشكل غير متوقع",
    blocked: "اضغط على التشغيل للبدء — يحتاج المتصفّح إلى نقرة أولاً",
  },
};
