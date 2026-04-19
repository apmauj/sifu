import React from 'react';
import { useI18n } from '../contexts/I18nContext';

const BuildInfoFooter = () => {
  const { t } = useI18n();
  const rawVersion = import.meta.env.VITE_APP_VERSION || '-';
  const version = rawVersion.startsWith('v') ? rawVersion : `v${rawVersion}`;
  const releaseUrl = import.meta.env.VITE_APP_RELEASE_URL || 'https://github.com/apmauj/sifu/releases';
  const sha = import.meta.env.VITE_APP_BUILD_SHA || '-';
  const date = import.meta.env.VITE_APP_BUILD_DATE || '-';
  return (
    <div className="mt-8 text-center text-[11px] text-neutral-500 dark:text-neutral-400 select-none">
      <span className="font-medium">{t('footer.sifu_title') || 'SIFU'}</span>
      {` · `}
      <a
        href={releaseUrl}
        target="_blank"
        rel="noreferrer noopener"
        className="font-medium text-primary-600 hover:underline dark:text-primary-400"
      >
        {version}
      </a>
      {` · build ${sha.substring(0,7)} · ${date}`}
    </div>
  );
};

export default BuildInfoFooter;