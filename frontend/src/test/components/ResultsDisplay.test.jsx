import React from 'react';
import { render, screen } from '@testing-library/react';
import ResultsDisplay from '../../components/ResultsDisplay';

describe('ResultsDisplay Component', () => {
  it('should display no results message when results are null', () => {
    render(<ResultsDisplay results={null} searchType="single" />);
    
    expect(screen.getByText('No se encontraron resultados')).toBeInTheDocument();
    expect(screen.getByText('Intenta con otra fecha o usa los selectores rápidos')).toBeInTheDocument();
  });

  it('should display error message when results contain an error', () => {
    const errorResults = { 
      success: false, 
      message: 'Error fetching data from server' 
    };
    
    render(<ResultsDisplay results={errorResults} searchType="single" />);
    
    expect(screen.getByText('Error fetching data from server')).toBeInTheDocument();
  });

  it('should display single UI value result correctly', () => {
    const singleResult = {
      success: true,
      data: {
        fecha: '2024-01-01',
        valor: 5.1234
      }
    };
    
    render(<ResultsDisplay results={singleResult} searchType="single" />);
    
    expect(screen.getByText('Valor de la UI')).toBeInTheDocument();
    expect(screen.getByText('$ 5,1234')).toBeInTheDocument();
    expect(screen.getByText('01/01/2024')).toBeInTheDocument();
    expect(screen.getByText('Fuente: Instituto Nacional de Estadística (INE) - Uruguay')).toBeInTheDocument();
  });

  it('should display range results with summary and detailed values', () => {
    const rangeResults = {
      success: true,
      data: [
        { fecha: '2024-01-01', valor: 5.1234 },
        { fecha: '2024-01-02', valor: 5.1334 }
      ]
    };
    
    render(<ResultsDisplay results={rangeResults} searchType="range" />);
    
    // Check summary section
    expect(screen.getByText('Resumen del Período')).toBeInTheDocument();
    
    // Check initial and final values
    expect(screen.getByText('Valor inicial')).toBeInTheDocument();
    expect(screen.getByText('Valor final')).toBeInTheDocument();
    
    // Check that both values appear in the document
    expect(screen.getAllByText('$ 5,1234').length).toBeGreaterThan(0);
    expect(screen.getAllByText('$ 5,1334').length).toBeGreaterThan(0);
    
    // Check variation calculation
    expect(screen.getAllByText('Variación').length).toBeGreaterThan(0);
    
    // Check percentage variation (flexible regex)
    const percentageElements = screen.getAllByText(/0\.\d+%/);
    expect(percentageElements.length).toBeGreaterThan(0);
  });

  it('should handle empty array results', () => {
    const emptyResults = {
      success: true,
      data: []
    };
    
    render(<ResultsDisplay results={emptyResults} searchType="range" />);
    
    // El componente muestra "No se encontraron datos" para arrays vacíos
    expect(screen.getByText('No se encontraron datos')).toBeInTheDocument();
  });

  it('should display UR values correctly', () => {
    const urResult = {
      success: true,
      data: {
        date: '2024-01-01',
        value: 1234.5678
      }
    };
    
    render(<ResultsDisplay results={urResult} searchType="single" dataType="ur" />);
    
    expect(screen.getByText('Valor de la UI')).toBeInTheDocument();
    expect(screen.getByText('$ 1.234,5678')).toBeInTheDocument();
  });

  it('should display exchange rate values correctly', () => {
    const exchangeResult = {
      success: true,
      data: {
        date: '2024-01-01',
        currency: 'USD',
        buy_rate: 42.50,
        sell_rate: 43.50,
        average_rate: 43.00,
        value: 43.00
      }
    };
    
    render(<ResultsDisplay results={exchangeResult} searchType="single" dataType="exchange" />);
    
    expect(screen.getByText('Valor de la UI')).toBeInTheDocument();
    expect(screen.getByText('$ 43,0000')).toBeInTheDocument();
    expect(screen.getByText('01/01/2024')).toBeInTheDocument();
  });

  it('should handle results with success false but no message', () => {
    const failedResults = { 
      success: false
    };
    
    render(<ResultsDisplay results={failedResults} searchType="single" />);
    
    expect(screen.getByText('No se encontraron resultados')).toBeInTheDocument();
  });

  it('should format currency values correctly', () => {
    const singleResult = {
      success: true,
      data: {
        fecha: '2024-01-01',
        valor: 1234.5678
      }
    };
    
    render(<ResultsDisplay results={singleResult} searchType="single" />);
    
    // Should format with proper thousands separator and decimals
    expect(screen.getByText('$ 1.234,5678')).toBeInTheDocument();
  });

  it('should handle date formatting correctly', () => {
    const singleResult = {
      success: true,
      data: {
        fecha: '2024-12-25',
        valor: 5.1234
      }
    };
    
    render(<ResultsDisplay results={singleResult} searchType="single" />);
    
    // Should format date as DD/MM/YYYY
    expect(screen.getByText('25/12/2024')).toBeInTheDocument();
  });
}); 