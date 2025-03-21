# Google Forms MCQ Auto-Fill Bot

This bot automatically fills out Google Forms MCQ questions using DeepSeek AI to provide answers.

## Prerequisites

- Python 3.7 or higher
- Chrome browser installed
- DeepSeek API key

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add your DeepSeek API key:
```
DEEPSEEK_API_KEY=your_api_key_here
```

## Usage

1. Run the script:
```bash
python form_bot.py
```

2. When prompted, enter the Google Form URL.

3. The bot will:
   - Open the form in Chrome
   - Read each MCQ question
   - Use DeepSeek AI to determine the correct answer
   - Select the appropriate option
   - Submit the form automatically

## Notes

- Make sure you have a stable internet connection
- The bot works best with standard MCQ questions
- Some forms may have additional security measures that could prevent automation
- Use responsibly and in accordance with the form's terms of service

## Disclaimer

This tool is for educational purposes only. Please ensure you have permission to automate form submissions and comply with all relevant terms of service. 