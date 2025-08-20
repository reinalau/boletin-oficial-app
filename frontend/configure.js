#!/usr/bin/env node

/**
 * Script de configuración para el frontend
 * Configura la URL de Lambda Function desde Terraform output
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔧 Configurando frontend con URL de Lambda...');

try {
  // Cambiar al directorio de Terraform
  const terraformDir = path.join(__dirname, '..', 'scripts', 'iac');
  process.chdir(terraformDir);
  
  // Obtener la URL de Lambda desde Terraform
  console.log('📡 Obteniendo URL de Lambda desde Terraform...');
  const terraformOutput = execSync('terraform output -json', { encoding: 'utf8' });
  const outputs = JSON.parse(terraformOutput);
  
  const lambdaUrl = outputs.lambda_function_url?.value;
  
  if (!lambdaUrl) {
    throw new Error('No se pudo obtener lambda_function_url desde Terraform output');
  }
  
  console.log('✅ URL de Lambda obtenida:', lambdaUrl);
  
  // Actualizar el meta tag en index.html
  const indexPath = path.join(__dirname, 'index.html');
  let indexContent = fs.readFileSync(indexPath, 'utf8');
  
  // Buscar y reemplazar el meta tag
  const metaTagRegex = /<meta name="lambda-function-url" content="[^"]*">/;
  const newMetaTag = `<meta name="lambda-function-url" content="${lambdaUrl}">`;
  
  if (metaTagRegex.test(indexContent)) {
    indexContent = indexContent.replace(metaTagRegex, newMetaTag);
    console.log('🔄 Actualizando meta tag en index.html...');
  } else {
    // Si no existe, agregarlo después de los otros meta tags
    const insertPoint = indexContent.indexOf('<!-- Configuración de API');
    if (insertPoint !== -1) {
      const beforeInsert = indexContent.substring(0, insertPoint);
      const afterInsert = indexContent.substring(insertPoint);
      indexContent = beforeInsert + `<!-- Configuración de API - Actualizar con tu URL de Lambda -->\n    ${newMetaTag}\n    \n    ` + afterInsert.replace('<!-- Configuración de API - Actualizar con tu URL de Lambda -->\n    <meta name="lambda-function-url" content="https://stpnwotleex7abzoxw437lc4240cbwvy.lambda-url.us-east-1.on.aws">', '');
    }
    console.log('➕ Agregando meta tag a index.html...');
  }
  
  fs.writeFileSync(indexPath, indexContent);
  
  // Crear archivo .env si no existe
  const envPath = path.join(__dirname, '.env');
  if (!fs.existsSync(envPath)) {
    const envContent = `# Configuración automática generada por configure.js
LAMBDA_FUNCTION_URL=${lambdaUrl}
`;
    fs.writeFileSync(envPath, envContent);
    console.log('📝 Archivo .env creado');
  } else {
    console.log('ℹ️ Archivo .env ya existe, no se modificó');
  }
  
  console.log('🎉 Configuración completada exitosamente!');
  console.log('');
  console.log('📋 Próximos pasos:');
  console.log('  1. Verificar que index.html tenga la URL correcta');
  console.log('  2. Desplegar el frontend a tu hosting (Vercel, Netlify, etc.)');
  console.log('  3. Probar la aplicación');
  
} catch (error) {
  console.error('❌ Error configurando frontend:', error.message);
  console.error('');
  console.error('💡 Soluciones posibles:');
  console.error('  1. Asegurar que Terraform esté desplegado: cd scripts/iac && terraform apply');
  console.error('  2. Verificar que terraform output funcione correctamente');
  console.error('  3. Configurar manualmente el meta tag en index.html');
  process.exit(1);
}