import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import { I18nProvider } from './contexts/I18nContext.jsx'
import { ToastProvider } from './contexts/ToastContext.jsx'
import { ThemeProvider } from './contexts/ThemeContext.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider>
      <I18nProvider>
        <ToastProvider>
          <App />
        </ToastProvider>
      </I18nProvider>
    </ThemeProvider>
  </React.StrictMode>,
) 