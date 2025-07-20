import pytest
import tempfile
import os
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db, URRecord
from services import URService
from models import URValue, URResponse
from excel_processor import URExcelProcessor


# Configuración de base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_ur.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dependencia de base de datos para tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Configurar base de datos de prueba"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Sesión de base de datos para tests"""
    # Limpiar todas las tablas antes de cada test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Cliente de prueba para FastAPI"""
    return TestClient(app)


@pytest.fixture
def sample_ur_data(db_session):
    """Datos de muestra para UR"""
    sample_records = [
        URRecord(año=2023, mes=1, valor=1501.26),
        URRecord(año=2023, mes=2, valor=1502.25),
        URRecord(año=2023, mes=3, valor=1579.57),
        URRecord(año=2024, mes=1, valor=1650.00),
        URRecord(año=2024, mes=2, valor=1675.50),
        URRecord(año=2025, mes=1, valor=1800.00),
        URRecord(año=2025, mes=6, valor=1827.25),
    ]
    
    for record in sample_records:
        db_session.add(record)
    db_session.commit()
    
    return sample_records


class TestURService:
    """Tests para el servicio URService"""
    
    def test_get_ur_by_year_month_exists(self, db_session, sample_ur_data):
        """Test obtener UR por año y mes que existe"""
        service = URService(db_session)
        result = service.get_ur_by_year_month(2023, 1)
        
        assert result is not None
        assert result.año == 2023
        assert result.mes == 1
        assert result.valor == 1501.26
    
    def test_get_ur_by_year_month_not_exists(self, db_session, sample_ur_data):
        """Test obtener UR por año y mes que no existe"""
        service = URService(db_session)
        result = service.get_ur_by_year_month(2023, 12)
        
        assert result is None
    
    def test_get_ur_by_year(self, db_session, sample_ur_data):
        """Test obtener todos los valores UR de un año"""
        service = URService(db_session)
        results = service.get_ur_by_year(2023)
        
        assert len(results) == 3
        assert all(r.año == 2023 for r in results)
        assert results[0].mes == 1  # Ordenados por mes
        assert results[1].mes == 2
        assert results[2].mes == 3
    
    def test_get_ur_by_year_empty(self, db_session, sample_ur_data):
        """Test obtener UR de un año sin datos"""
        service = URService(db_session)
        results = service.get_ur_by_year(2022)
        
        assert len(results) == 0
    
    def test_get_ur_by_range_same_year(self, db_session, sample_ur_data):
        """Test obtener UR por rango en el mismo año"""
        service = URService(db_session)
        results = service.get_ur_by_range(2023, 1, 2023, 3)
        
        assert len(results) == 3
        assert all(r.año == 2023 for r in results)
        assert results[0].mes == 1
        assert results[2].mes == 3
    
    def test_get_ur_by_range_multiple_years(self, db_session, sample_ur_data):
        """Test obtener UR por rango de múltiples años"""
        service = URService(db_session)
        results = service.get_ur_by_range(2023, 2, 2024, 1)
        
        assert len(results) == 3  # 2023: feb, mar + 2024: ene
        assert results[0].año == 2023 and results[0].mes == 2
        assert results[1].año == 2023 and results[1].mes == 3
        assert results[2].año == 2024 and results[2].mes == 1
    
    def test_get_latest_ur(self, db_session, sample_ur_data):
        """Test obtener el valor más reciente de UR"""
        service = URService(db_session)
        result = service.get_latest_ur()
        
        assert result is not None
        assert result.año == 2025
        assert result.mes == 6
        assert result.valor == 1827.25
    
    def test_get_total_records(self, db_session, sample_ur_data):
        """Test contar total de registros UR"""
        service = URService(db_session)
        total = service.get_total_records()
        
        assert total == 7
    
    def test_get_year_range_available(self, db_session, sample_ur_data):
        """Test obtener rango de años disponibles"""
        service = URService(db_session)
        min_year, max_year = service.get_year_range_available()
        
        assert min_year == 2023
        assert max_year == 2025
    
    def test_get_available_years(self, db_session, sample_ur_data):
        """Test obtener años disponibles"""
        service = URService(db_session)
        years = service.get_available_years()
        
        assert years == [2025, 2024, 2023]  # Ordenados descendente


class TestURAPI:
    """Tests para los endpoints de la API de UR"""
    
    def test_get_latest_ur_success(self, client, sample_ur_data):
        """Test endpoint obtener último valor UR"""
        response = client.get("/api/ur/latest")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["año"] == 2025
        assert data["data"]["mes"] == 6
        assert data["data"]["valor"] == 1827.25
    
    def test_get_ur_by_year_month_success(self, client, sample_ur_data):
        """Test endpoint obtener UR por año y mes"""
        response = client.get("/api/ur/year-month/2023/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["año"] == 2023
        assert data["data"]["mes"] == 1
        assert data["data"]["valor"] == 1501.26
    
    def test_get_ur_by_year_month_not_found(self, client, sample_ur_data):
        """Test endpoint UR por año y mes no encontrado"""
        response = client.get("/api/ur/year-month/2023/12")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No hay datos de UR disponibles" in data["message"]
    
    def test_get_ur_by_year_month_invalid_month(self, client, sample_ur_data):
        """Test endpoint UR con mes inválido"""
        response = client.get("/api/ur/year-month/2023/13")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "El mes debe estar entre 1 y 12" in data["message"]
    
    def test_get_ur_by_year_success(self, client, sample_ur_data):
        """Test endpoint obtener UR por año"""
        response = client.get("/api/ur/year/2023")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3
        assert all(item["año"] == 2023 for item in data["data"])
    
    def test_get_ur_by_year_empty(self, client, sample_ur_data):
        """Test endpoint UR por año sin datos"""
        response = client.get("/api/ur/year/2022")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No hay datos de UR disponibles" in data["message"]
    
    def test_get_ur_by_range_success(self, client, sample_ur_data):
        """Test endpoint obtener UR por rango"""
        response = client.get("/api/ur/range/2023/1/2023/3")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3
    
    def test_get_ur_by_range_invalid_months(self, client, sample_ur_data):
        """Test endpoint UR por rango con meses inválidos"""
        response = client.get("/api/ur/range/2023/0/2023/13")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Los meses deben estar entre 1 y 12" in data["message"]
    
    def test_get_ur_by_range_invalid_range(self, client, sample_ur_data):
        """Test endpoint UR por rango inválido"""
        response = client.get("/api/ur/range/2024/6/2024/3")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "El período de inicio debe ser anterior" in data["message"]
    
    def test_get_ur_by_range_post(self, client, sample_ur_data):
        """Test endpoint POST para obtener UR por rango"""
        payload = {
            "año_inicio": 2023,
            "mes_inicio": 1,
            "año_fin": 2023,
            "mes_fin": 2
        }
        response = client.post("/api/ur/range", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
    
    def test_get_ur_info(self, client, sample_ur_data):
        """Test endpoint información general de UR"""
        response = client.get("/api/ur/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_records"] == 7
        assert data["data"]["year_range"]["min_year"] == 2023
        assert data["data"]["year_range"]["max_year"] == 2025
        assert len(data["data"]["available_years"]) == 3


class TestURExcelProcessor:
    """Tests para el procesador de Excel de UR"""
    
    def test_parse_excel_data_empty(self):
        """Test parsear datos vacíos"""
        import pandas as pd
        processor = URExcelProcessor()
        
        empty_df = pd.DataFrame()
        result = processor.parse_excel_data(empty_df)
        
        assert result == []
    
    def test_parse_excel_data_sample(self):
        """Test parsear datos de muestra"""
        import pandas as pd
        processor = URExcelProcessor()
        
        # Crear datos de muestra que simulan el formato del BHU
        data = {
            'AÑO': [2023, 2024],
            'ENERO': [1501.26, 1650.00],
            'FEBRERO': [1502.25, 1675.50],
            'MARZO': [1579.57, None]
        }
        df = pd.DataFrame(data)
        
        # Simular que la primera fila contiene los encabezados
        # Insertamos una fila de encabezados
        header_row = pd.DataFrame([['AÑO', 'ENERO', 'FEBRERO', 'MARZO']], columns=df.columns)
        df_with_header = pd.concat([header_row, df], ignore_index=True)
        
        result = processor.parse_excel_data(df_with_header)
        
        # Verificar que se parsearon correctamente
        assert len(result) >= 4  # Al menos 4 registros válidos
        
        # Verificar algunos valores específicos
        records_dict = {(r[0], r[1]): r[2] for r in result}
        assert records_dict.get((2023, 1)) == 1501.26
        assert records_dict.get((2023, 2)) == 1502.25
        assert records_dict.get((2024, 1)) == 1650.00


class TestURModels:
    """Tests para los modelos de UR"""
    
    def test_ur_value_creation(self):
        """Test creación de URValue"""
        ur_value = URValue(año=2023, mes=6, valor=1500.50)
        
        assert ur_value.año == 2023
        assert ur_value.mes == 6
        assert ur_value.valor == 1500.50
    
    def test_ur_value_validation(self):
        """Test validación de URValue"""
        # Test con datos válidos
        ur_value = URValue(año=2023, mes=12, valor=1500.50)
        assert ur_value.mes == 12
        
        # Test serialización
        data = ur_value.dict()
        assert data["año"] == 2023
        assert data["mes"] == 12
        assert data["valor"] == 1500.50
    
    def test_ur_response_success(self):
        """Test URResponse exitoso"""
        ur_value = URValue(año=2023, mes=6, valor=1500.50)
        response = URResponse(
            success=True,
            message="Test exitoso",
            data=ur_value
        )
        
        assert response.success is True
        assert response.message == "Test exitoso"
        assert response.data.año == 2023
    
    def test_ur_response_list(self):
        """Test URResponse con lista de datos"""
        ur_values = [
            URValue(año=2023, mes=1, valor=1500.50),
            URValue(año=2023, mes=2, valor=1510.75)
        ]
        response = URResponse(
            success=True,
            message="Lista de valores",
            data=ur_values
        )
        
        assert response.success is True
        assert len(response.data) == 2
        assert response.data[0].mes == 1
        assert response.data[1].mes == 2


# Tests de integración
class TestURIntegration:
    """Tests de integración para UR"""
    
    def test_full_workflow(self, client, db_session):
        """Test del flujo completo: cargar datos, consultar API"""
        # 1. Agregar datos de prueba directamente
        sample_records = [
            URRecord(año=2023, mes=6, valor=1500.00),
            URRecord(año=2023, mes=7, valor=1510.00),
        ]
        
        for record in sample_records:
            db_session.add(record)
        db_session.commit()
        
        # 2. Probar endpoint latest
        response = client.get("/api/ur/latest")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 3. Probar endpoint específico
        response = client.get("/api/ur/year-month/2023/6")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["valor"] == 1500.00
        
        # 4. Probar endpoint de año
        response = client.get("/api/ur/year/2023")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2


if __name__ == "__main__":
    # Ejecutar tests específicos para debugging
    pytest.main([__file__, "-v", "--tb=short"]) 