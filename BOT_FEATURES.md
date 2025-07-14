# Bot Protection and Multi-Group Features

This document describes the new security and configuration features added to the Fairfruit Bot.

## Overview

Two new features have been implemented to enhance bot security and functionality:

1. **User Authorization Protection**: Restrict who can use bot commands
2. **Multiple Group Support**: Enable summary feature in multiple Telegram groups

## Features

### 1. User Authorization Protection

Control which users can access the bot commands through environment variable configuration.

**Environment Variable**: `ALLOWED_USER_IDS`

**Behavior**:
- If not set or empty: All users can use the bot (default behavior)
- If set: Only specified user IDs can use bot commands
- Unauthorized users receive a Portuguese message: "🚫 Você não tem permissão para usar este comando."

**Examples**:
```bash
# Allow all users (default)
# ALLOWED_USER_IDS=

# Allow single user
ALLOWED_USER_IDS=123456789

# Allow multiple users
ALLOWED_USER_IDS=123456789,987654321,555444333
```

**Finding User IDs**:
1. Add the bot to a group or start a private chat
2. Send any command to the bot
3. Check the bot logs for user ID information:
   ```
   command: bidu - user: (123456789) username - channel: -1001234567890 - text: /bidu
   ```

### 2. Multiple Group Support for Summaries

Configure the summary feature to work in multiple Telegram groups.

**Environment Variable**: `SUMMARY_GROUP_IDS`

**Behavior**:
- If not set: Uses original hardcoded group `-1001467780714` (backward compatibility)
- If set: Summary feature works in all specified groups
- Supports comma-separated list of negative group IDs

**Examples**:
```bash
# Use default group (backward compatibility)
# SUMMARY_GROUP_IDS=

# Single custom group
SUMMARY_GROUP_IDS=-1001234567890

# Multiple groups
SUMMARY_GROUP_IDS=-1001467780714,-1001234567890,-1009876543210
```

**Finding Group IDs**:
1. Add the bot to the desired group(s)
2. Send any message in the group
3. Check the bot logs for group ID information:
   ```
   GroupSummary - chat: -1001234567890 - user: (123456789) username - text: hello
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root with your configuration:

```bash
# Required: Bot token from @BotFather
TELEGRAM_TOKEN=your_telegram_bot_token_here

# Optional: User restrictions (comma-separated user IDs)
ALLOWED_USER_IDS=123456789,987654321

# Optional: Summary group IDs (comma-separated group IDs)
SUMMARY_GROUP_IDS=-1001467780714,-1001234567890
```

### Example Configurations

**Open Bot (Default)**:
```bash
TELEGRAM_TOKEN=your_token
# No restrictions - all users can use the bot
# Summary works in original group only
```

**Restricted Bot**:
```bash
TELEGRAM_TOKEN=your_token
ALLOWED_USER_IDS=123456789,987654321
SUMMARY_GROUP_IDS=-1001467780714,-1001234567890
```

**Admin-Only Bot**:
```bash
TELEGRAM_TOKEN=your_token
ALLOWED_USER_IDS=123456789
SUMMARY_GROUP_IDS=-1001234567890
```

## Usage

### Starting the Bot

1. Configure your `.env` file with the desired settings
2. Run the bot:
   ```bash
   cd src
   python bot.py
   ```

### Testing Authorization

1. **Authorized User**: Commands work normally
2. **Unauthorized User**: Receives rejection message in Portuguese

### Testing Multiple Groups

1. Add bot to multiple groups specified in `SUMMARY_GROUP_IDS`
2. In any configured group, send a message containing trigger phrases:
   - "6 falam"
   - "vcs falam" 
   - "ces falam"
   - "6️⃣"
3. Bot should respond with summary in that group

### Logs

The bot logs configuration on startup:
```
INFO - Bot access restricted to user IDs: [123456789, 987654321]
INFO - Summary feature enabled for group IDs: [-1001467780714, -1001234567890]
```

Or for open access:
```
INFO - Bot access open to all users
INFO - Summary feature enabled for group IDs: [-1001467780714]
```

## Backward Compatibility

- **No configuration changes needed** for existing deployments
- Without environment variables, bot behaves exactly as before
- Original group ID `-1001467780714` remains the default for summaries
- All existing commands continue to work unchanged

## Security Notes

- User IDs are logged for debugging and security monitoring
- Unauthorized access attempts are logged as warnings
- Group IDs are negative numbers (Telegram standard for groups)
- Environment variables should be kept secure and not committed to version control

## Troubleshooting

### Common Issues

1. **Bot not responding to authorized users**:
   - Check user ID format (numbers only, no spaces)
   - Verify `.env` file is loaded correctly
   - Check bot logs for user ID being used

2. **Summary not working in new groups**:
   - Verify group ID format (negative numbers)
   - Ensure bot has necessary permissions in the group
   - Check that trigger phrases are used correctly

3. **Environment variables not loading**:
   - Ensure `.env` file is in the correct location
   - Check file permissions
   - Restart the bot after making changes

### Getting Help

Check the bot logs for detailed information about:
- Configuration loading
- User authorization attempts
- Group message processing
- Environment variable parsing

Example log entries:
```
INFO - Bot access restricted to user IDs: [123456789]
WARNING - Unauthorized access attempt - command: bidu - user: (999999999) unauthorized_user
INFO - GroupSummary - chat: -1001234567890 - user: (123456789) username - text: 6 falam
```