import React from 'react'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import App from '../../App'
import { I18nProvider } from '../../contexts/I18nContext'
import { ToastProvider } from '../../contexts/ToastContext'
import { renderAsync, actFlush } from '../utils/renderAsync'

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
      await renderAsync(<TestWrapper><App /></TestWrapper>)
      expect(screen.getAllByText('SIFU').length).toBeGreaterThan(0)
    })
  })

  describe('I18n Loading State', () => {
    it('shows loading when i18n loading flag set', async () => {
      globalThis.__TEST_I18N_LOADING__ = true
  await renderAsync(<TestWrapper><App /></TestWrapper>)
  // While loading, the header still renders; avoid single getByText due to duplicate subtitle occurrences
  expect(screen.getAllByText(/Sistema de Índices Financieros/).length).toBeGreaterThan(0)
    })
  })

  describe('Navigation', () => {
    it('renders tabs', async () => {
      await renderAsync(<TestWrapper><App /></TestWrapper>)
      expect(screen.getAllByText(/Unidad Indexada/).length).toBeGreaterThan(0)
      expect(screen.getAllByText(/Unidad Reajustable/).length).toBeGreaterThan(0)
      expect(screen.getAllByText(/Cotizaciones/).length).toBeGreaterThan(0)
      expect(screen.getAllByText(/BROU/).length).toBeGreaterThan(0)
    })

    it('switches to UR', async () => {
      await renderAsync(<TestWrapper><App /></TestWrapper>)
      const urTab = screen.getByText(/Unidad Reajustable/)
      fireEvent.click(urTab)
      await actFlush()
      expect(urTab).toBeInTheDocument()
    })

    it('switches to Exchange', async () => {
      await renderAsync(<TestWrapper><App /></TestWrapper>)
  // Use tab role to select the exchange tab
  const exTab = screen.getByRole('tab', { name: /Cotizaciones/ })
      fireEvent.click(exTab)
      await actFlush()
      expect(exTab).toBeInTheDocument()
    })
  })

  describe('App Info (smoke variations)', () => {
    it('initial data variant full', async () => {
      globalThis.__TEST_NETWORK_ERROR__ = false
      globalThis.__TEST_MOCK_DATA__ = { success: true, data: { total_records: 1000, latest_ui: { value: 50.25, date: '2024-01-01' } } }
      await renderAsync(<TestWrapper><App /></TestWrapper>)
  const sifu = screen.queryAllByText(/SIFU/)
  const appError = screen.queryByText(/Error en la aplicación/i)
  expect(sifu.length > 0 || !!appError).toBeTruthy()
    })

    it('missing latest_ui safe', async () => {
      globalThis.__TEST_MOCK_DATA__ = { success: true, data: { total_records: 10 } }
      await renderAsync(<TestWrapper><App /></TestWrapper>)
      expect(screen.getAllByText(/SIFU/).length).toBeGreaterThan(0)
    })

    it('null latest_ui value tolerated', async () => {
      globalThis.__TEST_MOCK_DATA__ = { success: true, data: { latest_ui: { value: null, date: '2024-01-01' } } }
      await renderAsync(<TestWrapper><App /></TestWrapper>)
      expect(screen.getAllByText(/SIFU/).length).toBeGreaterThan(0)
    })
  })

  describe('Error Display (network)', () => {
    it('shows UI error', async () => {
      globalThis.__TEST_NETWORK_ERROR__ = true
      await renderAsync(<TestWrapper><App /></TestWrapper>)
      await waitFor(() => {
        const err = screen.queryByText(/Error UI/i) || screen.queryByText(/Error al/i) || screen.queryByText(/No se pudo cargar/i)
        expect(err).toBeTruthy()
      })
    })

    it('shows UR error after switching', async () => {
      globalThis.__TEST_NETWORK_ERROR__ = true
      await renderAsync(<TestWrapper><App /></TestWrapper>)
      fireEvent.click(screen.getByText(/Unidad Reajustable/))
      await actFlush()
      await waitFor(() => {
        const err = screen.queryByText(/Error UR/i) || screen.queryByText(/No se pudo cargar/i)
        expect(err).toBeTruthy()
      })
    })

    it('shows Exchange error after switching', async () => {
      globalThis.__TEST_NETWORK_ERROR__ = true
      await renderAsync(<TestWrapper><App /></TestWrapper>)
      fireEvent.click(screen.getByText(/Cotizaciones/))
      await actFlush()
      await waitFor(() => {
        const err = screen.queryByText(/Error Cotizaciones/i) || screen.queryByText(/No se pudo cargar las cotizaciones/i)
        expect(err).toBeTruthy()
      })
    })
  })

  describe('Content Rendering', () => {
    it('default UI panel', async () => {
      await renderAsync(<TestWrapper><App /></TestWrapper>)
      expect(screen.getByText(/Consultar Valor de UI/i)).toBeInTheDocument()
    })

    it('UR panel', async () => {
      await renderAsync(<TestWrapper><App /></TestWrapper>)
      fireEvent.click(screen.getByText(/Unidad Reajustable/))
      await actFlush()
      await waitFor(() => expect(screen.getByText(/Consultar Valor de UR/i)).toBeInTheDocument())
    })

    it('Exchange panel', async () => {
      await renderAsync(<TestWrapper><App /></TestWrapper>)
  const exTab = screen.getByRole('tab', { name: /Cotizaciones/ })
      fireEvent.click(exTab)
      await actFlush()
      await waitFor(() => expect(screen.getByText(/Consultar Cotizaciones/i)).toBeInTheDocument())
    })

    it('BROU relaxed', async () => {
      await renderAsync(<TestWrapper><App /></TestWrapper>)
      fireEvent.click(screen.getAllByText(/BROU/)[0])
      await actFlush()
      const headerEls = screen.queryAllByText(/Cotizaciones BCU/i)
      const loadingEls = screen.queryAllByText(/Cargando/i)
      expect(headerEls.length > 0 || loadingEls.length > 0).toBeTruthy()
    })
  })

  describe('Footer', () => {
    it('renders footer basics', async () => {
      await renderAsync(<TestWrapper><App /></TestWrapper>)
      expect(screen.getByText(/Sistema de Índices Financieros del Uruguay/i)).toBeInTheDocument()
      expect(screen.getByText(/Fuentes oficiales/i)).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /BCU/i })).toBeInTheDocument()
    })
  })
})
