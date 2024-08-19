import asyncio
import yaml
from birdeye_api import BirdeyeAPI
from token_scanner import TokenScanner
from telegram_bot import TelegramBot
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def main():
    try:
        # Load configuration
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)

        # Ensure chat IDs are integers
        allowed_chat_ids = [
            int(chat_id) for chat_id in config['allowed_chat_ids']
        ]

        # Initialize components
        api = BirdeyeAPI(config['birdeye_api_key'])
        scanner = TokenScanner(api, config['filter_criteria'],
                               config['scan_new_listings_only'])
        bot = TelegramBot(config['telegram_bot_token'], allowed_chat_ids,
                          config['filter_criteria'])

        # Setup and start the bot
        bot.setup()
        await bot.run()

        logger.info("Bot started successfully")

        # Start scanning
        while True:
            try:
                matching_tokens = await scanner.scan_tokens(config['chains'])
                for token in matching_tokens:
                    alert_message = (
                        f"New token alert:\n"
                        f"Symbol: {token.get('symbol', 'N/A')}\n"
                        f"Chain: {token.get('chain', 'N/A')}\n"
                        f"Address: {token.get('address', 'N/A')}\n"
                        f"Market Cap: ${token.get('marketCap', 0):,.2f}\n"
                        f"24h Volume: ${token.get('volume', {}).get('h24', 0):,.2f}\n"
                        f"24h Price Change: {token.get('priceChange', {}).get('h24', 0)}%\n"
                        f"Liquidity: ${token.get('liquidity', 0):,.2f}\n"
                        f"Total Supply: {token.get('totalSupply', 0):,.0f}\n"
                        f"Creator Ownership: {token.get('creatorOwnership', 0)}%"
                    )
                    for chat_id in bot.subscribed_users:
                        await bot.send_alert(chat_id, alert_message)

                logger.info(
                    f"Scanned and found {len(matching_tokens)} matching tokens"
                )

            except Exception as e:
                logger.error(f"An error occurred during scanning: {e}",
                             exc_info=True)

            # Wait for the next scan interval
            await asyncio.sleep(config['scan_interval'])

    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)

    finally:
        # Ensure the bot is properly shut down
        if 'bot' in locals():
            await bot.stop()
        logger.info("Bot shut down")


if __name__ == "__main__":
    asyncio.run(main())
