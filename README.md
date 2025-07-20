# Fairfruit Bot

Horoscope predictions, tarot and disgusting Persona weebery.

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
TELEGRAM_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
ALLOWED_USER_IDS=123456789,987654321
MONITORED_GROUP_IDS=-1001467780714,-1001234567890
DEV_MODE=false
```

### Environment Variables

- `TELEGRAM_TOKEN` - Bot token from @BotFather
- `OPENAI_API_KEY` - OpenAI-compatible API key for DeepSeek  
- `ALLOWED_USER_IDS` - User IDs allowed in private chats (optional)
- `MONITORED_GROUP_IDS` - Group IDs for GroupSummary/TypoDetector (optional)
- `DEV_MODE` - Testing mode with reduced thresholds (optional)

### Features

- **User Authorization**: Control private chat access via `ALLOWED_USER_IDS`
- **Group Monitoring**: GroupSummary (6️⃣) and TypoDetector work in `MONITORED_GROUP_IDS`
- **Dev Mode**: Easier testing with reduced thresholds
- Bot logs user and group IDs for easy configuration

# God Damn Raspberry Pi

Setting up for it is a pain, so here's the only fucking way I got it to work.

First we install pyenv:

```bash
curl https://pyenv.run | bash
ln -s 
```

## 2. Set up pyenv in your shell

Add the following lines to your shell startup file (`~/.bashrc` or `~/.zshrc`, depending on your shell):

```bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Then, apply the changes:

```bash
source ~/.bashrc
```

## 3. Install Minimal Dependencies

Install the minimal necessary development libraries:

```bash
sudo apt-get update
sudo apt-get install -y \
    libbz2-dev \
    libncurses5-dev \
    libreadline-dev \
    libsqlite3-dev \
    liblzma-dev \
    libssl-dev \
    zlib1g-dev
```

## 4. Install Python using pyenv

Install Python 3.10.14 using pyenv:

```bash
CFLAGS="-I/usr/include" LDFLAGS="-L/usr/lib" pyenv install 3.10.14
```

Set Python 3.10.14 as the global version:

```bash
pyenv global 3.10.14
```

## 5. Verify the Installation

Verify that Python and the required modules are correctly installed:

```bash
python -c "import bz2; import curses; import readline; import sqlite3; import lzma; print('All modules imported successfully')"
```