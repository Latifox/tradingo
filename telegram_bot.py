from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yaml
from datetime import datetime


class TelegramBot:

    def __init__(self, token, allowed_chat_ids, filter_criteria):
        self.application = Application.builder().token(token).build()
        self.allowed_chat_ids = set(
            int(chat_id) for chat_id in allowed_chat_ids)
        self.filter_criteria = filter_criteria
        self.subscribed_users = set()

    def setup(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(
            CommandHandler("scan_new_listings", self.scan_new_listings))
        self.application.add_handler(
            CommandHandler("chain_selection", self.chain_selection))
        self.application.add_handler(
            CommandHandler("min_volume", self.min_volume))
        self.application.add_handler(
            CommandHandler("min_liquidity", self.min_liquidity))
        self.application.add_handler(
            CommandHandler("max_supply", self.max_supply))
        self.application.add_handler(
            CommandHandler("min_market_cap", self.min_market_cap))
        self.application.add_handler(
            CommandHandler("max_market_cap", self.max_market_cap))
        self.application.add_handler(
            CommandHandler("min_price_change", self.min_price_change))
        self.application.add_handler(
            CommandHandler("min_volume_usd", self.min_volume_usd))
        self.application.add_handler(
            CommandHandler("token_security", self.token_security))
        self.application.add_handler(
            CommandHandler("creator_threshold", self.creator_threshold))
        self.application.add_handler(
            CommandHandler("first_mint_date", self.first_mint_date))
        self.application.add_handler(
            CommandHandler("supply_traded_percentage",
                           self.supply_traded_percentage))
        self.application.add_handler(
            CommandHandler("subscribe", self.subscribe))
        self.application.add_handler(
            CommandHandler("unsubscribe", self.unsubscribe))
        self.application.add_handler(CommandHandler("status", self.status))

    async def run(self):
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

    async def stop(self):
        await self.application.stop()

    async def send_alert(self, chat_id, message):
        if int(chat_id) in self.allowed_chat_ids and int(
                chat_id) in self.subscribed_users:
            await self.application.bot.send_message(chat_id=chat_id,
                                                    text=message)

    async def start(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            await update.message.reply_text(
                'Welcome to the Token Scanning Bot! Use /help to see available commands.'
            )
        else:
            await update.message.reply_text(
                'You are not authorized to use this bot.')

    async def help_command(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            help_text = """
            Available commands:
            /start - Start the bot
            /help - Show this help message
            /scan_new_listings [on/off] - Set whether to scan only new listings
            /chain_selection [all/specific] [chain_name] - Choose chains to scan
            /min_volume [time_period] [value] - Set minimum volume
            /min_liquidity [value] - Set minimum liquidity
            /max_supply [value] - Set maximum token supply
            /min_market_cap [value] - Set minimum market cap
            /max_market_cap [value] - Set maximum market cap
            /min_price_change [percentage] [time_period] - Set minimum price change
            /min_volume_usd [value] [time_period] - Set minimum USD volume
            /token_security [on/off] - Enable/disable token security checks
            /creator_threshold [percentage] - Set creator ownership threshold
            /first_mint_date [date_time] - Set first mint date
            /supply_traded_percentage [percentage] - Set minimum supply traded
            /subscribe - Subscribe to real-time updates
            /unsubscribe - Unsubscribe from updates
            /status - Show current settings
            """
            await update.message.reply_text(help_text)

    async def scan_new_listings(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            if len(context.args) != 1 or context.args[0] not in ['on', 'off']:
                await update.message.reply_text(
                    "Usage: /scan_new_listings [on/off]")
                return
            self.filter_criteria['scan_new_listings_only'] = context.args[
                0] == 'on'
            await update.message.reply_text(
                f"Scan new listings only: {'On' if context.args[0] == 'on' else 'Off'}"
            )

    async def chain_selection(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            if len(context.args) < 1 or context.args[0] not in [
                    'all', 'specific'
            ]:
                await update.message.reply_text(
                    "Usage: /chain_selection [all/specific] [chain_name]")
                return
            if context.args[0] == 'all':
                self.filter_criteria['chains'] = ['all']
            else:
                if len(context.args) != 2:
                    await update.message.reply_text(
                        "Please specify a chain name for specific selection.")
                    return
                self.filter_criteria['chains'] = [context.args[1]]
            await update.message.reply_text(
                f"Chain selection updated: {self.filter_criteria['chains']}")

    async def min_volume(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            if len(context.args) != 2:
                await update.message.reply_text(
                    "Usage: /min_volume [time_period] [value]")
                return
            time_period, value = context.args
            try:
                value = float(value)
                self.filter_criteria['min_volume'][time_period] = value
                await update.message.reply_text(
                    f"Minimum volume for {time_period} set to {value}")
            except ValueError:
                await update.message.reply_text(
                    "Invalid value. Please enter a number.")

    async def min_liquidity(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            if len(context.args) != 1:
                await update.message.reply_text("Usage: /min_liquidity [value]"
                                                )
                return
            try:
                value = float(context.args[0])
                self.filter_criteria['min_liquidity'] = value
                await update.message.reply_text(
                    f"Minimum liquidity set to {value}")
            except ValueError:
                await update.message.reply_text(
                    "Invalid value. Please enter a number.")

    async def max_supply(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            if len(context.args) != 1:
                await update.message.reply_text("Usage: /max_supply [value]")
                return
            try:
                value = float(context.args[0])
                self.filter_criteria['max_supply'] = value
                await update.message.reply_text(
                    f"Maximum supply set to {value}")
            except ValueError:
                await update.message.reply_text(
                    "Invalid value. Please enter a number.")

    async def min_market_cap(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            if len(context.args) != 1:
                await update.message.reply_text(
                    "Usage: /min_market_cap [value]")
                return
            try:
                value = float(context.args[0])
                self.filter_criteria['min_market_cap'] = value
                await update.message.reply_text(
                    f"Minimum market cap set to {value}")
            except ValueError:
                await update.message.reply_text(
                    "Invalid value. Please enter a number.")

    async def max_market_cap(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            if len(context.args) != 1:
                await update.message.reply_text(
                    "Usage: /max_market_cap [value]")
                return
            try:
                value = float(context.args[0])
                self.filter_criteria['max_market_cap'] = value
                await update.message.reply_text(
                    f"Maximum market cap set to {value}")
            except ValueError:
                await update.message.reply_text(
                    "Invalid value. Please enter a number.")

    async def min_price_change(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            if len(context.args) != 2:
                await update.message.reply_text(
                    "Usage: /min_price_change [percentage] [time_period]")
                return
            percentage, time_period = context.args
            try:
                percentage = float(percentage)
                self.filter_criteria['min_price_change'][
                    time_period] = percentage
                await update.message.reply_text(
                    f"Minimum price change for {time_period} set to {percentage}%"
                )
            except ValueError:
                await update.message.reply_text(
                    "Invalid value. Please enter a number for percentage.")

    async def min_volume_usd(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            if len(context.args) != 2:
                await update.message.reply_text(
                    "Usage: /min_volume_usd [value] [time_period]")
                return
            value, time_period = context.args
            try:
                value = float(value)
                self.filter_criteria['min_volume_usd'][time_period] = value
                await update.message.reply_text(
                    f"Minimum USD volume for {time_period} set to ${value}")
            except ValueError:
                await update.message.reply_text(
                    "Invalid value. Please enter a number.")

    async def token_security(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            if len(context.args) != 1 or context.args[0] not in ['on', 'off']:
                await update.message.reply_text(
                    "Usage: /token_security [on/off]")
                return
            self.filter_criteria['token_security'] = context.args[0] == 'on'
            await update.message.reply_text(
                f"Token security checks: {'On' if context.args[0] == 'on' else 'Off'}"
            )

    async def creator_threshold(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            if len(context.args) != 1:
                await update.message.reply_text(
                    "Usage: /creator_threshold [percentage]")
                return
            try:
                value = float(context.args[0])
                self.filter_criteria['max_creator_ownership'] = value
                await update.message.reply_text(
                    f"Creator ownership threshold set to {value}%")
            except ValueError:
                await update.message.reply_text(
                    "Invalid value. Please enter a number.")

    async def first_mint_date(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            if len(context.args) != 1:
                await update.message.reply_text(
                    "Usage: /first_mint_date [YYYY-MM-DD]")
                return
            try:
                date = datetime.strptime(context.args[0], "%Y-%m-%d")
                self.filter_criteria['first_mint_date'] = date.isoformat()
                await update.message.reply_text(
                    f"First mint date set to {context.args[0]}")
            except ValueError:
                await update.message.reply_text(
                    "Invalid date format. Please use YYYY-MM-DD.")

    async def supply_traded_percentage(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            if len(context.args) != 1:
                await update.message.reply_text(
                    "Usage: /supply_traded_percentage [percentage]")
                return
            try:
                value = float(context.args[0])
                self.filter_criteria['min_supply_traded'] = value
                await update.message.reply_text(
                    f"Minimum supply traded percentage set to {value}%")
            except ValueError:
                await update.message.reply_text(
                    "Invalid value. Please enter a number.")

    async def subscribe(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            self.subscribed_users.add(update.effective_chat.id)
            await update.message.reply_text(
                "You have subscribed to real-time updates.")

    async def unsubscribe(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            self.subscribed_users.discard(update.effective_chat.id)
            await update.message.reply_text(
                "You have unsubscribed from real-time updates.")

    async def status(self, update, context):
        if update.effective_chat.id in self.allowed_chat_ids:
            status_text = "Current settings:\n"
            for key, value in self.filter_criteria.items():
                status_text += f"{key}: {value}\n"
            status_text += f"Subscribed to updates: {'Yes' if update.effective_chat.id in self.subscribed_users else 'No'}"
            await update.message.reply_text(status_text)
