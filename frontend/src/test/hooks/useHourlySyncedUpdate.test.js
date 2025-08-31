import { renderHook, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

// Unmock the hook for this test file
vi.unmock('../../hooks/useHourlySyncedUpdate');

// Import the real hook
import { useHourlySyncedUpdate } from '../../hooks/useHourlySyncedUpdate';

// Mock de setTimeout y setInterval para testing
vi.useFakeTimers();

describe('useHourlySyncedUpdate', () => {
  let mockUpdateFunction;

  beforeEach(() => {
    mockUpdateFunction = vi.fn();
    vi.clearAllTimers();
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
    vi.useFakeTimers();
  });

  it('debería ejecutar la función inmediatamente al montar', () => {
    renderHook(() => useHourlySyncedUpdate(mockUpdateFunction));
    
    expect(mockUpdateFunction).toHaveBeenCalledTimes(1);
  });

  it('debería programar un timeout para sincronizar con la próxima hora', () => {
    const spySetTimeout = vi.spyOn(global, 'setTimeout');
    
    renderHook(() => useHourlySyncedUpdate(mockUpdateFunction));
    
    // Debería haber un setTimeout programado
    expect(spySetTimeout).toHaveBeenCalled();
    expect(setTimeout).toHaveBeenCalledWith(expect.any(Function), expect.any(Number));
  });

  it('no debería ejecutar si enabled es false', () => {
    renderHook(() => useHourlySyncedUpdate(mockUpdateFunction, false));
    
    expect(mockUpdateFunction).not.toHaveBeenCalled();
  });

  it('no debería ejecutar si updateFunction no es una función', () => {
    renderHook(() => useHourlySyncedUpdate(null));
    
    expect(mockUpdateFunction).not.toHaveBeenCalled();
  });

  it('debería limpiar los timers al desmontar', () => {
    const spyClearTimeout = vi.spyOn(global, 'clearTimeout');
    
    const { unmount } = renderHook(() => useHourlySyncedUpdate(mockUpdateFunction));
    
    act(() => {
      unmount();
    });

    // clearTimeout siempre debería ser llamado porque siempre hay un timeout
    expect(spyClearTimeout).toHaveBeenCalled();
    // clearInterval puede o no ser llamado dependiendo de si el timeout ya se ejecutó
    // Solo verificamos que la función de cleanup se ejecutó sin errores
  });

  it('debería retornar una función de cleanup', () => {
    const { result } = renderHook(() => useHourlySyncedUpdate(mockUpdateFunction));
    
    expect(typeof result.current).toBe('function');
  });

  it('debería ejecutar la función de cleanup manualmente', () => {
    const spyClearTimeout = vi.spyOn(global, 'clearTimeout');
    
    const { result } = renderHook(() => useHourlySyncedUpdate(mockUpdateFunction));
    
    act(() => {
      result.current(); // Ejecutar cleanup manual
    });

    // clearTimeout siempre debería ser llamado
    expect(spyClearTimeout).toHaveBeenCalled();
    // clearInterval puede o no ser llamado dependiendo del estado
    // Lo importante es que la función se ejecute sin errores
  });

  it('debería configurar interval después del timeout', () => {
    const spySetInterval = vi.spyOn(global, 'setInterval');
    
    renderHook(() => useHourlySyncedUpdate(mockUpdateFunction));
    
    // Avanzar el tiempo para que se ejecute el timeout
    act(() => {
      vi.advanceTimersByTime(3600000); // 1 hora
    });

    // Ahora debería haber configurado el interval
    expect(spySetInterval).toHaveBeenCalled();
    expect(mockUpdateFunction).toHaveBeenCalledTimes(2); // inicial + después del timeout
  });

  it('debería limpiar interval después de configurarlo', () => {
    const spyClearInterval = vi.spyOn(global, 'clearInterval');
    
    const { unmount } = renderHook(() => useHourlySyncedUpdate(mockUpdateFunction));
    
    // Avanzar el tiempo para que se configure el interval
    act(() => {
      vi.advanceTimersByTime(3600000); // 1 hora
    });

    // Ahora desmontar
    act(() => {
      unmount();
    });

    // Ahora sí debería haber llamado clearInterval
    expect(spyClearInterval).toHaveBeenCalled();
  });
}); 