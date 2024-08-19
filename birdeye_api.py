import aiohttp
from datetime import datetime, timedelta


class BirdeyeAPI:

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://public-api.birdeye.so"
        self.last_scan_time = datetime.now() - timedelta(minutes=5)

    async def get_token_data(self, chain, address):
        async with aiohttp.ClientSession() as session:
            headers = {"X-API-KEY": self.api_key}
            url = f"{self.base_url}/public/token/{chain}/{address}"
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                return data.get('data',
                                {})  # Assuming the API returns a 'data' field

    async def get_new_listings(self, chain):
        current_time = datetime.now()
        async with aiohttp.ClientSession() as session:
            headers = {"X-API-KEY": self.api_key}
            url = f"{self.base_url}/public/new_listings/{chain}"
            params = {
                "from": self.last_scan_time.isoformat(),
                "to": current_time.isoformat()
            }
            async with session.get(url, headers=headers,
                                   params=params) as response:
                data = await response.json()
                new_listings = data.get(
                    'data', [])  # Assuming the API returns a 'data' field
        self.last_scan_time = current_time
        return new_listings

    async def get_all_tokens(self, chain):
        async with aiohttp.ClientSession() as session:
            headers = {"X-API-KEY": self.api_key}
            url = f"{self.base_url}/public/all_tokens/{chain}"
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                return data.get('data',
                                {})  # Assuming the API returns a 'data' field

    async def get_token_security(self, chain, address):
        async with aiohttp.ClientSession() as session:
            headers = {"X-API-KEY": self.api_key}
            url = f"{self.base_url}/public/token_security/{chain}/{address}"
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                return data.get('data',
                                {})  # Assuming the API returns a 'data' field

    async def get_ohlcv(self, chain, address, interval):
        async with aiohttp.ClientSession() as session:
            headers = {"X-API-KEY": self.api_key}
            url = f"{self.base_url}/public/ohlcv/{chain}/{address}"
            params = {"interval": interval}
            async with session.get(url, headers=headers,
                                   params=params) as response:
                data = await response.json()
                return data.get('data',
                                {})  # Assuming the API returns a 'data' field
