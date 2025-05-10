# Dead Man Switch

A confidential dead man's switch application built with ROFL.

## Prerequisites

1. Python 3.9 or higher
2. Docker
3. Telegram Bot Token (get from @BotFather)
4. Oasis CLI installed

## Setup

1. Create a Telegram bot:
   - Message @BotFather on Telegram
   - Use `/newbot` command
   - Follow instructions to create bot
   - Save the bot token

2. Set up environment variable:
   ```bash
   export TELEGRAM_TOKEN="your_bot_token"
   ```

3. Build the Docker image:
   ```bash
   docker build -t deadmanswitch .
   ```

## Usage

### Create an Alert
```bash
python cli.py create \
  --id "my_alert" \
  --message "This is my secret message" \
  --group-id "TELEGRAM_GROUP_ID" \
  --expiry 30 \
  --check-in 7
```

### Check In
```bash
python cli.py checkin --id "my_alert"
```

### Manually Trigger Alert
```bash
python cli.py trigger --id "my_alert"
```

## Deploying to ROFL

1. Initialize ROFL app:
   ```bash
   oasis rofl init
   ```

2. Set secret:
   ```bash
   echo -n "$TELEGRAM_TOKEN" | oasis rofl secret set TELEGRAM_TOKEN -
   ```

3. Build and deploy:
   ```bash
   oasis rofl build
   oasis rofl deploy
   ```

## Security Notes

- All sensitive data is ephemeral and only exists in memory for the session
- The application runs in a Trusted Execution Environment (TEE)
- The node operator cannot access the sensitive data 