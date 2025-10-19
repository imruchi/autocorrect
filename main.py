#!/usr/bin/env python3
"""
Real-time Writing Assistant with Gemini API

A system-wide writing assistant that helps improve text in real-time.
Works across all applications on macOS.

Usage:
    1. Select text in any application
    2. Press configured hotkey (e.g., Cmd+Shift+G for grammar fix)
    3. Text will be automatically improved and replaced

Author: Writing Assistant
License: MIT
"""

import os
import sys
import logging
import signal
import threading
from pathlib import Path

from config_manager import ConfigManager
from gemini_client import GeminiClient
from text_handler import TextHandler
from hotkey_manager import HotkeyManager


class WritingAssistant:
    """Main application class for the writing assistant."""

    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize writing assistant.

        Args:
            config_path: Path to configuration file
        """
        self.config_manager = ConfigManager(config_path)
        self.logger = None
        self.gemini_client = None
        self.text_handler = None
        self.hotkey_manager = None
        self.is_running = False
        self.processing_lock = threading.Lock()

    def setup_logging(self):
        """Configure logging."""
        log_level = getattr(logging, self.config_manager.get_log_level(), logging.INFO)
        log_file = self.config_manager.get_log_file()

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 60)
        self.logger.info("Writing Assistant Starting")
        self.logger.info("=" * 60)

    def initialize(self):
        """Initialize all components."""
        try:
            # Load configuration
            self.logger.info("Loading configuration...")
            self.config_manager.load()

            # Initialize Gemini client
            self.logger.info("Initializing Gemini client...")
            gemini_config = self.config_manager.get_gemini_config()
            self.gemini_client = GeminiClient(
                api_key=gemini_config['api_key'],
                model=gemini_config['model'],
                requests_per_minute=self.config_manager.get_rate_limit(),
                max_retries=gemini_config['max_retries'],
                timeout=gemini_config['timeout']
            )

            # Initialize text handler
            self.logger.info("Initializing text handler...")
            self.text_handler = TextHandler()

            # Initialize hotkey manager
            self.logger.info("Initializing hotkey manager...")
            self.hotkey_manager = HotkeyManager()

            # Register hotkeys
            hotkeys = self.config_manager.get_hotkeys()
            self.hotkey_manager.register_multiple_hotkeys(hotkeys, self.handle_hotkey)

            self.logger.info("Initialization complete")
            return True

        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            print(f"\n❌ Error: {str(e)}\n")
            return False

    def handle_hotkey(self, mode: str):
        """
        Handle hotkey press.

        Args:
            mode: Improvement mode (grammar_fix, formal, etc.)
        """
        # Prevent concurrent processing
        if not self.processing_lock.acquire(blocking=False):
            self.logger.warning("Already processing a request, ignoring hotkey")
            return

        try:
            self.logger.info(f"Hotkey triggered: {mode}")

            # Show processing notification
            if self.config_manager.should_show_notifications():
                self.text_handler.show_notification(
                    "Writing Assistant",
                    f"Processing ({mode})...",
                    duration=1
                )

            # Get selected text
            selected_text = self.text_handler.get_selected_text()
            if not selected_text:
                if self.config_manager.should_show_notifications():
                    self.text_handler.show_notification(
                        "Writing Assistant",
                        "No text selected",
                        duration=2
                    )
                return

            self.logger.info(f"Processing {len(selected_text)} characters")

            # Improve text using Gemini
            improved_text = self.gemini_client.improve_text(selected_text, mode)

            if improved_text:
                # Replace text
                success = self.text_handler.replace_selected_text(improved_text)

                if success:
                    self.logger.info("Text replaced successfully")
                    if self.config_manager.should_show_notifications():
                        self.text_handler.show_notification(
                            "Writing Assistant",
                            f"Text improved ({mode})",
                            duration=self.config_manager.get_notification_duration()
                        )
                else:
                    self.logger.error("Failed to replace text")
                    if self.config_manager.should_show_notifications():
                        self.text_handler.show_notification(
                            "Writing Assistant",
                            "Failed to replace text",
                            duration=2
                        )
            else:
                self.logger.error("Failed to improve text")
                if self.config_manager.should_show_notifications():
                    self.text_handler.show_notification(
                        "Writing Assistant",
                        "Failed to improve text",
                        duration=2
                    )

        except Exception as e:
            self.logger.error(f"Error handling hotkey: {str(e)}")
            if self.config_manager.should_show_notifications():
                self.text_handler.show_notification(
                    "Writing Assistant",
                    "An error occurred",
                    duration=2
                )

        finally:
            self.processing_lock.release()

    def start(self):
        """Start the writing assistant."""
        if self.is_running:
            self.logger.warning("Already running")
            return

        try:
            self.logger.info("Starting hotkey listener...")
            self.hotkey_manager.start()
            self.is_running = True

            # Print status
            print("\n✅ Writing Assistant is running!")
            print("\n📝 Available hotkeys:")
            for hotkey, mode in self.hotkey_manager.get_registered_hotkeys().items():
                description = self.gemini_client.get_available_modes().get(mode, mode)
                print(f"  {hotkey:20} - {description}")

            print("\n💡 Tips:")
            print("  1. Select text in any application")
            print("  2. Press a hotkey to improve the text")
            print("  3. Text will be automatically replaced")
            print("\n⌨️  Press Ctrl+C to stop\n")

            # Show startup notification
            if self.config_manager.should_show_notifications():
                self.text_handler.show_notification(
                    "Writing Assistant",
                    "Ready to help!",
                    duration=2
                )

            # Keep running
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.pause()

        except Exception as e:
            self.logger.error(f"Error starting assistant: {str(e)}")
            self.stop()
            raise

    def stop(self):
        """Stop the writing assistant."""
        if not self.is_running:
            return

        self.logger.info("Stopping writing assistant...")
        print("\n👋 Stopping writing assistant...")

        try:
            if self.hotkey_manager:
                self.hotkey_manager.stop()

            self.is_running = False
            self.logger.info("Writing assistant stopped")
            print("✅ Stopped successfully\n")

        except Exception as e:
            self.logger.error(f"Error stopping assistant: {str(e)}")

    def _signal_handler(self, signum, frame):
        """Handle interrupt signal."""
        self.stop()
        sys.exit(0)


def main():
    """Main entry point."""
    print("=" * 60)
    print("Writing Assistant with Gemini API")
    print("=" * 60)

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Create assistant
    assistant = WritingAssistant()

    # Setup logging
    assistant.setup_logging()

    # Initialize
    if not assistant.initialize():
        sys.exit(1)

    # Start
    try:
        assistant.start()
    except KeyboardInterrupt:
        assistant.stop()
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
