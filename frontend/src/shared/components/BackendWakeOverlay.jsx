import { useState, useEffect } from 'react';
import { useI18n } from '../contexts/I18nContext';

const BackendWakeOverlay = ({ isVisible, onDismiss }) => {
  const { t } = useI18n();
  const [fadeOut, setFadeOut] = useState(false);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!isVisible) {
      setFadeOut(false);
      setElapsed(0);
      return;
    }
    const interval = setInterval(() => {
      setElapsed((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [isVisible]);

  if (!isVisible && !fadeOut) return null;

  const handleDismiss = () => {
    setFadeOut(true);
    setTimeout(() => {
      setFadeOut(false);
      if (onDismiss) onDismiss();
    }, 300);
  };

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center transition-opacity duration-300
        ${fadeOut ? 'opacity-0 pointer-events-none' : 'opacity-100'}
        bg-neutral-950/90 backdrop-blur-md`}
      role="dialog"
      aria-label={t('wake.title', 'Waking up the server')}
    >
      <div className="bg-white dark:bg-neutral-800 rounded-2xl shadow-2xl p-8 max-w-sm mx-4 text-center">
        <div className="mb-4 flex justify-center">
          <div className="relative">
            <div className="w-16 h-16 rounded-full border-4 border-primary-200 dark:border-primary-700" />
            <div className="absolute inset-0 w-16 h-16 rounded-full border-4 border-transparent border-t-primary-600 dark:border-t-primary-400 animate-spin" />
          </div>
        </div>

        <h2 className="text-lg font-semibold text-neutral-800 dark:text-neutral-100 mb-2">
          {t('wake.title', 'Waking up the server')}
        </h2>

        <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">
          {t('wake.description',
            'The backend is starting up from sleep mode. On the free tier this can take up to a minute on the first request.'
          )}
        </p>

        {elapsed > 10 && (
          <p className="text-xs text-neutral-400 dark:text-neutral-500 mb-4">
            {t('wake.elapsed', `${elapsed}s elapsed...`).replace('{elapsed}', elapsed)}
          </p>
        )}

        {elapsed > 60 && (
          <p className="text-xs text-amber-500 dark:text-amber-400 mb-4">
            {t('wake.takingLong',
              'This is taking longer than usual. The service may be under load.')}
          </p>
        )}

        <button
          onClick={handleDismiss}
          className="text-xs text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 underline transition-colors"
        >
          {t('wake.dismiss', 'Dismiss')}
        </button>
      </div>
    </div>
  );
};

export default BackendWakeOverlay;
