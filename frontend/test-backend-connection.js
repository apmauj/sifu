import axios from 'axios';

// Configuración para conectarse al backend local en Docker
const API_BASE_URL = 'http://localhost:8000';

async function testBackendConnection() {
  console.log('🧪 Probando conexión con el backend en Docker...\n');

  try {
    // Test 1: Health check
    console.log('1. Probando endpoint de health...');
    const healthResponse = await axios.get(`${API_BASE_URL}/api/health`);
    console.log('✅ Health check exitoso:', healthResponse.data);

    // Test 2: BROU endpoint
    console.log('\n2. Probando endpoint BROU...');
    const brouResponse = await axios.get(`${API_BASE_URL}/api/brou/current`);
    console.log('✅ BROU endpoint exitoso -', brouResponse.data.length, 'monedas obtenidas');

    // Test 3: Performance budgets
    console.log('\n3. Probando endpoint de performance budgets...');
    const budgetsResponse = await axios.get(`${API_BASE_URL}/api/performance/budgets`);
    console.log('✅ Performance budgets endpoint exitoso:', budgetsResponse.data);

    // Test 4: Performance status
    console.log('\n4. Probando endpoint de performance status...');
    const statusResponse = await axios.get(`${API_BASE_URL}/api/performance/budgets/status`);
    console.log('✅ Performance status endpoint exitoso:', statusResponse.data);

    // Test 5: Throughput metrics
    console.log('\n5. Probando endpoint de throughput...');
    const throughputResponse = await axios.get(`${API_BASE_URL}/api/performance/throughput`);
    console.log('✅ Throughput endpoint exitoso:', throughputResponse.data);

    console.log('\n🎉 ¡Todas las pruebas pasaron exitosamente!');
    console.log('📊 El frontend puede conectarse correctamente al backend en Docker');

  } catch (error) {
    console.error('❌ Error en la conexión:', error.message);
    if (error.response) {
      console.error('   Status:', error.response.status);
      console.error('   Data:', error.response.data);
    }
  }
}

// Ejecutar la prueba
testBackendConnection();
