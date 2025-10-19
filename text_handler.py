"""
Text capture and replacement for macOS.
Uses AppleScript and clipboard to capture and replace selected text.
"""

import time
import logging
import subprocess
from typing import Optional
import Cocoa


class TextHandler:
    """Handles text capture and replacement on macOS."""

    def __init__(self):
        """Initialize text handler."""
        self.logger = logging.getLogger(__name__)
        self.clipboard_delay = 0.1  # Delay for clipboard operations

    def get_selected_text(self) -> Optional[str]:
        """
        Capture currently selected text using clipboard.

        Returns:
            Selected text or None if failed
        """
        try:
            # Save current clipboard
            pasteboard = Cocoa.NSPasteboard.generalPasteboard()
            old_clipboard = pasteboard.stringForType_(Cocoa.NSPasteboardTypeString)

            # Copy selected text (Cmd+C)
            self._execute_applescript('''
                tell application "System Events"
                    keystroke "c" using command down
                end tell
            ''')

            # Wait for clipboard to update
            time.sleep(self.clipboard_delay)

            # Get new clipboard content
            new_clipboard = pasteboard.stringForType_(Cocoa.NSPasteboardTypeString)

            # Restore old clipboard
            if old_clipboard:
                pasteboard.clearContents()
                pasteboard.setString_forType_(old_clipboard, Cocoa.NSPasteboardTypeString)

            if new_clipboard and new_clipboard.strip():
                self.logger.info(f"Captured {len(new_clipboard)} characters")
                return new_clipboard
            else:
                self.logger.warning("No text selected")
                return None

        except Exception as e:
            self.logger.error(f"Failed to get selected text: {str(e)}")
            return None

    def replace_selected_text(self, new_text: str) -> bool:
        """
        Replace selected text with new text using clipboard.

        Args:
            new_text: Text to insert

        Returns:
            True if successful, False otherwise
        """
        try:
            if not new_text:
                self.logger.warning("No text to replace with")
                return False

            # Save current clipboard
            pasteboard = Cocoa.NSPasteboard.generalPasteboard()
            old_clipboard = pasteboard.stringForType_(Cocoa.NSPasteboardTypeString)

            # Set new text to clipboard
            pasteboard.clearContents()
            pasteboard.setString_forType_(new_text, Cocoa.NSPasteboardTypeString)

            time.sleep(self.clipboard_delay)

            # Paste (Cmd+V)
            self._execute_applescript('''
                tell application "System Events"
                    keystroke "v" using command down
                end tell
            ''')

            time.sleep(self.clipboard_delay)

            # Restore old clipboard
            if old_clipboard:
                pasteboard.clearContents()
                pasteboard.setString_forType_(old_clipboard, Cocoa.NSPasteboardTypeString)

            self.logger.info(f"Replaced with {len(new_text)} characters")
            return True

        except Exception as e:
            self.logger.error(f"Failed to replace text: {str(e)}")
            return False

    def _execute_applescript(self, script: str) -> Optional[str]:
        """
        Execute AppleScript.

        Args:
            script: AppleScript code

        Returns:
            Script output or None if failed
        """
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                self.logger.error(f"AppleScript error: {result.stderr}")
                return None

        except Exception as e:
            self.logger.error(f"Failed to execute AppleScript: {str(e)}")
            return None

    def show_notification(self, title: str, message: str, duration: int = 2):
        """
        Show macOS notification.

        Args:
            title: Notification title
            message: Notification message
            duration: Display duration in seconds
        """
        try:
            script = f'''
                display notification "{message}" with title "{title}" sound name "Glass"
            '''
            self._execute_applescript(script)
            self.logger.debug(f"Showed notification: {title}")

        except Exception as e:
            self.logger.error(f"Failed to show notification: {str(e)}")

    def get_active_application(self) -> Optional[str]:
        """
        Get name of currently active application.

        Returns:
            Application name or None
        """
        try:
            script = '''
                tell application "System Events"
                    return name of first application process whose frontmost is true
                end tell
            '''
            app_name = self._execute_applescript(script)
            return app_name

        except Exception as e:
            self.logger.error(f"Failed to get active application: {str(e)}")
            return None
