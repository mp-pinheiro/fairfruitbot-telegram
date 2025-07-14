# Fairfruit Bot - Repository Summary

## Overview

**Fairfruit Bot** is a Portuguese-language Telegram bot that provides horoscope predictions, tarot readings, and incorporates anime references from the Persona game series. The bot combines traditional astrological content with modern AI-powered predictions using OpenAI's GPT models.

## Features

### 🔮 Horoscope Predictions
- **Traditional Mode** (`/bidu_old`): Web-scraped horoscope readings from external sources
- **AI-Powered Mode** (`/bidu`): GPT-generated personalized horoscope predictions
- **Real Astronomical Data**: Uses actual planetary positions calculated with astropy and skyfield
- **12 Zodiac Signs**: Full support for all zodiac signs in Portuguese

### 🃏 Tarot Readings  
- **Daily Tarot** (`/tarot`): Personal daily tarot card draws (one per user per day)
- **Arcana Information**: Detailed information about specific tarot arcanas
- **Persona Integration**: References to characters from Persona video game series
- **AI-Enhanced**: GPT-powered interpretations and traditional card meanings

### 🤖 AI Integration
- **DeepSeek Chat Model**: Uses DeepSeek's chat model (deepseek-chat) via OpenAI API
- **Context-Aware**: Incorporates real astronomical data and user history
- **Intelligent Caching**: Daily prediction caching with Brazilian timezone support
- **Rate Limiting**: Built-in retry logic and error handling for API calls
- **Bilingual Support**: Primarily Portuguese with some English elements

## Technical Architecture

## Technical Architecture

### System Flow Diagram
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │    │    Bot.py        │    │   Commands      │
│   Users         │───▶│   (Main Entry)   │───▶│   /bidu         │
│                 │    │                  │    │   /tarot        │
└─────────────────┘    └──────────────────┘    │   /bidu_old     │
                                               │   /tarot_old    │
                                               └─────────┬───────┘
                                                         │
                              ┌─────────────────────────▼──────────────────────┐
                              │                 Fetchers                       │
                              │  ┌─────────────┐  ┌─────────────────────────┐  │
                              │  │ Traditional │  │      AI-Powered         │  │
                              │  │   Fetchers  │  │      Fetchers           │  │
                              │  │             │  │                         │  │
                              │  │ ┌─────────┐ │  │ ┌─────────┐ ┌─────────┐ │  │
                              │  │ │ Sign    │ │  │ │ SignGPT │ │TarotGPT │ │  │
                              │  │ │ Tarot   │ │  │ │         │ │         │ │  │
                              │  │ └─────────┘ │  │ └─────────┘ └─────────┘ │  │
                              │  └─────────────┘  └─────────────────────────┘  │
                              └────────┬─────────────────────┬─────────────────┘
                                       │                     │
                        ┌──────────────▼──────────┐         │
                        │     External Data       │         │
                        │                         │         │
                        │ ┌─────────────────────┐ │         │
                        │ │  joaobidu.com.br    │ │         │
                        │ │  (Web Scraping)     │ │         │
                        │ └─────────────────────┘ │         │
                        │                         │         │
                        │ ┌─────────────────────┐ │         │
                        │ │ Astronomical Data   │ │         │
                        │ │ (Astropy/Skyfield) │ │         │
                        │ └─────────────────────┘ │         │
                        │                         │         │
                        │ ┌─────────────────────┐ │         │
                        │ │   Local JSON        │ │         │
                        │ │ (Arcanas, Planets)  │ │         │
                        │ └─────────────────────┘ │         │
                        └─────────────────────────┘         │
                                                            │
                                           ┌────────────────▼─────────────────┐
                                           │            AI Services            │
                                           │                                  │
                                           │ ┌──────────────────────────────┐ │
                                           │ │        DeepSeek API          │ │
                                           │ │    (via OpenAI interface)    │ │
                                           │ └──────────────────────────────┘ │
                                           └──────────────────────────────────┘
```

### Core Components

```
src/
├── bot.py              # Main bot entry point and command registration
├── environment.py      # Environment configuration and validation
├── commands/           # Bot command handlers
│   ├── sign.py         # Traditional horoscope command
│   ├── sign_gpt.py     # AI-powered horoscope command  
│   ├── tarot.py        # Traditional tarot command
│   ├── tarot_gpt.py    # AI-powered tarot command
│   └── command.py      # Base command class
├── fetchers/           # Data fetching layer
│   ├── sign_fetcher.py # Horoscope data scraping
│   ├── tarot_fetcher.py# Tarot data management
│   └── *_gpt.py        # AI-powered data fetchers
├── modules/            # Core functionality modules
│   ├── astro_module.py # Astronomical calculations
│   ├── prediction_module.py # AI prediction generation
│   └── users_module.py # User management
├── clients/            # External API clients
│   └── openai_client.py # OpenAI API integration
└── tests/              # Unit tests
```

### Data Storage
```
data/
├── arcanas.json        # Tarot arcana definitions with Persona references
└── planet_data.json   # Pre-calculated planetary positions
```

## Technology Stack

### Core Dependencies
- **Python 3.10+**: Main programming language
- **python-telegram-bot**: Telegram Bot API wrapper
- **openai**: DeepSeek API integration (via OpenAI-compatible interface)
- **requests + beautifulsoup4**: Web scraping from joaobidu.com.br
- **python-dotenv**: Environment management

### Astronomical Libraries
- **astropy**: Professional astronomy calculations
- **skyfield**: Precise planetary position calculations using JPL ephemeris
- **astroquery**: Astronomical data queries

### Development Tools
- **pytest**: Testing framework
- **flake8**: Code linting
- **black**: Code formatting
- **yapf**: Alternative code formatting

## Bot Commands

| Command | Description | Type |
|---------|-------------|------|
| `/bidu [sign]` | AI-powered horoscope reading | GPT-Enhanced |
| `/bidu_old [sign]` | Traditional web-scraped horoscope | Web Scraping |
| `/tarot` | Daily tarot card draw | User-specific |
| `/tarot [arcana]` | Information about specific arcana | Reference |

## Setup Instructions

### Prerequisites
- Python 3.10.14 or higher
- Telegram Bot Token (from @BotFather)
- OpenAI API Key (for GPT features)

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Create a `.env` file with:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_deepseek_api_key
   ```
   
   Note: The bot uses DeepSeek's API via OpenAI-compatible interface.

3. **Run the bot:**
   ```bash
   cd src
   python bot.py
   ```

### Raspberry Pi Setup
The repository includes specific instructions for Raspberry Pi deployment using pyenv for Python version management.

## Data Sources

### Horoscope Data
- **Primary Source**: joaobidu.com.br (Brazilian horoscope website)
- **Web Scraping**: Automated extraction of daily predictions, tips, and colors
- **Real-time Calculations**: Astronomical calculations for planetary positions
- **Historical Data**: Pre-calculated planetary positions for performance optimization
- **Fuzzy Matching**: Intelligent zodiac sign recognition with typo tolerance

### Tarot Data
- **Traditional Meanings**: Classic tarot card interpretations
- **Persona Integration**: Character mappings from Persona video game series
- **Custom Descriptions**: Blend of traditional and modern gaming culture elements
- **Daily Uniqueness**: Algorithm ensures different cards for users each day

### Astronomical Data
- **JPL Ephemeris**: Uses DE440s for accurate planetary positions
- **Real-time Calculations**: Live coordinate transformations using astropy
- **Brazilian Timezone**: All predictions use BRT (UTC-3) timezone
- **Zodiac Boundaries**: Precise degree calculations for sign determination

## User Experience

### Language
- **Primary**: Portuguese (Brazilian)
- **Target Audience**: Portuguese-speaking users interested in astrology and Persona games
- **Tone**: Casual and friendly with anime references

### Personalization
- **Daily Tarot**: One unique card per user per day
- **Horoscope**: Customizable by zodiac sign with fuzzy matching
- **AI Predictions**: Context-aware based on astronomical data

### Error Handling
- Comprehensive error logging and user-friendly error messages
- Graceful fallbacks for external service failures
- Input validation with helpful suggestions for misspelled signs

## Development Features

### Code Quality
- Modular architecture with clear separation of concerns
- Singleton pattern for shared resources
- Type hints and documentation
- Unit tests for core functionality

### Extensibility
- Plugin-based command system
- Abstract base classes for easy feature addition
- Configurable data sources and AI models
- Support for multiple languages and regions

## License

Licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

The project follows standard Python development practices:
- Code formatting with black/yapf
- Linting with flake8
- Testing with pytest
- Git workflow with feature branches

## Key Technical Insights

### Smart Caching System
- **Daily Cache**: Predictions are cached per day using Brazilian timezone (BRT)
- **User Management**: Individual tarot cards tracked per user to ensure uniqueness
- **Performance**: Pre-calculated astronomical data reduces computation overhead
- **Memory Efficient**: Singleton pattern prevents resource duplication

### Error Handling & Resilience
- **Graceful Degradation**: Fallbacks when external services fail
- **User-Friendly Messages**: Portuguese error messages with helpful suggestions
- **Rate Limiting**: Intelligent retry logic for API calls with exponential backoff
- **Input Validation**: Fuzzy matching for zodiac signs handles typos gracefully

### Internationalization Features
- **Brazilian Portuguese**: Primary language with cultural context
- **Date Formatting**: Brazilian date format (DD/MM/YYYY)
- **Timezone Awareness**: All operations use Brasília timezone (UTC-3)
- **Cultural References**: Incorporates Brazilian horoscope traditions

### Security & Configuration
- **Environment Variables**: Secure API key and token management
- **Input Sanitization**: Telegram message escaping and validation
- **Error Isolation**: Errors don't crash the bot, users get friendly messages
- **API Key Validation**: Startup checks ensure required credentials are present

## Architecture Patterns

### Command Pattern
- **Modular Commands**: Each bot function is a separate command class
- **Inheritance**: Base `Command` class provides common functionality
- **Polymorphism**: GPT and traditional versions share interfaces
- **Registration**: Dynamic command registration with Telegram dispatcher

### Factory Pattern
- **Fetcher Factory**: Different data fetchers for various sources
- **Module Factory**: Prediction modules created based on type
- **Client Factory**: API clients instantiated as needed

### Singleton Pattern
- **Environment**: Single configuration instance across application
- **Prediction Module**: Shared cache and state management
- **Resource Optimization**: Prevents duplicate API clients and data structures

## Performance Optimizations

### Data Caching
- **Astronomical Data**: Pre-calculated planetary positions stored in JSON
- **Daily Predictions**: AI-generated content cached for 24 hours
- **User State**: Tarot card history maintained in memory

### Resource Management
- **Connection Pooling**: HTTP sessions reused for web scraping
- **Memory Efficiency**: Lazy loading of astronomical ephemeris data
- **API Rate Limiting**: Built-in delays and retry logic prevent throttling

---

*This bot represents a unique fusion of traditional astrology, modern AI technology, and gaming culture, specifically designed for the Brazilian Portuguese-speaking community interested in both mysticism and contemporary entertainment.*