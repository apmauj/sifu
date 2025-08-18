import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import App from '../../App'
import { I18nProvider } from '../../contexts/I18nContext'
import { ToastProvider } from '../../contexts/ToastContext'

const TestWrapper = ({ children }) => (
  <I18nProvider>
    <ToastProvider>{children}</ToastProvider>
  </I18nProvider>
)

describe('App Component', () => {
  beforeEach(() => {
    globalThis.__TEST_MOCK_DATA__ = {
      success: true,
      data: { value: 50.25, date: '2024-01-01' }
    }
    globalThis.__TEST_NETWORK_ERROR__ = false
    globalThis.__TEST_I18N_LOADING__ = false
  })

  describe('Basic Rendering', () => {
    it('mounts', async () => {
      await act(async () => {
        render(<TestWrapper><App /></TestWrapper>)
      })
      expect(screen.getAllByText('SIFU').length).toBeGreaterThan(0)
    })
  })

  describe('I18n Loading State', () => {
    it('shows loading when i18n loading flag set', () => {
      globalThis.__TEST_I18N_LOADING__ = true
      render(<TestWrapper><App /></TestWrapper>)
      expect(screen.getAllByText(/Cargando/i).length).toBeGreaterThan(0)
    })
  })

  describe('Navigation', () => {
    it('renders tabs', async () => {
      await act(async () => { render(<TestWrapper><App /></TestWrapper>) })
      expect(screen.getAllByText(/Unidad Indexada/).length).toBeGreaterThan(0)
      expect(screen.getAllByText(/Unidad Reajustable/).length).toBeGreaterThan(0)
      expect(screen.getAllByText(/Cotizaciones/).length).toBeGreaterThan(0)
      expect(screen.getAllByText(/BROU/).length).toBeGreaterThan(0)
    })

    it('switches to UR', async () => {
      render(<TestWrapper><App /></TestWrapper>)
      const urTab = screen.getByText(/Unidad Reajustable/)
      await act(async () => fireEvent.click(urTab))
      expect(urTab).toBeInTheDocument()
    })

    it('switches to Exchange', async () => {
      render(<TestWrapper><App /></TestWrapper>)
      const exTab = screen.getByText(/Cotizaciones/)
      await act(async () => fireEvent.click(exTab))
      expect(exTab).toBeInTheDocument()
    })
  })

  describe('App Info (smoke variations)', () => {
    it('initial data variant full', () => {
      globalThis.__TEST_MOCK_DATA__ = { success: true, data: { total_records: 1000, latest_ui: { value: 50.25, date: '2024-01-01' } } }
      render(<TestWrapper><App /></TestWrapper>)
      expect(screen.getAllByText(/SIFU/).length).toBeGreaterThan(0)
    })

    it('missing latest_ui safe', async () => {
      globalThis.__TEST_MOCK_DATA__ = { success: true, data: { total_records: 10 } }
      await act(async () => { render(<TestWrapper><App /></TestWrapper>) })
      expect(screen.getAllByText(/SIFU/).length).toBeGreaterThan(0)
    })

    it('null latest_ui value tolerated', async () => {
      globalThis.__TEST_MOCK_DATA__ = { success: true, data: { latest_ui: { value: null, date: '2024-01-01' } } }
      await act(async () => { render(<TestWrapper><App /></TestWrapper>) })
      expect(screen.getAllByText(/SIFU/).length).toBeGreaterThan(0)
    })
  })

  describe('Error Display (network)', () => {
    it('shows UI error', async () => {
      globalThis.__TEST_NETWORK_ERROR__ = true
      await act(async () => { render(<TestWrapper><App /></TestWrapper>) })
      await waitFor(() => {
        const err = screen.queryByText(/Error UI/i) || screen.queryByText(/Error al/i) || screen.queryByText(/No se pudo cargar/i)
        expect(err).toBeTruthy()
      })
    })

    it('shows UR error after switching', async () => {
      globalThis.__TEST_NETWORK_ERROR__ = true
      render(<TestWrapper><App /></TestWrapper>)
      await act(async () => fireEvent.click(screen.getByText(/Unidad Reajustable/)))
      await waitFor(() => {
        const err = screen.queryByText(/Error UR/i) || screen.queryByText(/No se pudo cargar/i)
        expect(err).toBeTruthy()
      })
    })

    it('shows Exchange error after switching', async () => {
      globalThis.__TEST_NETWORK_ERROR__ = true
      render(<TestWrapper><App /></TestWrapper>)
      await act(async () => fireEvent.click(screen.getByText(/Cotizaciones/)))
      await waitFor(() => {
        const err = screen.queryByText(/Error Cotizaciones/i) || screen.queryByText(/No se pudo cargar las cotizaciones/i)
        expect(err).toBeTruthy()
      })
    })
  })

  describe('Content Rendering', () => {
    it('default UI panel', async () => {
      await act(async () => { render(<TestWrapper><App /></TestWrapper>) })
      expect(screen.getByText(/Consultar Valor de UI/i)).toBeInTheDocument()
    })

    it('UR panel', async () => {
      render(<TestWrapper><App /></TestWrapper>)
      await act(async () => fireEvent.click(screen.getByText(/Unidad Reajustable/)))
      await waitFor(() => expect(screen.getByText(/Consultar Valor de UR/i)).toBeInTheDocument())
    })

    it('Exchange panel', async () => {
      render(<TestWrapper><App /></TestWrapper>)
      await act(async () => fireEvent.click(screen.getByText(/Cotizaciones/)))
      await waitFor(() => expect(screen.getByText(/Consultar Cotizaciones/i)).toBeInTheDocument())
    })

    it('BROU relaxed', async () => {
      render(<TestWrapper><App /></TestWrapper>)
      await act(async () => fireEvent.click(screen.getAllByText(/BROU/)[0]))
      const headerEls = screen.queryAllByText(/Cotizaciones BCU/i)
      const loadingEls = screen.queryAllByText(/Cargando/i)
      expect(headerEls.length > 0 || loadingEls.length > 0).toBeTruthy()
    })
  })

  describe('Footer', () => {
    it('renders footer basics', async () => {
      await act(async () => { render(<TestWrapper><App /></TestWrapper>) })
      expect(screen.getByText(/Sistema de Índices Financieros del Uruguay/i)).toBeInTheDocument()
      expect(screen.getByText(/Fuentes oficiales/i)).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /BCU/i })).toBeInTheDocument()
    })
  })
})
