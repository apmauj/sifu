import React from 'react';
import { useI18n } from '../contexts/I18nContext';

const BuildInfoFooter = () => {
  const { t } = useI18n();
  const sha = import.meta.env.VITE_APP_BUILD_SHA || '-';
  const date = import.meta.env.VITE_APP_BUILD_DATE || '-';
  return (
    <div className="mt-8 text-center text-[11px] text-neutral-500 dark:text-neutral-400 select-none">
      <span className="font-medium">{t('footer.sifu_title') || 'SIFU'}</span>
      {` · build ${sha.substring(0,7)} · ${date}`}
    </div>
  );
};

export default BuildInfoFooter;