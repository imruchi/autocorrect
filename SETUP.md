# Setup Guide - Writing Assistant

Complete step-by-step setup instructions for the Writing Assistant.

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] macOS computer (10.14 or later)
- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] pip installed (`pip3 --version`)
- [ ] Internet connection
- [ ] Google account (for API key)

## Step-by-Step Setup

### Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"** or **"Get API Key"**
4. Choose **"Create API key in new project"** (or select existing project)
5. Copy the API key (starts with `AIzaSy...`)
6. **Important:** Keep this key private and never share it

### Step 2: Install Dependencies

```bash
# Navigate to project directory
cd /Users/ruchibommaraju/Northwestern/thoughts/autocomplete

# Install required Python packages
pip3 install -r requirements.txt
```

Expected output:
```
Successfully installed google-generativeai-0.3.x pynput-1.7.x pyobjc-framework-Cocoa-9.x ...
```

**Troubleshooting:**
- If `pip3` is not found, try `pip` instead
- If you get permission errors, try: `pip3 install --user -r requirements.txt`

### Step 3: Configure the Application

1. **Open config.yaml** in your favorite text editor:
   ```bash
   open -a TextEdit config.yaml
   # Or use nano/vim/vscode
   ```

2. **Add your API key:**
   ```yaml
   gemini:
     api_key: "AIzaSy..."  # Paste your actual API key here
   ```

3. **Save the file**

4. **(Optional) Customize hotkeys** if you want different shortcuts:
   ```yaml
   hotkeys:
     grammar_fix: "cmd+shift+g"  # Change to your preference
     formal: "cmd+shift+f"
     # ... etc
   ```

### Step 4: Grant macOS Permissions

The app needs special permissions to work system-wide.

#### Run the app first time:

```bash
python3 main.py
```

You'll likely see an error about permissions. That's normal!

#### Grant Accessibility Access:

1. macOS will show a security dialog, or you'll see an error message
2. Open **System Settings** (or System Preferences)
3. Go to **Privacy & Security**
4. Click **Accessibility** in the sidebar
5. Click the **lock icon** (🔒) to make changes (enter your password)
6. Look for **Terminal** (or **Python**, **iTerm2**, **VS Code**, etc. depending on how you're running it)
7. **Toggle it ON** (check the checkbox)
8. Close System Settings

#### Grant Input Monitoring (if needed):

1. Still in **System Settings → Privacy & Security**
2. Click **Input Monitoring** in the sidebar
3. Enable access for **Terminal** (or your Python environment)

### Step 5: Test the Installation

1. **Start the assistant:**
   ```bash
   python3 main.py
   ```

2. **You should see:**
   ```
   ✅ Writing Assistant is running!

   📝 Available hotkeys:
     cmd+shift+g          - Fix grammar, spelling, and punctuation
     ...
   ```

3. **Test it:**
   - Open TextEdit or Notes
   - Type: `this is a test with bad grammer`
   - Select all the text (Cmd+A)
   - Press **Cmd+Shift+G**
   - Wait 1-2 seconds
   - Text should change to: `This is a test with bad grammar.`

4. **If it works:** 🎉 You're all set!

5. **Stop the app:** Press `Ctrl+C` in the terminal

## Verification Steps

### Test Each Component

1. **API Connection:**
   ```bash
   python3 -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('✅ API key works')"
   ```

2. **Dependencies:**
   ```bash
   python3 -c "import pynput, yaml, Cocoa; print('✅ All packages installed')"
   ```

3. **Configuration:**
   ```bash
   python3 -c "from config_manager import ConfigManager; c = ConfigManager(); c.load(); print('✅ Config valid')"
   ```

## Common Issues & Solutions

### Issue: "Configuration file not found"

**Solution:** Make sure you're in the correct directory:
```bash
pwd  # Should show: /Users/ruchibommaraju/Northwestern/thoughts/autocomplete
ls config.yaml  # Should exist
```

### Issue: "Gemini API key not configured"

**Solution:**
- Open `config.yaml`
- Replace `YOUR_GEMINI_API_KEY_HERE` with your actual key
- Save the file

### Issue: "ModuleNotFoundError: No module named 'google.generativeai'"

**Solution:**
```bash
pip3 install google-generativeai
```

### Issue: "Permission denied" or hotkeys don't work

**Solution:**
1. Quit the app (Ctrl+C)
2. Grant Accessibility permissions (see Step 4)
3. Restart Terminal
4. Run `python3 main.py` again

### Issue: "Text not being replaced"

**Possible causes:**
1. Text wasn't selected when you pressed the hotkey
2. Some apps block programmatic text input (try TextEdit first)
3. Accessibility permissions not granted
4. API request failed (check `writing_assistant.log`)

**Debug:**
```bash
# Check the log file
tail -f writing_assistant.log
```

### Issue: API errors or timeouts

**Solution:**
1. Check internet connection
2. Verify API key is correct
3. Check [API status](https://status.cloud.google.com/)
4. Ensure you haven't exceeded rate limits

## Testing Different Modes

Try each mode to verify everything works:

### Grammar Fix (Cmd+Shift+G)
- Input: `i went too the store yesterday`
- Expected: `I went to the store yesterday.`

### Formal (Cmd+Shift+F)
- Input: `hey can u help me out`
- Expected: `Hello, could you please assist me?`

### Casual (Cmd+Shift+C)
- Input: `I would appreciate your assistance`
- Expected: `I'd appreciate your help`

### Simplify (Cmd+Shift+S)
- Input: `The implementation utilizes sophisticated algorithms`
- Expected: `The code uses advanced algorithms`

### Expand (Cmd+Shift+E)
- Input: `Good idea`
- Expected: `That's a really good idea, and I think it could work well.`

## Running on Startup (Optional)

If you want the assistant to start automatically when you log in:

### Quick Method: Login Items

1. Create a shell script `start_assistant.sh`:
   ```bash
   #!/bin/bash
   cd /Users/ruchibommaraju/Northwestern/thoughts/autocomplete
   /usr/bin/python3 main.py
   ```

2. Make it executable:
   ```bash
   chmod +x start_assistant.sh
   ```

3. Add to Login Items:
   - System Settings → General → Login Items
   - Click **+** button
   - Select `start_assistant.sh`

### Advanced Method: LaunchAgent

See README.md for LaunchAgent setup instructions.

## Next Steps

Once everything is working:

1. **Customize hotkeys** in `config.yaml` to your preference
2. **Try in different apps** - Slack, Gmail, Word, etc.
3. **Adjust settings** - notification duration, logging level, etc.
4. **Set up autostart** if you want it always available
5. **Read the full README** for advanced features

## Getting Help

If you're still stuck:

1. Check `writing_assistant.log` for detailed error messages
2. Enable debug logging in `config.yaml`:
   ```yaml
   logging:
     level: "DEBUG"
   ```
3. Run the app and reproduce the issue
4. Check the log file: `cat writing_assistant.log`

## Security Best Practices

- ✅ Never commit `config.yaml` to git (it's in `.gitignore`)
- ✅ Keep your API key private
- ✅ Regularly check [API usage](https://aistudio.google.com/app/apikey) to monitor costs
- ✅ Consider using environment variables for the API key in production

## Success Criteria

You're ready to use the assistant when:

- [x] App starts without errors
- [x] You can see the hotkey list
- [x] Notifications appear when you trigger hotkeys
- [x] Selected text gets replaced with improved version
- [x] Log file shows successful API calls

**Congratulations! You're all set up! 🎉**
