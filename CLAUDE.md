# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot locally
cd src && python bot.py

# Run all tests
python -m pytest src/tests/

# Run a specific test
python -m pytest src/tests/test_persona.py::TestPersona::test_process

# Format code
black src/

# Lint code
flake8 src/
```

## Architecture Overview

This is a Portuguese-language Telegram bot that provides horoscope predictions, tarot readings, and Persona game references. The codebase uses a modular architecture with clear separation of concerns:

### Core Design Patterns

1. **Singleton Pattern**: Used for shared resources like `Environment` and `PredictionModule`. These maintain global state across command invocations.

2. **Command Pattern**: Each bot command is a separate class inheriting from `Command` base class. Commands handle authorization, processing, and response formatting.

3. **Inheritance Hierarchy**: GPT-enhanced commands inherit from traditional ones (e.g., `SignGPT` extends `Sign`), sharing core logic while adding AI capabilities.

### Key Architectural Components

- **Commands** (`src/commands/`): User-facing bot commands, each handling specific functionality
- **Fetchers** (`src/fetchers/`): Data retrieval logic, either via web scraping or AI generation
- **Modules** (`src/modules/`): Core business logic including astronomical calculations and predictions
- **Clients** (`src/clients/`): External API integrations (currently OpenAI-compatible for DeepSeek)

### Command Processing Flow

1. User sends command → `bot.py` routes to appropriate command class
2. Command validates authorization (user/group restrictions)
3. Fetcher retrieves/generates data (with caching for AI predictions)
4. Response formatted with Telegram markdown and error handling
5. Message sent back to user in Portuguese

### AI Integration

- Uses DeepSeek Chat model via OpenAI-compatible API
- Daily caching system (BRT timezone) to minimize API calls
- Retry logic with exponential backoff for reliability
- Context-aware prompts incorporating astronomical data

## Code Conventions

- **Import order**: stdlib → third-party → local (with blank lines between)
- **Error messages**: Always in Portuguese for user-facing content
- **Singleton cleanup**: Use `_reset_singleton()` in tests
- **Telegram formatting**: Use proper markdown escaping for special characters
- **Environment validation**: Check required vars on startup with clear errors

## Testing Guidelines

- Mock Telegram objects using `MagicMock` for unit tests
- Clean up singletons in test teardown to prevent state leakage
- Patch environment variables for test isolation
- Test both success and error paths for external API calls