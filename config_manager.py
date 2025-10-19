"""
Configuration management for the writing assistant.
Loads and validates configuration from YAML file.
"""

import os
import logging
import yaml
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages application configuration."""

    DEFAULT_CONFIG = {
        'gemini': {
            'api_key': '',
            'model': 'gemini-2.0-flash-exp',
            'max_retries': 3,
            'timeout': 10
        },
        'hotkeys': {
            'grammar_fix': 'cmd+shift+g',
            'formal': 'cmd+shift+f',
            'casual': 'cmd+shift+c',
            'simplify': 'cmd+shift+s',
            'expand': 'cmd+shift+e'
        },
        'rate_limit': {
            'requests_per_minute': 50
        },
        'ui': {
            'show_notifications': True,
            'notification_duration': 2
        },
        'logging': {
            'level': 'INFO',
            'file': 'writing_assistant.log'
        }
    }

    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = {}
        self.logger = logging.getLogger(__name__)

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If configuration is invalid
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config.yaml and add your Gemini API key."
            )

        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)

            # Merge with defaults
            self.config = self._merge_with_defaults(self.config, self.DEFAULT_CONFIG)

            # Validate
            self._validate()

            self.logger.info("Configuration loaded successfully")
            return self.config

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {str(e)}")

    def _merge_with_defaults(self, config: Dict, defaults: Dict) -> Dict:
        """Merge configuration with defaults."""
        result = defaults.copy()

        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_with_defaults(value, result[key])
            else:
                result[key] = value

        return result

    def _validate(self):
        """Validate configuration."""
        # Check API key
        api_key = self.config.get('gemini', {}).get('api_key', '')
        if not api_key or api_key == 'YOUR_GEMINI_API_KEY_HERE':
            raise ValueError(
                "Gemini API key not configured.\n"
                "Please add your API key to config.yaml.\n"
                "Get your key from: https://aistudio.google.com/app/apikey"
            )

        # Validate rate limit
        rpm = self.config.get('rate_limit', {}).get('requests_per_minute', 0)
        if rpm <= 0 or rpm > 60:
            raise ValueError("requests_per_minute must be between 1 and 60")

    def get(self, *keys, default=None) -> Any:
        """
        Get configuration value by nested keys.

        Args:
            *keys: Nested keys to traverse
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def get_gemini_config(self) -> Dict[str, Any]:
        """Get Gemini API configuration."""
        return self.config.get('gemini', {})

    def get_hotkeys(self) -> Dict[str, str]:
        """Get hotkey configuration."""
        return self.config.get('hotkeys', {})

    def get_rate_limit(self) -> int:
        """Get rate limit configuration."""
        return self.config.get('rate_limit', {}).get('requests_per_minute', 50)

    def should_show_notifications(self) -> bool:
        """Check if notifications should be shown."""
        return self.config.get('ui', {}).get('show_notifications', True)

    def get_notification_duration(self) -> int:
        """Get notification duration."""
        return self.config.get('ui', {}).get('notification_duration', 2)

    def get_log_level(self) -> str:
        """Get logging level."""
        return self.config.get('logging', {}).get('level', 'INFO')

    def get_log_file(self) -> str:
        """Get log file path."""
        return self.config.get('logging', {}).get('file', 'writing_assistant.log')
