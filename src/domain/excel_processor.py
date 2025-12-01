from typing import Any
try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # noqa: N816
    import warnings
    warnings.warn(
        "pandas no disponible; operaciones de Excel serán omitidas en este entorno"
    )
import requests
from datetime import datetime, date
from typing import List, Tuple, Optional
import logging
from sqlalchemy.orm import Session
from src.infrastructure.database import UIRecord, URRecord, ExchangeRateRecord
import io
from urllib3.exceptions import InsecureRequestWarning
from src.infrastructure.circuit_breaker import get_circuit_breaker, CircuitBreakerOpenException
from src.utils.constants import (
    UR_MONTH_NAMES,
    URL_BCU_EXCHANGE_RATES,
    SUPPORTED_CURRENCIES,
    HTTP_USER_AGENT,
    HTTP_TIMEOUT,
    URL_INE_EXCHANGE_RATES,
    MAX_VALID_YEAR,
    MIN_VALID_YEAR,
    LOG_EXCEL_UR_DOWNLOADED,
    EXCEL_ENGINE_XLS,
    LOG_DOWNLOADING_EXCEL_INE,
    LOG_DOWNLOADING_EXCEL_BHU,
    LOG_DOWNLOADING_EXCEL_INE_UR_FALLBACK,
    URL_BHU_UR,
    URL_BHU_UR_TEMPLATE,
    URL_INE_UR,
    UR_URL_MONTHS_BACK,
    URL_INE_UI,
    LOG_RECORDS_SAVED,
    LOG_RECORDS_PARSED,
    DATE_FORMATS,
    LOG_EXCEL_DOWNLOADED,
    LOG_TRYING_BHU_URL,
    LOG_USING_BHU_URL,
    LOG_ALL_BHU_URLS_FAILED,
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExcelProcessor:
    """Processor for UI (Unidad Indexada) historical Excel from INE.

    Note: Dynamic BHU URL resolution applies ONLY to URExcelProcessor below; this
    class intentionally keeps the simpler static INE download logic.
    """

    def __init__(self):
        self.url = URL_INE_UI
        self.timeout = HTTP_TIMEOUT

    def download_excel(self) -> Optional[Any]:
        """Download Excel file from INE URL"""
        if pd is None:
            logger.warning("pandas not available; skipping UI Excel download")
            return None
        try:
            logger.info(LOG_DOWNLOADING_EXCEL_INE)
            headers = {"User-Agent": HTTP_USER_AGENT}

            cb = get_circuit_breaker("INE_API")
            with cb:
                # NOTE: INE server presents incomplete certificate chain (missing intermediate cert).
                # Since this is official government site (.gub.uy), we disable SSL verification.
                # WARNING: Do not use verify=False for untrusted sites.
                logger.warning("INE server has incomplete SSL cert chain - disabling verification")
                # Suppress InsecureRequestWarning for this specific request
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                response = requests.get(
                    self.url, 
                    timeout=self.timeout, 
                    headers=headers,
                    verify=False
                )
                response.raise_for_status()

            excel_data = pd.read_excel(
                io.BytesIO(response.content), engine=EXCEL_ENGINE_XLS
            )
            logger.info(LOG_EXCEL_DOWNLOADED.format(count=len(excel_data)))
            return excel_data

        except CircuitBreakerOpenException:
            logger.warning("Circuit breaker is OPEN for INE API - skipping download")
            return None
        except requests.RequestException as e:
            logger.error(f"Error downloading file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            return None

    def parse_excel_data(self, excel_data: Any) -> List[Tuple[date, float]]:
        """Parse Excel data and return a list of tuples (date, value)"""
        if pd is None:
            logger.warning("pandas not available; cannot parse UI Excel data")
            return []
        try:
            records = []
            skipped_rows = 0

            # Find date and value columns
            # Assuming first column is date and second is value
            date_col = excel_data.columns[0]
            value_col = excel_data.columns[1]

            for _, row in excel_data.iterrows():
                try:
                    date_raw = row[date_col]
                    value_raw = row[value_col]

                    # Skip empty rows or headers
                    if pd.isna(date_raw) or pd.isna(value_raw):
                        continue

                    # Convert date
                    if isinstance(date_raw, str):
                        # Try various date formats
                        for fmt in DATE_FORMATS:
                            try:
                                parsed_date = datetime.strptime(date_raw, fmt).date()
                                break
                            except ValueError:
                                continue
                        else:
                            continue
                    elif isinstance(date_raw, datetime):
                        parsed_date = date_raw.date()
                    else:
                        continue

                    # Convert value
                    try:
                        # Handle string values with comma decimal or thousand separators
                        if isinstance(value_raw, str):
                            raw = value_raw.strip()
                            if raw == "":
                                skipped_rows += 1
                                continue
                            # European decimal: 6,3655 -> 6.3655
                            # Remove spaces; if both '.' and ',' appear assume '.' thousands separator
                            if "," in raw:
                                if "." in raw:
                                    # 1.234,56 -> 1234.56
                                    raw = raw.replace(".", "").replace(",", ".")
                                else:
                                    # 1234,56 -> 1234.56
                                    raw = raw.replace(",", ".")
                            parsed_value = float(raw)
                        else:
                            parsed_value = float(value_raw)
                    except (ValueError, TypeError):
                        skipped_rows += 1
                        continue

                    records.append((parsed_date, parsed_value))

                except Exception as e:
                    logger.warning(f"Error processing row: {e}")
                    continue

            logger.info(LOG_RECORDS_PARSED.format(count=len(records)))
            if skipped_rows:
                logger.info(
                    f"UI parser skipped {skipped_rows} rows due to value parsing issues (likely comma decimal format before fix)"
                )
            return records

        except Exception as e:
            logger.error(f"Error parsing Excel data: {e}")
            return []

    def save_to_database(self, db: Session, records: List[Tuple[date, float]]) -> int:
        """Save records to database"""
        if pd is None:
            logger.warning("pandas not available; skipping UI save_to_database")
            return 0
        try:
            saved_count = 0

            for record_date, record_value in records:
                # Check if already exists
                existing = (
                    db.query(UIRecord).filter(UIRecord.date == record_date).first()
                )

                if existing:
                    # Update if value changed
                    if existing.value != record_value:
                        existing.value = record_value
                        existing.updated_at = datetime.utcnow()
                        saved_count += 1
                else:
                    # Create new record
                    new_record = UIRecord(date=record_date, value=record_value)
                    db.add(new_record)
                    saved_count += 1

            db.commit()
            logger.info(LOG_RECORDS_SAVED.format(count=saved_count))
            return saved_count

        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            db.rollback()
            return 0

    def refresh_data(self, db: Session) -> Tuple[bool, str, int]:
        """Update data by downloading and processing the INE spreadsheet"""
        if pd is None:
            return False, "pandas not available; UI refresh skipped", 0
        try:
            # Download file
            excel_data = self.download_excel()
            if excel_data is None:
                return False, "Error downloading file from INE", 0

            # Parse data
            records = self.parse_excel_data(excel_data)
            if not records:
                return False, "Could not extract valid data from file", 0

            # Save to database
            saved_count = self.save_to_database(db, records)

            if saved_count > 0:
                return (
                    True,
                    f"Data updated successfully. {saved_count} records processed",
                    saved_count,
                )
            else:
                return True, "No changes in data", 0

        except Exception as e:
            logger.error(f"Error in refresh_data: {e}")
            return False, f"Internal error: {str(e)}", 0


class URExcelProcessor:
    def __init__(self):
        self.url = URL_BHU_UR
        self.timeout = HTTP_TIMEOUT

    def download_excel(self) -> Optional[Any]:
        """Download UR Excel file from BHU URL with INE fallback"""
        if pd is None:
            logger.warning("pandas not available; skipping UR Excel download")
            return None
        
        # Try to resolve the most recent BHU URL
        bhu_url = self._resolve_dynamic_bhu_url()
        if bhu_url:
            logger.info(LOG_DOWNLOADING_EXCEL_BHU)
            excel_data = self._try_download_from_url(bhu_url)
            if excel_data is not None:
                return excel_data
            logger.warning("BHU URL found but file is invalid or corrupt")
        
        # If BHU fails, try INE as fallback
        logger.info(LOG_DOWNLOADING_EXCEL_INE_UR_FALLBACK)
        excel_data = self._try_download_from_url(URL_INE_UR)
        if excel_data is not None:
            logger.info(f"Successfully using INE fallback: {URL_INE_UR}")
            return excel_data
        
        logger.error("Both BHU and INE sources failed for UR data")
        return None
    
    def _try_download_from_url(self, url: str) -> Optional[Any]:
        """Attempt to download and parse Excel file from given URL"""
        try:
            headers = {"User-Agent": HTTP_USER_AGENT}
            cb = get_circuit_breaker("BHU_API")
            
            with cb:
                # NOTE: BHU/INE servers have incomplete SSL certificate chain (missing intermediate cert).
                # Since these are official government sites (.gub.uy), we disable SSL verification.
                # WARNING: Do not use verify=False for untrusted sites.
                logger.warning(f"Disabling SSL verification for government site: {url}")
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                response = requests.get(
                    url, 
                    timeout=self.timeout, 
                    headers=headers,
                    verify=False
                )
                response.raise_for_status()
            
            # Try to read Excel file
            excel_data = pd.read_excel(
                io.BytesIO(response.content), engine=EXCEL_ENGINE_XLS
            )
            logger.info(LOG_EXCEL_UR_DOWNLOADED.format(count=len(excel_data)))
            return excel_data
            
        except CircuitBreakerOpenException:
            logger.warning(f"Circuit breaker is OPEN for {url} - skipping download")
            return None
        except requests.RequestException as e:
            logger.error(f"Error downloading from {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing Excel file from {url}: {e}")
            return None

    def _resolve_dynamic_bhu_url(self) -> Optional[str]:
        """Attempt to find the most recent available BHU UR Excel URL.

        Strategy:
        - Build candidate URLs using template for current month going backwards
          up to UR_URL_MONTHS_BACK months.
        - On first successful HTTP 200, return that URL.
        - Fallback to legacy URL_BHU_UR if no candidate works.
        Returns selected URL or None if all fail.
        """
        try:
            from dateutil.relativedelta import (
                relativedelta,
            )  # lightweight, may already be present
        except Exception:  # pragma: no cover - avoid hard dep if missing
            relativedelta = None

        now = datetime.utcnow().date().replace(day=1)
        candidates = []
        for i in range(UR_URL_MONTHS_BACK):
            if relativedelta:
                dt = now - relativedelta(months=i)
            else:  # simple fallback manual month decrement
                year = now.year
                month = now.month - i
                while month <= 0:
                    month += 12
                    year -= 1
                dt = now.replace(year=year, month=month)
            candidates.append(URL_BHU_UR_TEMPLATE.format(year=dt.year, month=dt.month))

        # Ensure legacy static URL is tried last if not already included
        if URL_BHU_UR not in candidates:
            candidates.append(URL_BHU_UR)

        for url in candidates:
            try:
                logger.info(LOG_TRYING_BHU_URL.format(url=url))
                headers = {"User-Agent": HTTP_USER_AGENT}
                resp = requests.head(
                    url,
                    timeout=min(10, self.timeout),
                    headers=headers,
                    allow_redirects=True,
                )
                if (
                    resp.status_code == 200
                    and int(resp.headers.get("Content-Length", "1")) > 0
                ):
                    logger.info(LOG_USING_BHU_URL.format(url=url))
                    return url
            except Exception as e:  # noqa: BLE001
                logger.debug(f"HEAD failed for {url}: {e}")
                continue

        # All BHU URLs failed, try INE as fallback
        logger.info(LOG_DOWNLOADING_EXCEL_INE_UR_FALLBACK)
        try:
            headers = {"User-Agent": HTTP_USER_AGENT}
            resp = requests.head(
                URL_INE_UR,
                timeout=min(10, self.timeout),
                headers=headers,
                allow_redirects=True,
            )
            if (
                resp.status_code == 200
                and int(resp.headers.get("Content-Length", "1")) > 0
            ):
                logger.info(f"Usando fallback INE UR: {URL_INE_UR}")
                return URL_INE_UR
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Fallback INE también falló: {e}")

        logger.warning(LOG_ALL_BHU_URLS_FAILED)
        return None

    def parse_excel_data(
        self, excel_data: Any
    ) -> List[Tuple[int, int, float]]:
        """
        Parse UR Excel data from either BHU (matrix format) or INE (list format).
        Returns a list of tuples (year, month, value)
        """
        if pd is None:
            logger.warning("pandas not available; cannot parse UR Excel data")
            return []
        try:
            logger.info(f"UR file structure: {excel_data.shape}")
            logger.info(f"Detected columns: {list(excel_data.columns)}")
            logger.info(f"First 5 rows:\n{excel_data.head()}")
            
            # Detect format: INE format has date strings in first column
            # Look for pattern "YYYY-MM-DD HH:MM:SS" or similar date format
            first_col = excel_data.iloc[:, 0]
            sample_values = first_col.dropna().head(10).astype(str)
            
            # Check if it looks like INE format (dates in first column)
            is_ine_format = any(
                '-' in str(val) and any(char.isdigit() for char in str(val))
                for val in sample_values
            )
            
            if is_ine_format:
                logger.info("Detected INE list format (date, value)")
                return self._parse_ine_format(excel_data)
            else:
                logger.info("Detected BHU matrix format (years x months)")
                return self._parse_bhu_format(excel_data)
                
        except Exception as e:
            logger.error(f"Error parsing UR Excel data: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_ine_format(self, excel_data: Any) -> List[Tuple[int, int, float]]:
        """Parse INE format: sequential list with date in col 0, value in col 1"""
        records = []
        
        # Find the header row (contains "Mes y año" or similar)
        data_start_idx = 0
        for idx, row in excel_data.iterrows():
            row_str = " ".join([str(cell) for cell in row if pd.notna(cell)])
            if "Mes" in row_str or "año" in row_str or "Valor" in row_str:
                data_start_idx = idx + 1
                logger.info(f"INE data starts at row {data_start_idx}")
                break
        
        # Process data rows
        for idx in range(data_start_idx, len(excel_data)):
            try:
                row = excel_data.iloc[idx]
                date_val = row.iloc[0]  # First column: date
                value_val = row.iloc[1] if len(row) > 1 else None  # Second column: value
                
                if pd.isna(date_val) or pd.isna(value_val):
                    continue
                
                # Parse date - can be string "YYYY-MM-DD HH:MM:SS" or datetime object
                if isinstance(date_val, str):
                    # Extract year and month from string
                    date_parts = date_val.split('-')
                    if len(date_parts) >= 2:
                        year = int(date_parts[0])
                        month = int(date_parts[1])
                    else:
                        continue
                else:
                    # Assume it's a datetime object
                    year = date_val.year
                    month = date_val.month
                
                # Parse value
                value = float(value_val)
                
                # Validate
                if MIN_VALID_YEAR <= year <= MAX_VALID_YEAR and 1 <= month <= 12:
                    records.append((year, month, value))
                    
            except Exception as e:
                logger.debug(f"Skipping row {idx}: {e}")
                continue
        
        logger.info(f"INE format: Parsed {len(records)} records")
        return records
    
    def _parse_bhu_format(self, excel_data: Any) -> List[Tuple[int, int, float]]:
        """Parse BHU format: matrix with years in rows, months in columns"""
        records = []
        
        # BHU file has a specific structure
        # We need to find the row with month names and the column with years

        # Search for the row containing months (header)
        header_row_idx = None
        month_names = UR_MONTH_NAMES

        for idx, row in excel_data.iterrows():
            row_str = " ".join(
                [str(cell).upper() for cell in row if pd.notna(cell)]
            )
            if any(month in row_str for month in month_names):
                header_row_idx = idx
                logger.info(f"Month header found in row {idx}")
                break

        if header_row_idx is None:
            logger.error("No row with month names found in BHU format")
            return []

        # Use that row as header
        new_header = excel_data.iloc[header_row_idx].values
        excel_data.columns = new_header

        # Data starts after the header
        data_start = header_row_idx + 1
        data_section = excel_data.iloc[data_start:].copy()

        logger.info(f"New columns: {list(data_section.columns)}")
        logger.info(f"Data from row {data_start}, total rows: {len(data_section)}")

        # Search for the year column (first column that is not NaN)
        year_column = None
        for col in data_section.columns:
            if pd.notna(col):  # Column with valid name
                # Check if it contains years
                sample_values = data_section[col].dropna().head(10)
                if any(
                    isinstance(val, (int, float)) and 1990 <= val <= 2030
                    for val in sample_values
                ):
                    year_column = col
                    break

        # If we didn't find by name, use the first column
        if year_column is None:
            year_column = data_section.columns[0]
            logger.info(f"Using first column as years: {year_column}")

        # Map month columns
        month_columns = {}
        for col in data_section.columns:
            if pd.isna(col):
                continue

            col_str = str(col).upper().strip()

            # Specific mapping for each month
            if "ENERO" in col_str or col_str == "ENE":
                month_columns[1] = col
            elif "FEBRERO" in col_str or col_str == "FEB":
                month_columns[2] = col
            elif "MARZO" in col_str or col_str == "MAR":
                month_columns[3] = col
            elif "ABRIL" in col_str or col_str == "ABR":
                month_columns[4] = col
            elif "MAYO" in col_str or col_str == "MAY":
                month_columns[5] = col
            elif "JUNIO" in col_str or col_str == "JUN":
                month_columns[6] = col
            elif "JULIO" in col_str or col_str == "JUL":
                month_columns[7] = col
            elif "AGOSTO" in col_str or col_str == "AGO":
                month_columns[8] = col
            elif (
                "SEPTIEMBRE" in col_str
                or "SETIEMBRE" in col_str
                or col_str == "SEP"
                or col_str == "SET"
            ):
                month_columns[9] = col
            elif "OCTUBRE" in col_str or col_str == "OCT":
                month_columns[10] = col
            elif "NOVIEMBRE" in col_str or col_str == "NOV":
                month_columns[11] = col
            elif "DICIEMBRE" in col_str or col_str == "DIC":
                month_columns[12] = col

        logger.info(f"Mapped month columns: {month_columns}")

        # Process data row by row
        for idx, row in data_section.iterrows():
            try:
                year_raw = row[year_column]

                # Validate year
                if pd.isna(year_raw):
                    continue

                try:
                    year = int(
                        float(year_raw)
                    )  # Convert to float first just in case
                    if year < MIN_VALID_YEAR or year > MAX_VALID_YEAR:
                        continue
                except (ValueError, TypeError):
                    continue

                # Process each month
                for month, col in month_columns.items():
                    try:
                        value_raw = row[col]
                        if pd.isna(value_raw) or value_raw == "":
                            continue

                        # Clean and convert value
                        if isinstance(value_raw, str):
                            # Clean spaces and strange characters
                            value_raw = value_raw.strip()

                            # Handle European format: 1.234,56 or 1234,56
                            if "," in value_raw:
                                # European format with comma as decimal
                                if "." in value_raw:
                                    # Format: 1.234,56 -> 1234.56
                                    value_raw = value_raw.replace(".", "").replace(
                                    ",", "."
                                )
                            else:
                                # Format: 1234,56 -> 1234.56
                                value_raw = value_raw.replace(",", ".")

                            value = float(value_raw)
                        else:
                            value = float(value_raw)

                        # Check that the value is reasonable for UR
                        if (
                            value > 0 and value < 100000
                        ):  # Values between 0 and 100,000 are reasonable
                            records.append((year, month, value))
                            logger.debug(f"Added: {year}-{month:02d} = {value}")

                    except (ValueError, TypeError) as e:
                        logger.debug(
                            f"Error processing value {year}-{month}: {value_raw} - {e}"
                        )
                        continue

            except Exception as e:
                logger.warning(f"Error processing row: {e}")
                continue

        logger.info(f"BHU format: Parsed {len(records)} valid UR records")

        # Show some sample records
        if records:
            records.sort(key=lambda x: (x[0], x[1]))  # Sort by year and month
            logger.info(f"First record: {records[0]}")
            logger.info(f"Last record: {records[-1]}")
            logger.info(f"Sample records: {records[:5]}")

        return records

    def save_to_database(
        self, db: Session, records: List[Tuple[int, int, float]]
    ) -> int:
        """Save UR records to database"""
        if pd is None:
            logger.warning("pandas not available; skipping UR save_to_database")
            return 0
        try:
            saved_count = 0

            for year, month, value in records:
                # Check if already exists
                existing = (
                    db.query(URRecord)
                    .filter(URRecord.year == year, URRecord.month == month)
                    .first()
                )

                if existing:
                    # Update if value changed
                    if existing.value != value:
                        existing.value = value
                        existing.updated_at = datetime.utcnow()
                        saved_count += 1
                else:
                    # Create new record
                    new_record = URRecord(year=year, month=month, value=value)
                    db.add(new_record)
                    saved_count += 1

            db.commit()
            logger.info(f"Saved/updated {saved_count} UR records in database")
            return saved_count

        except Exception as e:
            logger.error(f"Error saving UR records to database: {e}")
            db.rollback()
            return 0

    def refresh_data(self, db: Session) -> Tuple[bool, str, int]:
        """Update UR data by downloading and processing the BHU spreadsheet"""
        if pd is None:
            return False, "pandas not available; UR refresh skipped", 0
        try:
            # Download file
            excel_data = self.download_excel()
            if excel_data is None:
                return False, "Error downloading file from BHU", 0

            # Parse data
            records = self.parse_excel_data(excel_data)
            if not records:
                return False, "Could not extract valid data from file", 0

            # Save to database
            saved_count = self.save_to_database(db, records)

            # Detect if current month value is not yet published.
            # Previous implementation compared tuples (max_year, max_month) < (current_year, current_month)
            # which incorrectly flagged datasets whose latest record belonged to a prior year (e.g., 2023 vs 2025)
            # as a "pending current month" scenario. We only want the special
            # message when we already have data for the current year and are simply
            # waiting for the current (in‑progress) month to appear.
            try:
                from datetime import datetime as _dt
                now = _dt.utcnow()
                current_year, current_month = now.year, now.month
                max_year, max_month = max((y, m) for y, m, _ in records)
                # Only mark missing_current when latest data is from this year and not yet this month
                missing_current = max_year == current_year and max_month < current_month
            except Exception:  # pragma: no cover - defensive
                missing_current = False

            if saved_count > 0:
                return (
                    True,
                    f"UR data updated successfully. {saved_count} records processed",
                    saved_count,
                )
            else:
                if missing_current:
                    from src.utils.constants import MSG_UR_MONTH_NOT_PUBLISHED
                    return True, MSG_UR_MONTH_NOT_PUBLISHED, 0
                return True, "No changes in UR data", 0

        except Exception as e:
            logger.error(f"Error in UR refresh_data: {e}")
            return False, f"Internal error: {str(e)}", 0


class ExchangeRateExcelProcessor:
    """Processor for INE Exchange Rate Excel file (historical data)"""

    def __init__(self):
        self.url = URL_INE_EXCHANGE_RATES
        self.timeout = HTTP_TIMEOUT

    def download_excel(self) -> Optional[Any]:
        """Download Exchange Rate Excel file from INE URL"""
        if pd is None:
            logger.warning("pandas not available; skipping Exchange Excel download")
            return None
        try:
            logger.info("Downloading exchange rate Excel from INE...")
            headers = {"User-Agent": HTTP_USER_AGENT}

            # Use circuit breaker to protect INE API calls
            cb = get_circuit_breaker("INE_API")
            with cb:
                # NOTE: INE server presents incomplete certificate chain (missing intermediate cert).
                # Since this is official government site (.gub.uy), we disable SSL verification.
                # WARNING: Do not use verify=False for untrusted sites.
                logger.warning("INE server has incomplete SSL cert chain - disabling verification")
                # Suppress InsecureRequestWarning for this specific request
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                response = requests.get(
                    self.url, 
                    timeout=self.timeout, 
                    headers=headers,
                    verify=False
                )
                response.raise_for_status()

            # Read Excel file
            excel_data = pd.read_excel(io.BytesIO(response.content), engine="openpyxl")
            logger.info(
                f"Exchange rate Excel downloaded successfully. Rows: {len(excel_data)}"
            )
            return excel_data

        except CircuitBreakerOpenException:
            logger.warning("Circuit breaker is OPEN for INE API - skipping download")
            return None
        except requests.RequestException as e:
            logger.error(f"Error downloading exchange rate file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing exchange rate Excel file: {e}")
            return None

    def parse_excel_data(
        self, excel_data: Any
    ) -> List[Tuple[date, str, float, float, Optional[float]]]:
        """
        Parse INE Exchange Rate Excel data
        Returns a list of tuples (date, currency, buy_rate, sell_rate, average_rate)
        """
        if pd is None:
            logger.warning("pandas not available; cannot parse Exchange Excel data")
            return []
        try:
            records = []

            logger.info(f"Exchange rate file structure: {excel_data.shape}")
            logger.info(f"Detected columns: {list(excel_data.columns)}")
            logger.info(f"First 5 rows:\n{excel_data.head()}")

            # Currency mappings based on INE Excel structure
            currency_mappings = [
                ("USD", "Dólar.USA.Compra", "Dólar.USA.Venta"),
                ("EUR", "Euro.Compra", "Euro.Venta"),
                ("ARS", "Peso.Argentino.Compra", "Peso.Argentino.Venta"),
                ("BRL", "Real.Compra", "Real.Venta"),
                # Note: Dólar.eBROU is a different modality, we'll map it as USD_EBROU if needed
            ]

            for _, row in excel_data.iterrows():
                try:
                    # Skip empty rows or headers
                    if row.isna().all():
                        continue

                    # Extract and parse date
                    date_raw = row["Fecha"]
                    if pd.isna(date_raw) or date_raw == "Fecha":  # Skip header rows
                        continue

                    # Parse date (DD-MM-YYYY format)
                    try:
                        if isinstance(date_raw, str):
                            # Try different date formats
                            date_formats = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"]
                            parsed_date = None
                            for fmt in date_formats:
                                try:
                                    parsed_date = datetime.strptime(
                                        date_raw, fmt
                                    ).date()
                                    break
                                except ValueError:
                                    continue

                            if parsed_date is None:
                                logger.debug(f"Could not parse date: {date_raw}")
                                continue
                        elif isinstance(date_raw, datetime):
                            parsed_date = date_raw.date()
                        else:
                            logger.debug(
                                f"Unknown date format: {date_raw} (type: {type(date_raw)})"
                            )
                            continue
                    except Exception as e:
                        logger.debug(f"Error parsing date {date_raw}: {e}")
                        continue

                    # Extract exchange rates for each currency
                    for currency_code, buy_col, sell_col in currency_mappings:
                        try:
                            buy_rate_raw = row[buy_col]
                            sell_rate_raw = row[sell_col]

                            # Skip if both values are missing or invalid
                            if (pd.isna(buy_rate_raw) or buy_rate_raw == "..") and (
                                pd.isna(sell_rate_raw) or sell_rate_raw == ".."
                            ):
                                continue

                            # Parse buy rate
                            buy_rate = self._parse_rate_value(buy_rate_raw)
                            if buy_rate is None:
                                continue

                            # Parse sell rate
                            sell_rate = self._parse_rate_value(sell_rate_raw)
                            if sell_rate is None:
                                continue

                            # Calculate average rate
                            average_rate = round((buy_rate + sell_rate) / 2, 4)

                            # Add record
                            records.append(
                                (
                                    parsed_date,
                                    currency_code,
                                    buy_rate,
                                    sell_rate,
                                    average_rate,
                                )
                            )

                        except Exception as e:
                            logger.debug(
                                f"Error processing {currency_code} for date {parsed_date}: {e}"
                            )
                            continue

                except Exception as e:
                    logger.warning(f"Error processing exchange rate row: {e}")
                    continue

            logger.info(f"Parsed {len(records)} exchange rate records")

            # Show some sample records for verification
            if records:
                records.sort(key=lambda x: (x[0], x[1]))  # Sort by date and currency
                logger.info(f"First record: {records[0]}")
                logger.info(f"Last record: {records[-1]}")
                logger.info(f"Sample records: {records[:10]}")

            return records

        except Exception as e:
            logger.error(f"Error parsing exchange rate Excel data: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return []

    def _parse_rate_value(self, value) -> Optional[float]:
        """Parse a rate value from the Excel, handling various formats"""
        if pd is None:
            logger.warning("pandas not available; skipping exchange save_to_database")
            return -1
        try:
            # Handle missing values
            if pd.isna(value) or value == ".." or value == "":
                return None

            # Convert to string and clean
            if not isinstance(value, str):
                value = str(value)

            # Remove any non-numeric characters except decimal separators
            cleaned = value.strip()

            # Handle different decimal separators
            if "," in cleaned and "." in cleaned:
                # Assume comma is thousands separator, dot is decimal
                cleaned = cleaned.replace(",", "")
            elif "," in cleaned and "." not in cleaned:
                # Assume comma is decimal separator
                cleaned = cleaned.replace(",", ".")

            # Try to convert to float
            rate = float(cleaned)

            # Validate reasonable range (exchange rates should be positive and reasonable)
            if rate <= 0 or rate > 10000:
                logger.debug(f"Rate value out of reasonable range: {rate}")
                return None

            return round(rate, 4)

        except (ValueError, TypeError) as e:
            logger.debug(f"Could not parse rate value '{value}': {e}")
            return None

    def save_to_database(
        self,
        db: Session,
        records: List[Tuple[date, str, float, float, Optional[float]]],
    ) -> int:
        """Save exchange rate records to database"""
        if pd is None:
            return False, "pandas not available; exchange refresh skipped", 0
        try:
            saved_count = 0
            seen: set[tuple[date, str]] = set()

            for record_date, currency, buy_rate, sell_rate, average_rate in records:
                # Skip unsupported
                if currency not in SUPPORTED_CURRENCIES:
                    continue
                key = (record_date, currency)
                if key in seen:
                    # Avoid intra-batch duplicates that would trigger UNIQUE constraint
                    continue
                seen.add(key)

                existing = (
                    db.query(ExchangeRateRecord)
                    .filter(
                        ExchangeRateRecord.date == record_date,
                        ExchangeRateRecord.currency == currency,
                    )
                    .first()
                )

                if existing:
                    if (
                        existing.buy_rate != buy_rate
                        or existing.sell_rate != sell_rate
                        or existing.average_rate != average_rate
                    ):
                        existing.buy_rate = buy_rate
                        existing.sell_rate = sell_rate
                        existing.average_rate = average_rate
                        existing.updated_at = datetime.utcnow()
                        saved_count += 1
                else:
                    db.add(
                        ExchangeRateRecord(
                            date=record_date,
                            currency=currency,
                            buy_rate=buy_rate,
                            sell_rate=sell_rate,
                            average_rate=average_rate,
                            arbitrage=None,
                        )
                    )
                    saved_count += 1

            db.commit()
            logger.info(
                f"Saved/updated {saved_count} exchange rate records (unique batch size={len(seen)})"
            )
            return saved_count

        except Exception as e:
            logger.error(f"Error saving exchange rates to database: {e}")
            db.rollback()
            return -1  # sentinel for failure

    def refresh_data(self, db: Session) -> Tuple[bool, str, int]:
        """Update historical exchange rate data by downloading and processing the INE Excel"""
        try:
            # Download file
            excel_data = self.download_excel()
            if excel_data is None:
                return False, "Error downloading exchange rate file from INE", 0

            # Parse data
            records = self.parse_excel_data(excel_data)
            if not records:
                return False, "Could not extract valid exchange rate data from file", 0

            existing_before = db.query(ExchangeRateRecord).count()
            saved_count = self.save_to_database(db, records)

            if saved_count == -1:
                return False, "Failed to persist exchange rate data", 0
            if saved_count > 0:
                return (
                    True,
                    f"Exchange rate data updated successfully. {saved_count} records processed",
                    saved_count,
                )
            # saved_count == 0
            if existing_before == 0:
                # We parsed records but could not save new ones; treat as failure
                return (
                    False,
                    "Parsed data but no records saved (possible duplicate/constraint issue)",
                    0,
                )
            return True, "No changes in exchange rate data", 0

        except Exception as e:
            logger.error(f"Error in exchange rate refresh_data: {e}")
            return False, f"Internal error: {str(e)}", 0


class ExchangeRateBCUProcessor:
    """Processor for BCU real-time exchange rates (current day data)"""

    def __init__(self):
        self.url = URL_BCU_EXCHANGE_RATES
        self.timeout = HTTP_TIMEOUT

    def get_current_rates_from_webservice(
        self,
    ) -> Tuple[List[Tuple[str, float, float, Optional[float]]], bool]:
        """Get current exchange rates using official BCU webservice

        Returns:
            Tuple containing:
            - List of rates: (currency, buy, sell, average)
            - Boolean indicating if data is from BCU webservice (True) or fallback (False)
        """
        try:
            from py_bcu.bcu_cotizacion import get_cotizacion

            logger.info("Getting current exchange rates from BCU webservice...")

            # Códigos de monedas principales del BCU
            currency_codes = {
                2225: "USD",  # DLS. USA BILLETE
                1111: "EUR",  # EURO
                1001: "BRL",  # REAL BILLETE
                501: "ARS",  # PESO ARG.BILLETE
            }

            rates = []
            successful_requests = 0

            for code, currency in currency_codes.items():
                try:
                    # Get cotization from BCU webservice
                    cotizacion = get_cotizacion(moneda=code)

                    if cotizacion and len(cotizacion) >= 2:
                        buy_rate = float(cotizacion[0])
                        sell_rate = float(cotizacion[1])

                        # BCU typically returns same value for buy and sell, use single rate
                        if buy_rate == sell_rate:
                            single_rate = buy_rate
                            rates.append(
                                (currency, single_rate, single_rate, single_rate)
                            )
                            successful_requests += 1
                            logger.info(f"Successfully got {currency}: {single_rate}")
                        else:
                            # Different buy/sell rates (rare case)
                            avg_rate = (buy_rate + sell_rate) / 2
                            rates.append((currency, buy_rate, sell_rate, avg_rate))
                            successful_requests += 1
                            logger.info(
                                f"Successfully got {currency}: buy={buy_rate}, sell={sell_rate}"
                            )
                    else:
                        logger.warning(
                            f"Invalid cotization data for {currency}: {cotizacion}"
                        )

                except Exception as e:
                    logger.error(
                        f"Error getting cotization for {currency} (code {code}): {e}"
                    )
                    continue

            # Validate we got enough currencies
            if successful_requests >= 4:  # At least 4 currencies
                logger.info(
                    f"Successfully retrieved {successful_requests} currencies from BCU webservice"
                )
                return rates, True
            else:
                logger.warning(
                    f"Only got {successful_requests} currencies from BCU webservice, using fallback"
                )
                return self._get_sample_current_rates(), False

        except ImportError:
            logger.error("py_bcu library not available, using fallback")
            return self._get_latest_historical_rates(), False
        except Exception as e:
            logger.error(f"Error using BCU webservice: {e}")
            return self._get_latest_historical_rates(), False

    def get_current_rates(
        self,
    ) -> Tuple[List[Tuple[str, float, float, Optional[float]]], bool]:
        """Get current exchange rates from BCU

        Returns:
            Tuple containing:
            - List of rates: (currency, buy, sell, average)
            - Boolean indicating if data is from BCU webservice (True) or historical data fallback (False)
        """
        try:
            logger.info("Getting current exchange rates from BCU...")

            # First try: Official BCU webservice (most reliable)
            try:
                rates, is_from_webservice = self.get_current_rates_from_webservice()
                if is_from_webservice and rates:
                    logger.info(
                        f"Successfully got {len(rates)} rates from BCU webservice"
                    )
                    return rates, True
            except Exception as e:
                logger.warning(f"BCU webservice failed: {e}")

            # Fallback to historical data (real data from database)
            logger.warning(
                "BCU webservice not available, using latest historical exchange rates"
            )
            return self._get_latest_historical_rates(), False

        except Exception as e:
            logger.error(f"Error getting current rates: {e}")
            return self._get_latest_historical_rates(), False

    def _get_latest_historical_rates(
        self,
    ) -> List[Tuple[str, float, float, Optional[float]]]:
        """Get latest historical exchange rates from database as fallback"""
        try:
            from src.domain.services import ExchangeRateService
            from src.infrastructure.database import get_db

            # Get database session
            db = next(get_db())
            service = ExchangeRateService(db)

            # Get latest historical rates
            latest_rates = service.get_latest_exchange_rates()

            if latest_rates:
                result = []
                for rate in latest_rates:
                    # Convert to the expected format
                    result.append(
                        (
                            rate.currency,
                            float(rate.buy_rate)
                            if rate.buy_rate
                            else float(rate.average_rate),
                            float(rate.sell_rate)
                            if rate.sell_rate
                            else float(rate.average_rate),
                            float(rate.average_rate) if rate.average_rate else None,
                        )
                    )

                logger.info(
                    f"Retrieved {len(result)} historical exchange rates as fallback"
                )
                return result
            else:
                logger.warning(
                    "No historical rates available, using minimal sample data"
                )
                return self._get_minimal_sample_rates()

        except Exception as e:
            logger.error(f"Error getting historical rates: {e}")
            return self._get_minimal_sample_rates()

    def _get_minimal_sample_rates(
        self,
    ) -> List[Tuple[str, float, float, Optional[float]]]:
        """Get minimal sample rates as last resort fallback"""
        logger.warning("Using minimal sample rates as last resort")
        return [
            ("USD", 41.50, 42.00, 41.75),
            ("EUR", 45.80, 46.50, 46.15),
            ("ARS", 0.041, 0.043, 0.042),
            ("BRL", 7.60, 7.80, 7.70),
        ]



