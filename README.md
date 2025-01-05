# Cocktail Finder Python Telegram Bot 🎯

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A Telegram bot designed to help users discover and explore a variety of cocktails. Whether you're looking for a random cocktail, searching by name, ingredient, or even by the first letter, this bot has you covered.

## Features 🌟

- Random cocktail generation
- Search cocktails by name
- Search cocktails by first letter
- Search cocktails by ingredient
- Search ingredients by name
- Interactive keyboard interface
- Emoji support
- Error handling and logging
- Environment variable configuration

## Project Structure 🌟

```
python-telegram-bot
├── src
│   ├── bot.py               # Main entry point for the bot
│   ├── handlers
│   │   └── commands.py      # Command handlers for the bot
│   ├── config
│   │   └── settings.py      # Configuration settings for the bot
│   ├─── utils
│   |  └── helpers.py       # Utility functions for the bot
|   └─── services
|      └── cocktail_service.py
├── requirements.txt          # Project dependencies
├── .env                      # Environment variables
├── .gitignore                # Git ignore file
└── README.md                 # Project documentation
```

## Setup Instructions 🛠️

1. Clone the repository and move to the directory

```bash
git clone https://github.com/yourusername/telegram-pickup-bot.git
cd telegram-pickup-bot
```

2. Create virtual environment and activate it

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure environment variables

```bash
copy .env.example .env
# Edit .env with your Telegram Bot Token
```

## Usage 💡

1. Start the bot

```bash
python src/bot.py
```

2. Available Commands

- `/start` - Initialize the bot
- `/random` - Get a random cocktail
- `/search` - Search for a cocktail by name
- `/letter` - Search for cocktails by first letter
- `/ingredient` - Search for cocktails by ingredient
- `/find_ingredient` - Search for ingredients by name
- `/help` - Display help
- `/about` - Show bot information

## Dependencies 📦

- python-telegram-bot
- python-dotenv
- requests

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

Distributed under the MIT License. See LICENSE for more information.

## Contact 📧

Find me - `@alishahriarioff` - on every platform.
