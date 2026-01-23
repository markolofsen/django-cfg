/**
 * Admin Korean Translations
 */

import type { AdminTranslations } from './en';

export const ko: AdminTranslations = {
  nav: {
    home: '홈',
    dashboard: '대시보드',
    admin: '관리',
    profile: '프로필',
    settings: '설정',
  },
  pages: {
    home: {
      title: '환영합니다',
      subtitle: 'Django-CFG 관리자 대시보드',
    },
    dashboard: {
      title: '대시보드',
      welcome: '다시 오신 것을 환영합니다!',
    },
  },
  common: {
    loading: '로딩 중...',
    error: '오류가 발생했습니다',
    retry: '다시 시도',
    save: '저장',
    cancel: '취소',
    delete: '삭제',
    edit: '편집',
    create: '생성',
    search: '검색...',
    noResults: '결과 없음',
  },
};
