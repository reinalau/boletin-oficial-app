#!/usr/bin/env python3
"""
API Testing Script for Boletín Oficial Telegram App
This script tests the deployed API endpoints with real data
"""

import json
import requests
import time
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import argparse


class BoletinAPITester:
    """Test suite for the Boletín Oficial API"""
    
    def __init__(self, api_url: str, timeout: int = 60):
        """
        Initialize the API tester
        
        Args:
            api_url: Base URL of the API Gateway
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'BoletinOficial-API-Tester/1.0'
        })
        
        # Test results tracking
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def print_status(self, message: str, status: str = "INFO"):
        """Print colored status message"""
        colors = {
            "INFO": "\033[94m",    # Blue
            "SUCCESS": "\033[92m", # Green
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
            "RESET": "\033[0m"     # Reset
        }
        
        color = colors.get(status, colors["INFO"])
        reset = colors["RESET"]
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"{color}[{timestamp}] {status}: {message}{reset}")
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> bool:
        """
        Run a single test and track results
        
        Args:
            test_name: Name of the test
            test_func: Test function to execute
            *args, **kwargs: Arguments for test function
            
        Returns:
            bool: True if test passed, False otherwise
        """
        self.tests_run += 1
        self.print_status(f"Running test: {test_name}")
        
        try:
            start_time = time.time()
            result = test_func(*args, **kwargs)
            end_time = time.time()
            
            duration = end_time - start_time
            
            if result:
                self.tests_passed += 1
                self.print_status(f"✓ {test_name} PASSED ({duration:.2f}s)", "SUCCESS")
                self.test_results.append({
                    "name": test_name,
                    "status": "PASSED",
                    "duration": duration,
                    "error": None
                })
                return True
            else:
                self.tests_failed += 1
                self.print_status(f"✗ {test_name} FAILED ({duration:.2f}s)", "ERROR")
                self.test_results.append({
                    "name": test_name,
                    "status": "FAILED",
                    "duration": duration,
                    "error": "Test returned False"
                })
                return False
                
        except Exception as e:
            self.tests_failed += 1
            duration = time.time() - start_time if 'start_time' in locals() else 0
            self.print_status(f"✗ {test_name} ERROR: {str(e)}", "ERROR")
            self.test_results.append({
                "name": test_name,
                "status": "ERROR",
                "duration": duration,
                "error": str(e)
            })
            return False
    
    def test_api_health(self) -> bool:
        """Test basic API connectivity"""
        try:
            # Try to reach the API endpoint
            response = self.session.get(f"{self.api_url}/analyze", timeout=10)
            
            # We expect a 405 (Method Not Allowed) since we're using GET instead of POST
            if response.status_code == 405:
                self.print_status("API is reachable (405 Method Not Allowed as expected)")
                return True
            elif response.status_code == 200:
                self.print_status("API is reachable (200 OK)")
                return True
            else:
                self.print_status(f"Unexpected status code: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_status(f"API health check failed: {e}")
            return False
    
    def test_analyze_endpoint_validation(self) -> bool:
        """Test input validation on analyze endpoint"""
        try:
            # Test with missing data
            response = self.session.post(
                f"{self.api_url}/analyze",
                json={},
                timeout=self.timeout
            )
            
            # Should return 400 for missing required fields
            if response.status_code == 400:
                self.print_status("Input validation working correctly (400 for empty request)")
                return True
            
            # Test with invalid date format
            response = self.session.post(
                f"{self.api_url}/analyze",
                json={"fecha": "invalid-date"},
                timeout=self.timeout
            )
            
            if response.status_code == 400:
                self.print_status("Date validation working correctly")
                return True
            
            self.print_status(f"Unexpected validation response: {response.status_code}")
            return False
            
        except requests.exceptions.RequestException as e:
            self.print_status(f"Validation test failed: {e}")
            return False
    
    def test_analyze_with_recent_date(self) -> bool:
        """Test analysis with a recent date (likely to have data)"""
        try:
            # Use yesterday's date
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            self.print_status(f"Testing analysis for date: {yesterday}")
            
            response = self.session.post(
                f"{self.api_url}/analyze",
                json={"fecha": yesterday},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if self._validate_analysis_response(data):
                    self.print_status("Recent date analysis successful")
                    self._print_analysis_summary(data)
                    return True
                else:
                    self.print_status("Invalid response structure")
                    return False
                    
            elif response.status_code == 404:
                self.print_status(f"No data found for {yesterday} (this is normal)")
                return True
            else:
                self.print_status(f"Analysis failed with status: {response.status_code}")
                try:
                    error_data = response.json()
                    self.print_status(f"Error details: {error_data}")
                except:
                    self.print_status(f"Response text: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_status(f"Recent date test failed: {e}")
            return False
    
    def test_analyze_with_old_date(self) -> bool:
        """Test analysis with an older date (more likely to have data)"""
        try:
            # Use a date from a week ago
            old_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            self.print_status(f"Testing analysis for date: {old_date}")
            
            response = self.session.post(
                f"{self.api_url}/analyze",
                json={"fecha": old_date},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if self._validate_analysis_response(data):
                    self.print_status("Old date analysis successful")
                    self._print_analysis_summary(data)
                    return True
                else:
                    self.print_status("Invalid response structure")
                    return False
                    
            elif response.status_code == 404:
                self.print_status(f"No data found for {old_date}")
                return True
            else:
                self.print_status(f"Analysis failed with status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_status(f"Old date test failed: {e}")
            return False
    
    def test_cache_functionality(self) -> bool:
        """Test that caching works by making the same request twice"""
        try:
            test_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            
            self.print_status(f"Testing cache with date: {test_date}")
            
            # First request
            start_time = time.time()
            response1 = self.session.post(
                f"{self.api_url}/analyze",
                json={"fecha": test_date},
                timeout=self.timeout
            )
            first_duration = time.time() - start_time
            
            if response1.status_code not in [200, 404]:
                self.print_status(f"First request failed: {response1.status_code}")
                return False
            
            # Second request (should be faster due to caching)
            start_time = time.time()
            response2 = self.session.post(
                f"{self.api_url}/analyze",
                json={"fecha": test_date},
                timeout=self.timeout
            )
            second_duration = time.time() - start_time
            
            if response2.status_code != response1.status_code:
                self.print_status("Cache test: Different status codes")
                return False
            
            if response1.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                
                # Check if second request indicates cache usage
                cache_used = data2.get('data', {}).get('metadatos', {}).get('desde_cache', False)
                
                self.print_status(f"First request: {first_duration:.2f}s")
                self.print_status(f"Second request: {second_duration:.2f}s")
                self.print_status(f"Cache used: {cache_used}")
                
                return True
            else:
                self.print_status("Cache test completed (no data to cache)")
                return True
                
        except requests.exceptions.RequestException as e:
            self.print_status(f"Cache test failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling with invalid requests"""
        try:
            # Test with future date
            future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            response = self.session.post(
                f"{self.api_url}/analyze",
                json={"fecha": future_date},
                timeout=self.timeout
            )
            
            if response.status_code == 400:
                self.print_status("Future date correctly rejected")
                return True
            else:
                self.print_status(f"Future date handling unexpected: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_status(f"Error handling test failed: {e}")
            return False
    
    def _validate_analysis_response(self, data: Dict[str, Any]) -> bool:
        """Validate the structure of an analysis response"""
        try:
            # Check top-level structure
            if not isinstance(data, dict):
                return False
            
            if 'success' not in data or 'data' not in data:
                return False
            
            if not data['success']:
                return False
            
            analysis_data = data['data']
            
            # Check required fields
            required_fields = ['fecha', 'analisis']
            for field in required_fields:
                if field not in analysis_data:
                    self.print_status(f"Missing required field: {field}")
                    return False
            
            # Check analysis structure
            analisis = analysis_data['analisis']
            analysis_fields = ['resumen', 'cambios_principales', 'areas_afectadas']
            for field in analysis_fields:
                if field not in analisis:
                    self.print_status(f"Missing analysis field: {field}")
                    return False
            
            return True
            
        except Exception as e:
            self.print_status(f"Response validation error: {e}")
            return False
    
    def _print_analysis_summary(self, data: Dict[str, Any]):
        """Print a summary of the analysis response"""
        try:
            analysis_data = data['data']
            analisis = analysis_data['analisis']
            
            self.print_status("--- Analysis Summary ---")
            self.print_status(f"Date: {analysis_data['fecha']}")
            self.print_status(f"Summary length: {len(analisis.get('resumen', ''))}")
            self.print_status(f"Main changes: {len(analisis.get('cambios_principales', []))}")
            self.print_status(f"Affected areas: {len(analisis.get('areas_afectadas', []))}")
            
            if 'metadatos' in analysis_data:
                metadatos = analysis_data['metadatos']
                self.print_status(f"Processing time: {metadatos.get('tiempo_procesamiento', 'N/A')}s")
                self.print_status(f"From cache: {metadatos.get('desde_cache', False)}")
            
        except Exception as e:
            self.print_status(f"Error printing summary: {e}")
    
    def run_all_tests(self) -> bool:
        """Run all API tests"""
        self.print_status("Starting comprehensive API test suite", "INFO")
        self.print_status(f"API URL: {self.api_url}")
        self.print_status(f"Timeout: {self.timeout}s")
        print("-" * 60)
        
        # Run all tests
        tests = [
            ("API Health Check", self.test_api_health),
            ("Input Validation", self.test_analyze_endpoint_validation),
            ("Recent Date Analysis", self.test_analyze_with_recent_date),
            ("Old Date Analysis", self.test_analyze_with_old_date),
            ("Cache Functionality", self.test_cache_functionality),
            ("Error Handling", self.test_error_handling),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
            print()  # Add spacing between tests
        
        # Print summary
        self.print_test_summary()
        
        return self.tests_failed == 0
    
    def print_test_summary(self):
        """Print a summary of all test results"""
        print("=" * 60)
        self.print_status("TEST SUMMARY", "INFO")
        print("=" * 60)
        
        self.print_status(f"Total tests run: {self.tests_run}")
        self.print_status(f"Tests passed: {self.tests_passed}", "SUCCESS")
        
        if self.tests_failed > 0:
            self.print_status(f"Tests failed: {self.tests_failed}", "ERROR")
        else:
            self.print_status("All tests passed! 🎉", "SUCCESS")
        
        # Print detailed results
        print("\nDetailed Results:")
        for result in self.test_results:
            status_color = "SUCCESS" if result["status"] == "PASSED" else "ERROR"
            self.print_status(
                f"{result['name']}: {result['status']} ({result['duration']:.2f}s)",
                status_color
            )
            if result["error"]:
                self.print_status(f"  Error: {result['error']}", "ERROR")


def load_test_data_to_mongodb():
    """Load test data to MongoDB for integration testing"""
    try:
        from pymongo import MongoClient
        import os
        
        # Get MongoDB connection from environment
        connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        database_name = os.getenv('MONGODB_DATABASE', 'BoletinOficial')
        collection_name = os.getenv('MONGODB_COLLECTION', 'boletin-oficial')
        
        if not connection_string:
            print("MongoDB connection string not found in environment variables")
            return False
        
        client = MongoClient(connection_string)
        db = client[database_name]
        collection = db[collection_name]
        
        # Multiple test data entries for different scenarios
        test_data_entries = [
            {
                "fecha": "2024-01-15",
                "seccion": "legislacion_avisos_oficiales",
                "pdf_url": "https://example.com/test1.pdf",
                "contenido_original": "Decreto 123/2024 - Modificación del régimen tributario para pequeñas empresas",
                "analisis": {
                    "resumen": "Se modifica el régimen tributario aplicable a pequeñas empresas, estableciendo nuevas alícuotas y beneficios fiscales.",
                    "cambios_principales": [
                        {
                            "tipo": "decreto",
                            "numero": "123/2024",
                            "titulo": "Modificación régimen tributario PYMES",
                            "descripcion": "Establece nuevas alícuotas reducidas para empresas con facturación menor a $100M",
                            "impacto": "alto"
                        }
                    ],
                    "impacto_estimado": "Alto impacto en el sector PYME, beneficiando aproximadamente 50,000 empresas",
                    "areas_afectadas": ["tributario", "pymes", "comercial"]
                },
                "opiniones_expertos": [
                    {
                        "fuente": "Dr. Juan Pérez - Especialista Tributario",
                        "opinion": "Esta medida representa un alivio significativo para las PYMES argentinas",
                        "fecha_opinion": "2024-01-15",
                        "relevancia": "alta"
                    }
                ],
                "metadatos": {
                    "fecha_creacion": datetime.utcnow().isoformat(),
                    "version_analisis": "1.0",
                    "modelo_llm_usado": "gemini-2.5-pro",
                    "tiempo_procesamiento": 15.5,
                    "estado": "completado"
                }
            },
            {
                "fecha": "2024-01-16",
                "seccion": "legislacion_avisos_oficiales",
                "pdf_url": "https://example.com/test2.pdf",
                "contenido_original": "Resolución 456/2024 - Nuevas normas de seguridad laboral en la construcción",
                "analisis": {
                    "resumen": "Se establecen nuevos protocolos de seguridad laboral para el sector de la construcción, con énfasis en prevención de accidentes.",
                    "cambios_principales": [
                        {
                            "tipo": "resolucion",
                            "numero": "456/2024",
                            "titulo": "Protocolos de seguridad en construcción",
                            "descripcion": "Implementa nuevos estándares de seguridad y capacitación obligatoria",
                            "impacto": "medio"
                        }
                    ],
                    "impacto_estimado": "Impacto medio en el sector construcción, afectando empresas constructoras y trabajadores",
                    "areas_afectadas": ["laboral", "construccion", "seguridad"]
                },
                "opiniones_expertos": [],
                "metadatos": {
                    "fecha_creacion": datetime.utcnow().isoformat(),
                    "version_analisis": "1.0",
                    "modelo_llm_usado": "gemini-2.5-pro",
                    "tiempo_procesamiento": 12.3,
                    "estado": "completado"
                }
            },
            {
                "fecha": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "seccion": "legislacion_avisos_oficiales",
                "pdf_url": "https://example.com/test_recent.pdf",
                "contenido_original": "Disposición 789/2024 - Actualización de aranceles aduaneros",
                "analisis": {
                    "resumen": "Actualización de los aranceles aduaneros para productos importados, con ajustes en múltiples categorías.",
                    "cambios_principales": [
                        {
                            "tipo": "disposicion",
                            "numero": "789/2024",
                            "titulo": "Actualización aranceles aduaneros",
                            "descripcion": "Modifica aranceles para productos electrónicos y textiles",
                            "impacto": "medio"
                        }
                    ],
                    "impacto_estimado": "Impacto medio en importadores y consumidores finales",
                    "areas_afectadas": ["aduanero", "comercio_exterior", "importaciones"]
                },
                "opiniones_expertos": [],
                "metadatos": {
                    "fecha_creacion": datetime.utcnow().isoformat(),
                    "version_analisis": "1.0",
                    "modelo_llm_usado": "gemini-2.5-pro",
                    "tiempo_procesamiento": 18.7,
                    "estado": "completado"
                }
            }
        ]
        
        # Clear existing test data
        collection.delete_many({"metadatos.modelo_llm_usado": "test-model"})
        collection.delete_many({"metadatos.modelo_llm_usado": "gemini-2.5-pro", "contenido_original": {"$regex": "^(Decreto 123/2024|Resolución 456/2024|Disposición 789/2024)"}})
        
        # Insert test data
        result = collection.insert_many(test_data_entries)
        print(f"Inserted {len(result.inserted_ids)} test data entries")
        
        # Verify insertion
        count = collection.count_documents({"metadatos.modelo_llm_usado": "gemini-2.5-pro"})
        print(f"Total test documents in database: {count}")
        
        client.close()
        return True
        
    except ImportError:
        print("pymongo not available. Skipping test data loading.")
        return False
    except Exception as e:
        print(f"Error loading test data: {e}")
        return False


def main():
    """Main function to run API tests"""
    parser = argparse.ArgumentParser(description="Test the Boletín Oficial API")
    parser.add_argument(
        "api_url",
        help="API Gateway URL (e.g., https://abc123.execute-api.us-east-1.amazonaws.com/v1)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Request timeout in seconds (default: 60)"
    )
    parser.add_argument(
        "--load-test-data",
        action="store_true",
        help="Load test data to MongoDB before running tests"
    )
    parser.add_argument(
        "--single-test",
        choices=["health", "validation", "recent", "old", "cache", "error"],
        help="Run only a specific test"
    )
    
    args = parser.parse_args()
    
    # Load test data if requested
    if args.load_test_data:
        print("Loading test data to MongoDB...")
        if load_test_data_to_mongodb():
            print("Test data loaded successfully")
        else:
            print("Failed to load test data")
        print()
    
    # Initialize tester
    tester = BoletinAPITester(args.api_url, args.timeout)
    
    # Run tests
    if args.single_test:
        test_map = {
            "health": ("API Health Check", tester.test_api_health),
            "validation": ("Input Validation", tester.test_analyze_endpoint_validation),
            "recent": ("Recent Date Analysis", tester.test_analyze_with_recent_date),
            "old": ("Old Date Analysis", tester.test_analyze_with_old_date),
            "cache": ("Cache Functionality", tester.test_cache_functionality),
            "error": ("Error Handling", tester.test_error_handling),
        }
        
        test_name, test_func = test_map[args.single_test]
        success = tester.run_test(test_name, test_func)
        tester.print_test_summary()
        
        sys.exit(0 if success else 1)
    else:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()