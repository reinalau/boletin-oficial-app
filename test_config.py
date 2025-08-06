#!/usr/bin/env python3
"""
Test script to verify configuration is working correctly
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("🧪 Testing Configuration")
print("=" * 50)

# Test environment variables
print("\n📋 Environment Variables:")
print(f"GEMINI_API_KEY: {'✅ Set' if os.getenv('GEMINI_API_KEY') else '❌ Missing'}")
print(f"MONGODB_CONNECTION_STRING: {'✅ Set' if os.getenv('MONGODB_CONNECTION_STRING') else '❌ Missing'}")
print(f"MONGODB_DATABASE: {os.getenv('MONGODB_DATABASE', '❌ Missing')}")
print(f"MONGODB_COLLECTION: {os.getenv('MONGODB_COLLECTION', '❌ Missing')}")

# Test config service
print("\n🔧 Testing Config Service:")
try:
    from services.config_service import config_service
    
    # Load configuration
    config = config_service.load_config()
    print("✅ Config service loaded successfully")
    
    # Test LLM config
    llm_config = config_service.get_llm_config()
    print(f"✅ LLM API Key: {'Set' if llm_config['api_key'] else 'Missing'}")
    print(f"✅ LLM Model: {llm_config['model']}")
    print(f"✅ LLM Temperature: {llm_config['temperature']}")
    
    # Test MongoDB config
    mongo_config = config_service.get_mongodb_config()
    print(f"✅ MongoDB Database: {mongo_config['database']}")
    print(f"✅ MongoDB Collection: {mongo_config['collection']}")
    
except Exception as e:
    print(f"❌ Config service error: {e}")

# Test LLM service initialization
print("\n🤖 Testing LLM Service:")
try:
    from services.llm_service_direct import LLMAnalysisServiceDirect
    
    llm_service = LLMAnalysisServiceDirect()
    print("✅ LLM service initialized successfully")
    
except Exception as e:
    print(f"❌ LLM service error: {e}")

print("\n🎉 Configuration test completed!")