#!/usr/bin/env python3
"""
Procesador de cotizaciones del BROU
Extrae cotizaciones del sitio web oficial del BROU y calcula arbitrajes
"""

import requests
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BROUProcessor:
    """Procesador para obtener cotizaciones del BROU"""
    
    def __init__(self):
        self.base_url = "https://www.brou.com.uy"
        self.portlet_url = (
            f"{self.base_url}/c/portal/render_portlet"
            "?p_l_id=20593"
            "&p_p_id=cotizacionfull_WAR_broutmfportlet_INSTANCE_otHfewh1klyS"
            "&p_p_lifecycle=0"
            "&p_t_lifecycle=0"
            "&p_p_state=normal"
            "&p_p_mode=view"
            "&p_p_col_id=column-1"
            "&p_p_col_pos=0"
            "&p_p_col_count=2"
            "&p_p_isolated=1"
            "&currentURL=%2Fweb%2Fguest%2Fcotizaciones"
        )
        
        # Mapeo de monedas BROU a códigos estándar
        self.currency_mapping = {
            'Dólar': 'USD',
            'Dólar eBROU': 'USD_EBROU',
            'Euro': 'EUR',
            'Peso Argentino': 'ARS',
            'Real': 'BRL'
        }
        
        # Monedas objetivo para el componente
        self.target_currencies = ['USD', 'USD_EBROU', 'EUR', 'ARS', 'BRL']
        
        # Monedas para calcular arbitraje (vs USD)
        self.arbitrage_currencies = ['EUR', 'ARS', 'BRL']
    
    def get_current_rates(self) -> Tuple[List[Dict], bool]:
        """
        Obtiene las cotizaciones actuales del BROU
        Returns: (rates_list, is_from_brou)
        """
        try:
            logger.info("Obteniendo cotizaciones del BROU...")
            rates_data = self._fetch_rates()
            
            if not rates_data:
                logger.warning("No se pudieron obtener datos del BROU, usando datos de muestra")
                return self._get_sample_rates(), False
            
            # Convertir a formato de lista
            rates_list = []
            usd_rate = None
            
            # Primero obtener USD para calcular arbitrajes
            if 'USD' in rates_data:
                usd_rate = rates_data['USD']
            
            for currency in self.target_currencies:
                if currency in rates_data:
                    rate_data = rates_data[currency]
                    
                    # Calcular arbitrajes si corresponde
                    arbitrage_buy = None
                    arbitrage_sell = None
                    
                    if currency in self.arbitrage_currencies and usd_rate:
                        arbitrage_buy, arbitrage_sell = self._calculate_arbitrage(
                            rate_data, usd_rate
                        )
                    
                    rates_list.append({
                        'currency': currency,
                        'name': rate_data['name'],
                        'buy_rate': rate_data['buy_rate'],
                        'sell_rate': rate_data['sell_rate'],
                        'average_rate': rate_data['average_rate'],
                        'arbitrage_buy': arbitrage_buy,
                        'arbitrage_sell': arbitrage_sell,
                        'source': 'BROU',
                        'timestamp': rate_data['timestamp']
                    })
            
            logger.info(f"Cotizaciones BROU obtenidas exitosamente: {len(rates_list)} monedas")
            return rates_list, True
            
        except Exception as e:
            logger.error(f"Error obteniendo cotizaciones BROU: {e}")
            return self._get_sample_rates(), False
    
    def _fetch_rates(self) -> Optional[Dict]:
        """Obtiene las cotizaciones del BROU via scraping"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(self.portlet_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            return self._parse_html(response.text)
            
        except requests.RequestException as e:
            logger.error(f"Error al obtener datos del BROU: {e}")
            return None
    
    def _parse_html(self, html: str) -> Dict:
        """Parsea el HTML para extraer las cotizaciones"""
        rates = {}
        
        # Patrón para extraer filas de la tabla
        table_pattern = r'<tr>.*?<p class="moneda">([^<]+)</p>.*?</tr>'
        
        for row_match in re.finditer(table_pattern, html, re.DOTALL):
            row_html = row_match.group(0)
            
            # Extraer nombre de la moneda
            currency_match = re.search(r'<p class="moneda">([^<]+)</p>', row_html)
            if not currency_match:
                continue
                
            currency_name = currency_match.group(1).strip()
            currency_code = self.currency_mapping.get(currency_name)
            
            # Solo procesar monedas que nos interesan
            if not currency_code or currency_code not in self.target_currencies:
                continue
            
            # Extraer valores (compra, venta)
            values = re.findall(r'<p class="valor">\s*([0-9.,\-]+)\s*</p>', row_html)
            
            if len(values) >= 2:
                try:
                    # Convertir valores (formato uruguayo: coma decimal, punto miles)
                    buy_str = values[0].replace('.', '').replace(',', '.')
                    sell_str = values[1].replace('.', '').replace(',', '.')
                    
                    # Manejar valores especiales
                    if buy_str == '-':
                        buy_rate = None
                    else:
                        buy_rate = float(buy_str)
                    
                    if sell_str == '-':
                        sell_rate = None
                    else:
                        sell_rate = float(sell_str)
                    
                    # Calcular promedio si ambos valores existen
                    if buy_rate is not None and sell_rate is not None:
                        average_rate = (buy_rate + sell_rate) / 2
                    else:
                        average_rate = buy_rate or sell_rate
                    
                    rates[currency_code] = {
                        'currency': currency_code,
                        'name': currency_name,
                        'buy_rate': buy_rate,
                        'sell_rate': sell_rate,
                        'average_rate': average_rate,
                        'source': 'BROU',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    logger.debug(f"BROU {currency_code}: Compra={buy_rate}, Venta={sell_rate}")
                    
                except (ValueError, IndexError) as e:
                    logger.error(f"Error procesando {currency_name}: {e}")
                    continue
        
        return rates
    
    def _calculate_arbitrage(self, currency_rate: Dict, usd_rate: Dict) -> Tuple[Optional[float], Optional[float]]:
        """
        Calcula arbitraje de compra y venta vs USD
        Arbitraje = (Tasa_Moneda / Tasa_USD)
        """
        try:
            currency_buy = currency_rate.get('buy_rate')
            currency_sell = currency_rate.get('sell_rate')
            usd_buy = usd_rate.get('buy_rate')
            usd_sell = usd_rate.get('sell_rate')
            
            arbitrage_buy = None
            arbitrage_sell = None
            
            # Arbitraje de compra: Compra_Moneda / Compra_USD
            if currency_buy is not None and usd_buy is not None and usd_buy != 0:
                arbitrage_buy = currency_buy / usd_buy
            
            # Arbitraje de venta: Venta_Moneda / Venta_USD  
            if currency_sell is not None and usd_sell is not None and usd_sell != 0:
                arbitrage_sell = currency_sell / usd_sell
            
            return arbitrage_buy, arbitrage_sell
            
        except Exception as e:
            logger.error(f"Error calculando arbitraje: {e}")
            return None, None
    
    def _get_sample_rates(self) -> List[Dict]:
        """Datos de muestra como fallback"""
        logger.warning("Usando datos de muestra BROU")
        
        sample_data = [
            {
                'currency': 'USD',
                'name': 'Dólar',
                'buy_rate': 39.65,
                'sell_rate': 42.05,
                'average_rate': 40.85,
                'arbitrage_buy': None,
                'arbitrage_sell': None,
                'source': 'BROU_SAMPLE',
                'timestamp': datetime.now().isoformat()
            },
            {
                'currency': 'USD_EBROU',
                'name': 'Dólar eBROU',
                'buy_rate': 40.15,
                'sell_rate': 41.55,
                'average_rate': 40.85,
                'arbitrage_buy': None,
                'arbitrage_sell': None,
                'source': 'BROU_SAMPLE',
                'timestamp': datetime.now().isoformat()
            },
            {
                'currency': 'EUR',
                'name': 'Euro',
                'buy_rate': 44.79,
                'sell_rate': 50.06,
                'average_rate': 47.425,
                'arbitrage_buy': 1.129,
                'arbitrage_sell': 1.190,
                'source': 'BROU_SAMPLE',
                'timestamp': datetime.now().isoformat()
            },
            {
                'currency': 'ARS',
                'name': 'Peso Argentino',
                'buy_rate': 0.020,
                'sell_rate': 0.200,
                'average_rate': 0.110,
                'arbitrage_buy': 0.0005,
                'arbitrage_sell': 0.0048,
                'source': 'BROU_SAMPLE',
                'timestamp': datetime.now().isoformat()
            },
            {
                'currency': 'BRL',
                'name': 'Real',
                'buy_rate': 6.70,
                'sell_rate': 8.40,
                'average_rate': 7.55,
                'arbitrage_buy': 0.169,
                'arbitrage_sell': 0.200,
                'source': 'BROU_SAMPLE',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        return sample_data 