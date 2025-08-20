// Script simple para probar la API desde Node.js o navegador

const API_URL = 'https://w6scjpjua3bmj272d2dqhxy2ve0yrkpf.lambda-url.us-east-1.on.aws';

/**
 * Función para probar la API del Boletín Oficial
 * @param {string} fecha - Fecha en formato YYYY-MM-DD
 * @param {boolean} forzarReanalisis - Forzar reanálisis
 */
async function testAPI(fecha = '2024-12-15', forzarReanalisis = false) {
    console.log('🚀 Iniciando test de API...');
    console.log(`📅 Fecha: ${fecha}`);
    console.log(`🔄 Forzar reanálisis: ${forzarReanalisis}`);
    console.log(`🌐 URL: ${API_URL}`);
    console.log('⏳ Enviando petición...\n');

    const startTime = Date.now();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify({
                fecha: fecha,
                forzar_reanalisis: forzarReanalisis
            })
        });

        const endTime = Date.now();
        const duration = ((endTime - startTime) / 1000).toFixed(2);

        console.log(`⏱️ Tiempo de respuesta: ${duration}s`);
        console.log(`📊 Status: ${response.status} ${response.statusText}`);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Error en la respuesta:');
            console.error(errorText);
            return;
        }

        const data = await response.json();
        
        console.log('\n✅ RESPUESTA EXITOSA:');
        console.log('==========================================');
        
        if (data.success) {
            const analisis = data.data;
            
            console.log(`📊 RESUMEN:`);
            console.log(analisis.analisis?.resumen || 'No disponible');
            
            console.log(`\n📋 CAMBIOS PRINCIPALES (${analisis.analisis?.cambios_principales?.length || 0}):`);
            analisis.analisis?.cambios_principales?.forEach((cambio, i) => {
                console.log(`${i + 1}. ${cambio.tipo?.toUpperCase()}: ${cambio.titulo}`);
                console.log(`   📄 ${cambio.descripcion}`);
                console.log(`   📈 Impacto: ${cambio.impacto} - ${cambio.justificacion_impacto}\n`);
            });
            
            console.log(`🎯 IMPACTO ESTIMADO:`);
            console.log(analisis.analisis?.impacto_estimado || 'No disponible');
            
            console.log(`\n🏛️ ÁREAS AFECTADAS:`);
            console.log(analisis.analisis?.areas_afectadas?.join(', ') || 'No especificadas');
            
            console.log(`\n👥 OPINIONES DE EXPERTOS (${analisis.opiniones_expertos?.length || 0}):`);
            analisis.opiniones_expertos?.forEach((opinion, i) => {
                console.log(`${i + 1}. ${opinion.medio} - ${opinion.relevancia?.toUpperCase()}`);
                console.log(`   📰 ${opinion.titulo}`);
                console.log(`   ✍️ ${opinion.autor}`);
                console.log(`   💭 ${opinion.opinion_resumen}`);
                console.log(`   🔗 ${opinion.url || 'Sin URL'}\n`);
            });
            
            console.log(`📈 METADATOS:`);
            console.log(`• Fecha: ${analisis.fecha}`);
            console.log(`• Desde caché: ${analisis.metadatos?.desde_cache ? 'Sí' : 'No'}`);
            console.log(`• Tiempo procesamiento: ${analisis.metadatos?.tiempo_procesamiento}s`);
            console.log(`• Modelo usado: ${analisis.metadatos?.modelo_llm_usado}`);
            console.log(`• Método: ${analisis.metadatos?.metodo_analisis}`);
            
        } else {
            console.error('❌ La API retornó success: false');
            console.error('Mensaje:', data.message);
            console.error('Error:', data.error);
        }

    } catch (error) {
        const endTime = Date.now();
        const duration = ((endTime - startTime) / 1000).toFixed(2);
        
        console.error(`\n❌ ERROR DESPUÉS DE ${duration}s:`);
        console.error('==========================================');
        console.error('Tipo:', error.name);
        console.error('Mensaje:', error.message);
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            console.error('\n💡 POSIBLES CAUSAS:');
            console.error('• CORS: El navegador bloquea la petición');
            console.error('• Red: Sin conexión a internet');
            console.error('• DNS: No se puede resolver la URL');
        } else if (error.name === 'AbortError') {
            console.error('\n💡 CAUSA: Timeout - La petición tardó demasiado');
        }
    }
}

/**
 * Función para probar conectividad básica
 */
async function testConnection() {
    console.log('🔗 Probando conectividad básica...');
    
    try {
        const response = await fetch(API_URL, {
            method: 'OPTIONS'
        });
        
        console.log(`✅ Conectividad OK - Status: ${response.status}`);
        console.log('Headers disponibles:', [...response.headers.keys()]);
        
    } catch (error) {
        console.error('❌ Error de conectividad:', error.message);
    }
}

// Si se ejecuta en Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { testAPI, testConnection };
}

// Si se ejecuta en navegador, exponer funciones globalmente
if (typeof window !== 'undefined') {
    window.testAPI = testAPI;
    window.testConnection = testConnection;
}

// Ejemplo de uso
console.log('📋 EJEMPLOS DE USO:');
console.log('==========================================');
console.log('// Test básico con fecha específica:');
console.log('testAPI("2024-12-15", false);');
console.log('');
console.log('// Test con reanálisis forzado:');
console.log('testAPI("2024-12-15", true);');
console.log('');
console.log('// Test de conectividad:');
console.log('testConnection();');
console.log('==========================================\n');