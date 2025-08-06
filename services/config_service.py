"""
Configuration service for the Boletin Oficial application.
Handles environment variables and configuration validation.
"""

import os
from typing import Dict, Any, Optional
from utils.error_handler import error_handler, ErrorCode


class ConfigService:
    """Service for managing application configuration."""
    
    # Required configuration keys
    REQUIRED_CONFIG = {
        'GEMINI_API_KEY': 'Google Gemini API key for LLM service',
        'MONGODB_CONNECTION_STRING': 'MongoDB Atlas connection string',
        'MONGODB_DATABASE': 'MongoDB database name',
        'MONGODB_COLLECTION': 'MongoDB collection name'
    }
    
    # Optional configuration with defaults
    OPTIONAL_CONFIG = {
        'LANGCHAIN_MODEL': 'gemini-2.5-flash',
        'LANGCHAIN_TEMPERATURE': '1',
        'MAX_RETRY_ATTEMPTS': '3',
        'LLM_REQUEST_TIMEOUT': '120',
        'LOG_LEVEL': 'INFO'
    }
    
    def __init__(self):
        """Initialize the configuration service."""
        self._config = {}
        self._validated = False
        
    def load_config(self) -> Dict[str, Any]:
        """
        Load and validate configuration from environment variables.
        
        Returns:
            dict: Configuration dictionary
            
        Raises:
            Exception: If required configuration is missing or invalid
        """
        try:
            # Load required configuration
            for key, description in self.REQUIRED_CONFIG.items():
                value = os.getenv(key)
                if not value:
                    raise ValueError(f"Missing required configuration: {key} ({description})")
                self._config[key] = value
            
            # Load optional configuration with defaults
            for key, default_value in self.OPTIONAL_CONFIG.items():
                self._config[key] = os.getenv(key, default_value)
            
            # Validate configuration
            self._validate_config()
            self._validated = True
            
            # Log success without using error_handler to avoid recursion
            print(f"Configuration loaded successfully: {len(self.REQUIRED_CONFIG)} required, {len(self.OPTIONAL_CONFIG)} optional keys")
            
            return self._config.copy()
            
        except Exception as e:
            # Avoid recursion by logging directly instead of using error_handler
            print(f"Configuration error: {str(e)}")
            raise
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not self._validated:
            try:
                self.load_config()
            except RecursionError:
                print(f"Recursion detected in config loading, returning default for {key}")
                return default
        
        return self._config.get(key, default)
    
    def get_int(self, key: str, default: Optional[int] = None) -> int:
        """
        Get a configuration value as integer.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value as integer
            
        Raises:
            ValueError: If value cannot be converted to integer
        """
        value = self.get(key, default)
        if value is None:
            raise ValueError(f"Configuration key '{key}' not found and no default provided")
        
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Configuration key '{key}' cannot be converted to integer: {value}") from e
    
    def get_float(self, key: str, default: Optional[float] = None) -> float:
        """
        Get a configuration value as float.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value as float
            
        Raises:
            ValueError: If value cannot be converted to float
        """
        value = self.get(key, default)
        if value is None:
            raise ValueError(f"Configuration key '{key}' not found and no default provided")
        
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Configuration key '{key}' cannot be converted to float: {value}") from e
    
    def get_bool(self, key: str, default: Optional[bool] = None) -> bool:
        """
        Get a configuration value as boolean.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value as boolean
        """
        value = self.get(key, default)
        if value is None:
            raise ValueError(f"Configuration key '{key}' not found and no default provided")
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        
        return bool(value)
    
    def is_valid(self) -> bool:
        """
        Check if configuration is valid.
        
        Returns:
            bool: True if configuration is valid
        """
        return self._validated
    
    def get_mongodb_config(self) -> Dict[str, str]:
        """
        Get MongoDB-specific configuration.
        
        Returns:
            dict: MongoDB configuration
        """
        return {
            'connection_string': self.get('MONGODB_CONNECTION_STRING'),
            'database': self.get('MONGODB_DATABASE'),
            'collection': self.get('MONGODB_COLLECTION')
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """
        Get LLM-specific configuration.
        
        Returns:
            dict: LLM configuration
        """
        return {
            'api_key': self.get('GEMINI_API_KEY'),
            'model': self.get('LANGCHAIN_MODEL'),
            'temperature': self.get_float('LANGCHAIN_TEMPERATURE'),
            'timeout': self.get_int('LLM_REQUEST_TIMEOUT')
        }
    
    def get_retry_config(self) -> Dict[str, int]:
        """
        Get retry-specific configuration.
        
        Returns:
            dict: Retry configuration
        """
        return {
            'max_attempts': self.get_int('MAX_RETRY_ATTEMPTS'),
            'pdf_timeout': self.get_int('PDF_DOWNLOAD_TIMEOUT')
        }
    
    def _validate_config(self):
        """
        Validate the loaded configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate MongoDB connection string format
        mongodb_conn = self._config.get('MONGODB_CONNECTION_STRING', '')
        if not mongodb_conn.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError("MONGODB_CONNECTION_STRING must start with 'mongodb://' or 'mongodb+srv://'")
        
        # Validate numeric values directly from _config to avoid recursion
        try:
            max_retries = int(self._config.get('MAX_RETRY_ATTEMPTS', '3'))
            pdf_timeout = int(self._config.get('PDF_DOWNLOAD_TIMEOUT', '30'))
            llm_timeout = int(self._config.get('LLM_REQUEST_TIMEOUT', '60'))
            temperature = float(self._config.get('LANGCHAIN_TEMPERATURE', '1'))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid numeric configuration: {e}") from e
        
        # Validate temperature range
        if not 0 <= temperature <= 2:
            raise ValueError("LANGCHAIN_TEMPERATURE must be between 0 and 2")
        
        # Validate retry attempts
        if max_retries < 1 or max_retries > 10:
            raise ValueError("MAX_RETRY_ATTEMPTS must be between 1 and 10")
        
        # Validate timeouts
              
        if llm_timeout < 10 or llm_timeout > 600:
            raise ValueError("LLM_REQUEST_TIMEOUT must be between 10 and 600 seconds")
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        Get all configuration (excluding sensitive values).
        
        Returns:
            dict: All configuration with sensitive values masked
        """
        if not self._validated:
            self.load_config()
        
        config_copy = self._config.copy()
        
        # Mask sensitive values
        sensitive_keys = ['GEMINI_API_KEY', 'MONGODB_CONNECTION_STRING']
        for key in sensitive_keys:
            if key in config_copy:
                config_copy[key] = '***MASKED***'
        
        return config_copy


# Global configuration service instance
config_service = ConfigService()