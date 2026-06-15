import React, { useState, useEffect, useRef, useCallback } from 'react';

/**
 * BackendWakeOverlay
 *
 * Full-screen overlay that shows during Render cold starts.
 * Displays progressive stages: connecting → waking → loading → ready.
 * Auto-dismisses with a fade-out once the first API call succeeds.
 *
 * Usage:
 *   <BackendWakeOverlay isVisible={show} onDismiss={() => setShow(false)} />
 */
const BackendWakeOverlay = ({ isVisible, onDismiss }) => {
  const [stage, setStage] = useState(0);
  const [fadeOut, setFadeOut] = useState(false);
  const timerRef = useRef(null);
  const dismissedRef = useRef(false);

  // Stages: message key, duration (ms) before advancing
  const stages = [
    { key: 'connecting', duration: 3000 },
    { key: 'waking', duration: 15000 },
    { key: 'loading', duration: null }, // stays until backend responds
  ];

  // Auto-advance through stages
  useEffect(() => {
    if (!isVisible) {
      setStage(0);
      setFadeOut(false);
      dismissedRef.current = false;
      return;
    }

    setStage(0);
    dismissedRef.current = false;

    const scheduleNext = (currentStage) => {
      if (currentStage >= stages.length - 1) return; // last stage stays
      const s = stages[currentStage];
      if (!s.duration) return; // no auto-advance from loading stage
      timerRef.current = setTimeout(() => {
        setStage((prev) => Math.min(prev + 1, stages.length - 1));
        scheduleNext(currentStage + 1);
      }, s.duration);
    };

    scheduleNext(0);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isVisible]);

  // Dismiss with fade-out animation
  const dismiss = useCallback(() => {
    if (dismissedRef.current) return;
    dismissedRef.current = true;
    setFadeOut(true);
    setTimeout(() => {
      onDismiss?.();
    }, 600);
  }, [onDismiss]);

  // Auto-dismiss when visibility goes false
  useEffect(() => {
    if (!isVisible && !dismissedRef.current) {
      dismiss();
    }
  }, [isVisible, dismiss]);

  if (!isVisible && !fadeOut) return null;

  const currentStage = stages[Math.min(stage, stages.length - 1)];

  return (
    <div
      className={`
        fixed inset-0 z-[9999]
        flex items-center justify-center
        transition-opacity duration-500 ease-out
        ${fadeOut ? 'opacity-0 pointer-events-none' : 'opacity-100'}
      `}
      role="alert"
      aria-live="polite"
      aria-label="Iniciando sistema"
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-gradient-to-br from-neutral-900 via-neutral-800 to-neutral-900" />

      {/* Subtle grid pattern */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)',
          backgroundSize: '40px 40px',
        }}
      />

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center gap-8 px-6">
        {/* Animated logo / icon */}
        <div className="relative">
          {/* Outer pulse ring */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div
              className="w-24 h-24 rounded-full border-2 border-primary-500/30 animate-ping"
              style={{ animationDuration: '2s' }}
            />
          </div>
          {/* Inner spinning ring */}
          <div className="w-20 h-20 rounded-full border-[3px] border-t-primary-400 border-r-primary-400/30 border-b-primary-400/10 border-l-primary-400/30 animate-spin" />
          {/* Center dot */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-primary-400 animate-pulse" />
          </div>
        </div>

        {/* App name */}
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white tracking-wide mb-1">
            SIFU
          </h1>
          <p className="text-sm text-neutral-400">
            Sistema de Índices Financieros del Uruguay
          </p>
        </div>

        {/* Stage message */}
        <div className="text-center min-h-[60px] flex flex-col items-center gap-3">
          <p
            key={currentStage.key}
            className="text-lg font-medium text-neutral-200 animate-fade-in"
          >
            {getMessage(currentStage.key)}
          </p>

          {/* Animated dots */}
          <div className="flex items-center gap-1.5">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-1.5 h-1.5 rounded-full bg-primary-400 animate-bounce"
                style={{ animationDelay: `${i * 200}ms`, animationDuration: '1s' }}
              />
            ))}
          </div>
        </div>

        {/* Progress steps indicator */}
        <div className="flex items-center gap-3 mt-2">
          {stages.map((s, i) => (
            <React.Fragment key={s.key}>
              <div
                className={`
                  w-2 h-2 rounded-full transition-all duration-500
                  ${i < stage ? 'bg-primary-400 scale-100' : ''}
                  ${i === stage ? 'bg-primary-300 scale-125 ring-2 ring-primary-400/30' : ''}
                  ${i > stage ? 'bg-neutral-600 scale-100' : ''}
                `}
              />
              {i < stages.length - 1 && (
                <div
                  className={`
                    w-8 h-px transition-colors duration-500
                    ${i < stage ? 'bg-primary-400' : 'bg-neutral-700'}
                  `}
                />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Hint text */}
        <p className="text-xs text-neutral-500 mt-4 max-w-xs text-center">
          El servidor entra en modo reposo tras 15 minutos de inactividad.
          La primera carga puede tardar hasta un minuto.
        </p>
      </div>
    </div>
  );
};

/**
 * Get localized message for a stage key
 * Uses inline translations to avoid i18n dependency (overlay shows before i18n loads)
 */
function getMessage(stageKey) {
  // Simple browser language detection
  const lang = (typeof navigator !== 'undefined' && navigator.language?.slice(0, 2)) || 'es';

  const messages = {
    connecting: {
      es: 'Conectando al servidor...',
      en: 'Connecting to server...',
      pt: 'Conectando ao servidor...',
    },
    waking: {
      es: 'Despertando sistema...',
      en: 'Waking up server...',
      pt: 'Iniciando servidor...',
    },
    loading: {
      es: 'Obteniendo datos financieros...',
      en: 'Loading financial data...',
      pt: 'Carregando dados financeiros...',
    },
  };

  return messages[stageKey]?.[lang] || messages[stageKey]?.es || 'Cargando...';
}

export default BackendWakeOverlay;
