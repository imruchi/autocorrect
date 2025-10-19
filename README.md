# Writing Assistant with Gemini API

A system-wide real-time writing assistant for macOS that uses Google's Gemini API to improve your text across all applications.

## Features

✨ **System-wide availability** - Works in any text field (email, Slack, browser, Word, etc.)
⌨️ **Multiple correction modes** - Grammar, formal, casual, simplify, expand
🚀 **Low latency** - Fast responses using Gemini 2.0 Flash
🔐 **Secure** - API key stored locally in config file
💰 **Free to run** - Uses Gemini free tier (60 requests/min)
🎯 **Simple setup** - Easy installation and configuration

## Quick Start

### 1. Prerequisites

- macOS (tested on macOS 15.5)
- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/imruchi/autocorrect.git
cd autocorrect

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

1. Open `config.yaml` in a text editor
2. Replace `YOUR_GEMINI_API_KEY_HERE` with your actual API key:

```yaml
gemini:
  api_key: "your_actual_api_key_here"
```

3. (Optional) Customize hotkeys and other settings

### 4. Grant Permissions

The app needs two macOS permissions:

**Accessibility Access:**
1. Run the app once: `python main.py`
2. macOS will prompt for Accessibility access
3. Go to **System Settings → Privacy & Security → Accessibility**
4. Enable access for Terminal (or your Python IDE)

**Input Monitoring** (may also be required):
1. Go to **System Settings → Privacy & Security → Input Monitoring**
2. Enable access for Terminal (or your Python IDE)

### 5. Run

```bash
python main.py
```

You should see:
```
✅ Writing Assistant is running!

📝 Available hotkeys:
  cmd+shift+g          - Fix grammar, spelling, and punctuation
  cmd+shift+f          - Make more formal and professional
  cmd+shift+c          - Make more casual and friendly
  cmd+shift+s          - Simplify and clarify
  cmd+shift+e          - Expand with more detail
```

## Usage

1. **Select text** in any application (email, Slack, Notes, etc.)
2. **Press a hotkey** (e.g., `Cmd+Shift+G` for grammar correction)
3. **Wait briefly** - You'll see a notification while processing
4. **Text is replaced** automatically with the improved version

### Example

**Before** (select this text and press `Cmd+Shift+G`):
```
hey can u send me teh report by tommorow
```

**After**:
```
Hey, could you send me the report by tomorrow?
```

## Configuration

Edit `config.yaml` to customize:

### Hotkeys

```yaml
hotkeys:
  grammar_fix: "cmd+shift+g"  # Change to your preferred combination
  formal: "cmd+shift+f"
  casual: "cmd+shift+c"
  simplify: "cmd+shift+s"
  expand: "cmd+shift+e"
```

### Rate Limiting

```yaml
rate_limit:
  requests_per_minute: 50  # Max 60 for free tier
```

### Notifications

```yaml
ui:
  show_notifications: true
  notification_duration: 2  # seconds
```

### Logging

```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "writing_assistant.log"
```

## Architecture

```
┌─────────────────────┐
│   main.py          │  Main application & coordination
└──────────┬──────────┘
           │
           ├──► config_manager.py    (Configuration loading)
           │
           ├──► hotkey_manager.py    (Global hotkey detection)
           │
           ├──► text_handler.py      (Clipboard & text operations)
           │
           └──► gemini_client.py     (API integration & prompts)
```

### Key Components

- **`main.py`** - Application entry point, orchestrates all components
- **`config_manager.py`** - Loads and validates YAML configuration
- **`gemini_client.py`** - Handles Gemini API calls with rate limiting
- **`text_handler.py`** - Captures and replaces text using clipboard
- **`hotkey_manager.py`** - Listens for global keyboard shortcuts

## Troubleshooting

### "No text selected" notification

- Make sure text is actually selected (highlighted) before pressing hotkey
- Try selecting text again and ensure it's still selected when you press the hotkey

### Hotkeys not working

- Check that you've granted Accessibility permissions
- Verify no other app is using the same hotkey combination
- Check `writing_assistant.log` for error messages

### API errors

- Verify your API key is correct in `config.yaml`
- Check your internet connection
- Ensure you haven't exceeded rate limits (60 requests/min for free tier)
- Check [Gemini API status](https://status.cloud.google.com/)

### Text not being replaced

- Some apps (like secure password fields) block programmatic text input
- Try the same operation in a different app (like Notes or TextEdit)
- Check Accessibility permissions are granted

### Permission denied errors

```bash
# If you see permission errors, run with elevated privileges
sudo python main.py
```

## Running on Startup

### Option 1: LaunchAgent (Recommended)

Create `~/Library/LaunchAgents/com.writingassistant.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.writingassistant</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/autocorrect/main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.writingassistant.plist
```

### Option 2: Login Items

1. Open **System Settings → General → Login Items**
2. Click **+** under "Open at Login"
3. Navigate to and select your Python script or create a shell script wrapper

## API Costs

The Gemini API free tier includes:
- **60 requests per minute**
- **1,500 requests per day**
- **1 million tokens per month**

At typical usage (10-20 corrections per hour), you should stay well within free limits.

## Security

- API key is stored locally in `config.yaml` (never committed to git)
- No data is sent anywhere except Google's Gemini API
- All processing happens locally except API calls
- Clipboard is restored after each operation

## Limitations

- **macOS only** (uses AppleScript and Cocoa frameworks)
- **Requires permissions** (Accessibility, Input Monitoring)
- **Some apps may block** programmatic text input (e.g., password fields)
- **Rate limited** to Gemini API free tier limits

## Future Enhancements (Phase 2 & 3)

- [ ] Context-aware suggestions based on active application
- [ ] Custom prompt templates
- [ ] Local text history (optional)
- [ ] Learning from user corrections
- [ ] Menu bar icon with quick settings
- [ ] Sentence-level suggestions as you type
- [ ] Multiple language support

## Contributing

Feel free to submit issues, feature requests, or pull requests!

## License

MIT License - feel free to use and modify as needed.

## Support

If you encounter issues:
1. Check `writing_assistant.log` for error details
2. Verify all permissions are granted
3. Test with a simple app like TextEdit first
4. Ensure your API key is valid

## Acknowledgments

- Built with [Google Gemini API](https://ai.google.dev/)
- Uses [pynput](https://github.com/moses-palmer/pynput) for hotkey detection
- Uses [PyObjC](https://github.com/ronaldoussoren/pyobjc) for macOS integration
