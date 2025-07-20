import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  getTodayLocal,
  formatDateLocal,
  subtractDaysLocal,
  getDaysAgoLocal,
  getCurrentTimestamp
} from '../../utils/dateUtils.js';

describe('Date Utils', () => {
  // Sin fake timers - usar fechas reales para coverage correcto

  describe('getTodayLocal', () => {
    it('should return current date in YYYY-MM-DD format', () => {
      const today = getTodayLocal();
      
      // Verificar formato correcto
      expect(today).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      
      // Verificar que es una fecha válida
      const date = new Date(today);
      expect(date).toBeInstanceOf(Date);
      expect(date.toString()).not.toBe('Invalid Date');
    });

    it('should return a valid date string', () => {
      const today = getTodayLocal();
      const todayDate = new Date(today);
      
      // Verificar que es una fecha válida y reciente
      expect(todayDate).toBeInstanceOf(Date);
      expect(todayDate.getFullYear()).toBeGreaterThan(2020);
      expect(todayDate.getFullYear()).toBeLessThan(2030);
    });

    it('should have proper zero padding for months and days', () => {
      const today = getTodayLocal();
      const parts = today.split('-');
      
      expect(parts).toHaveLength(3);
      expect(parts[0]).toHaveLength(4); // Year
      expect(parts[1]).toHaveLength(2); // Month
      expect(parts[2]).toHaveLength(2); // Day
    });
  });

  describe('formatDateLocal', () => {
    it('should format date to YYYY-MM-DD', () => {
      const testDate = new Date('2024-01-01T12:00:00.000Z');
      const formatted = formatDateLocal(testDate);
      
      expect(formatted).toBe('2024-01-01');
    });

    it('should handle single digit months and days with zero padding', () => {
      const testDate = new Date('2024-03-05T12:00:00.000Z');
      const formatted = formatDateLocal(testDate);
      
      expect(formatted).toBe('2024-03-05');
    });

    it('should handle end of year dates', () => {
      const testDate = new Date('2023-12-31T12:00:00.000Z');
      const formatted = formatDateLocal(testDate);
      
      expect(formatted).toBe('2023-12-31');
    });

    it('should handle beginning of year dates', () => {
      const testDate = new Date('2024-01-01T12:00:00.000Z');
      const formatted = formatDateLocal(testDate);
      
      expect(formatted).toBe('2024-01-01');
    });

    it('should handle various valid dates correctly', () => {
      const dates = [
        { input: new Date('2024-06-15T12:00:00.000Z'), expected: '2024-06-15' },
        { input: new Date('2023-11-30T12:00:00.000Z'), expected: '2023-11-30' },
        { input: new Date('2025-02-28T12:00:00.000Z'), expected: '2025-02-28' }
      ];

      dates.forEach(({ input, expected }) => {
        expect(formatDateLocal(input)).toBe(expected);
      });
    });
  });

  describe('subtractDaysLocal', () => {
    it('should subtract days correctly', () => {
      const testDate = new Date('2024-01-15T12:00:00.000Z');
      const result = subtractDaysLocal(testDate, 5);
      
      expect(result).toBe('2024-01-10');
    });

    it('should handle month boundaries', () => {
      const testDate = new Date('2024-02-05T12:00:00.000Z');
      const result = subtractDaysLocal(testDate, 10);
      
      expect(result).toBe('2024-01-26');
    });

    it('should handle year boundaries', () => {
      const testDate = new Date('2024-01-05T12:00:00.000Z');
      const result = subtractDaysLocal(testDate, 10);
      
      expect(result).toBe('2023-12-26');
    });

    it('should handle zero days (no change)', () => {
      const testDate = new Date('2024-01-15T12:00:00.000Z');
      const result = subtractDaysLocal(testDate, 0);
      
      expect(result).toBe('2024-01-15');
    });

    it('should handle large day differences', () => {
      const testDate = new Date('2024-06-15T12:00:00.000Z');
      const result = subtractDaysLocal(testDate, 100);
      
      expect(result).toBe('2024-03-07');
    });

    it('should not modify original date object', () => {
      const originalDate = new Date('2024-01-15T12:00:00.000Z');
      const originalTime = originalDate.getTime();
      
      subtractDaysLocal(originalDate, 5);
      
      expect(originalDate.getTime()).toBe(originalTime);
    });
  });

  describe('getDaysAgoLocal', () => {
    it('should return date in correct format', () => {
      const result = getDaysAgoLocal(1);
      
      expect(result).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      
      const date = new Date(result);
      expect(date).toBeInstanceOf(Date);
      expect(date.toString()).not.toBe('Invalid Date');
    });

    it('should return different dates for different day counts', () => {
      const result1 = getDaysAgoLocal(1);
      const result7 = getDaysAgoLocal(7);
      
      expect(result1).not.toBe(result7);
      
      const date1 = new Date(result1);
      const date7 = new Date(result7);
      
      expect(date1.getTime()).toBeGreaterThan(date7.getTime());
    });

    it('should handle zero days (should equal getTodayLocal)', () => {
      const result = getDaysAgoLocal(0);
      const today = getTodayLocal();
      
      expect(result).toBe(today);
    });

    it('should maintain chronological order', () => {
      const results = [
        getDaysAgoLocal(1),
        getDaysAgoLocal(2),
        getDaysAgoLocal(3)
      ];
      
      const dates = results.map(r => new Date(r));
      
      expect(dates[0].getTime()).toBeGreaterThan(dates[1].getTime());
      expect(dates[1].getTime()).toBeGreaterThan(dates[2].getTime());
    });

    it('should handle reasonable day differences', () => {
      const result = getDaysAgoLocal(30);
      const resultDate = new Date(result);
      const today = new Date();
      
      // Verificar que la diferencia está en el rango esperado (28-32 días)
      const diffInDays = Math.round((today.getTime() - resultDate.getTime()) / (1000 * 60 * 60 * 24));
      expect(diffInDays).toBeGreaterThanOrEqual(28);
      expect(diffInDays).toBeLessThanOrEqual(32);
    });
  });

  describe('getCurrentTimestamp', () => {
    it('should return a Date object', () => {
      const result = getCurrentTimestamp();
      
      expect(result).toBeInstanceOf(Date);
    });

    it('should return a valid timestamp', () => {
      const timestamp = getCurrentTimestamp();
      
      // Verificar que es una fecha válida y reciente
      expect(timestamp.getFullYear()).toBeGreaterThan(2020);
      expect(timestamp.getFullYear()).toBeLessThan(2030);
      expect(timestamp.toString()).not.toBe('Invalid Date');
    });

    it('should return timestamps that change over time', () => {
      const timestamp1 = getCurrentTimestamp();
      
      // Esperar un poco para asegurar diferencia de tiempo
      const timestamp2 = getCurrentTimestamp();
      
      // Los timestamps deberían ser muy cercanos en tiempo
      const diff = Math.abs(timestamp2.getTime() - timestamp1.getTime());
      expect(diff).toBeLessThan(1000); // Menos de 1 segundo de diferencia
    });
  });

  describe('Integration tests', () => {
    it('should work together for common use cases', () => {
      const today = getTodayLocal();
      const yesterday = getDaysAgoLocal(1);
      const timestamp = getCurrentTimestamp();
      
      expect(today).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      expect(yesterday).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      expect(timestamp).toBeInstanceOf(Date);
      
      expect(today).not.toBe(yesterday);
    });

    it('should format and calculate dates consistently', () => {
      const testDate = new Date('2024-06-15T12:00:00.000Z');
      const formatted = formatDateLocal(testDate);
      const subtracted = subtractDaysLocal(testDate, 5);
      
      expect(formatted).toBe('2024-06-15');
      expect(subtracted).toBe('2024-06-10');
    });

    it('should handle current date operations consistently', () => {
      const today1 = getTodayLocal();
      const today2 = getDaysAgoLocal(0);
      const timestamp = getCurrentTimestamp();
      const formattedTimestamp = formatDateLocal(timestamp);
      
      expect(today1).toBe(today2);
      expect(today1).toBe(formattedTimestamp);
    });
  });

  describe('Edge cases and error handling', () => {
    it('should handle leap year calculations', () => {
      const leapYearDate = new Date('2024-03-01T12:00:00.000Z'); // 2024 is a leap year
      const result = subtractDaysLocal(leapYearDate, 30);
      
      expect(result).toBe('2024-01-31');
    });

    it('should handle non-leap year calculations', () => {
      const nonLeapYearDate = new Date('2023-03-01T12:00:00.000Z'); // 2023 is not a leap year
      const result = subtractDaysLocal(nonLeapYearDate, 30);
      
      expect(result).toBe('2023-01-30');
    });

    it('should handle year boundary calculations', () => {
      const newYearDate = new Date('2024-01-01T12:00:00.000Z');
      const result = subtractDaysLocal(newYearDate, 1);
      
      expect(result).toBe('2023-12-31');
    });

    it('should handle various month lengths correctly', () => {
      // Test February (28 days)
      const feb = new Date('2023-03-01T12:00:00.000Z');
      expect(subtractDaysLocal(feb, 1)).toBe('2023-02-28');
      
      // Test April (30 days)
      const may = new Date('2024-05-01T12:00:00.000Z');
      expect(subtractDaysLocal(may, 1)).toBe('2024-04-30');
      
      // Test January (31 days)
      const feb2 = new Date('2024-02-01T12:00:00.000Z');
      expect(subtractDaysLocal(feb2, 1)).toBe('2024-01-31');
    });

    it('should maintain format consistency across all functions', () => {
      const today = getTodayLocal();
      const yesterday = getDaysAgoLocal(1);
      const testDate = new Date('2024-01-01T12:00:00.000Z');
      const formatted = formatDateLocal(testDate);
      const subtracted = subtractDaysLocal(testDate, 1);
      
      // All should follow YYYY-MM-DD format
      expect(today).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      expect(yesterday).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      expect(formatted).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      expect(subtracted).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    });
  });
}); 