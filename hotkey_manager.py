"""
Global hotkey management for macOS.
Listens for keyboard shortcuts and triggers actions.
"""

import logging
import threading
from typing import Callable, Dict
from pynput import keyboard


class HotkeyManager:
    """Manages global hotkeys for the writing assistant."""

    # Mapping of config keys to pynput keys
    KEY_MAPPING = {
        'cmd': keyboard.Key.cmd,
        'ctrl': keyboard.Key.ctrl,
        'alt': keyboard.Key.alt,
        'option': keyboard.Key.alt,
        'shift': keyboard.Key.shift,
    }

    def __init__(self):
        """Initialize hotkey manager."""
        self.logger = logging.getLogger(__name__)
        self.hotkeys = {}
        self.listener = None
        self.is_running = False

    def register_hotkey(self, hotkey_str: str, callback: Callable, mode: str):
        """
        Register a hotkey combination.

        Args:
            hotkey_str: Hotkey string (e.g., "cmd+shift+g")
            callback: Function to call when hotkey is pressed
            mode: Mode name for the callback
        """
        try:
            # Parse hotkey string
            parts = hotkey_str.lower().replace(' ', '').split('+')
            modifiers = set()
            key = None

            for part in parts:
                if part in self.KEY_MAPPING:
                    modifiers.add(self.KEY_MAPPING[part])
                else:
                    # Regular key
                    key = keyboard.KeyCode.from_char(part)

            if key is None:
                self.logger.error(f"No key specified in hotkey: {hotkey_str}")
                return

            # Create hotkey combination
            hotkey = keyboard.HotKey(
                keyboard.HotKey.parse(hotkey_str.replace('cmd', '<cmd>').replace('option', '<alt>')),
                lambda m=mode: callback(m)
            )

            self.hotkeys[hotkey_str] = {
                'hotkey': hotkey,
                'callback': callback,
                'mode': mode
            }

            self.logger.info(f"Registered hotkey: {hotkey_str} -> {mode}")

        except Exception as e:
            self.logger.error(f"Failed to register hotkey {hotkey_str}: {str(e)}")

    def start(self):
        """Start listening for hotkeys."""
        if self.is_running:
            self.logger.warning("Hotkey manager already running")
            return

        try:
            # Create listener
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )

            self.listener.start()
            self.is_running = True
            self.logger.info("Hotkey manager started")

        except Exception as e:
            self.logger.error(f"Failed to start hotkey manager: {str(e)}")
            raise

    def stop(self):
        """Stop listening for hotkeys."""
        if not self.is_running:
            return

        try:
            if self.listener:
                self.listener.stop()
                self.listener = None

            self.is_running = False
            self.logger.info("Hotkey manager stopped")

        except Exception as e:
            self.logger.error(f"Failed to stop hotkey manager: {str(e)}")

    def _on_press(self, key):
        """Handle key press events."""
        try:
            for hotkey_data in self.hotkeys.values():
                hotkey_data['hotkey'].press(self.listener.canonical(key))
        except Exception as e:
            self.logger.error(f"Error in key press handler: {str(e)}")

    def _on_release(self, key):
        """Handle key release events."""
        try:
            for hotkey_data in self.hotkeys.values():
                hotkey_data['hotkey'].release(self.listener.canonical(key))
        except Exception as e:
            self.logger.error(f"Error in key release handler: {str(e)}")

    def register_multiple_hotkeys(self, hotkey_config: Dict[str, str], callback: Callable):
        """
        Register multiple hotkeys from configuration.

        Args:
            hotkey_config: Dictionary of mode -> hotkey string
            callback: Callback function that receives mode as argument
        """
        for mode, hotkey_str in hotkey_config.items():
            self.register_hotkey(hotkey_str, callback, mode)

    def get_registered_hotkeys(self) -> Dict[str, str]:
        """
        Get all registered hotkeys.

        Returns:
            Dictionary of hotkey string -> mode
        """
        return {
            hotkey_str: data['mode']
            for hotkey_str, data in self.hotkeys.items()
        }
