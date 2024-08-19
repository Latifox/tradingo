from token_filter import TokenFilter


class TokenScanner:

    def __init__(self, api, filter_criteria, scan_new_listings_only):
        self.api = api
        self.token_filter = TokenFilter(filter_criteria)
        self.scan_new_listings_only = scan_new_listings_only

    async def scan_tokens(self, chains):
        matching_tokens = []
        for chain in chains:
            try:
                if self.scan_new_listings_only:
                    tokens_to_scan = await self.api.get_new_listings(chain)
                else:
                    tokens_to_scan = await self.api.get_all_tokens(chain)

                if isinstance(tokens_to_scan, list):
                    for token in tokens_to_scan:
                        if isinstance(token, dict) and 'address' in token:
                            token_data = await self.api.get_token_data(
                                chain, token['address'])
                        elif isinstance(token, str):
                            # Assuming the token is just an address string
                            token_data = await self.api.get_token_data(
                                chain, token)
                        else:
                            continue  # Skip invalid token data

                        ohlcv_data = {
                            '5m':
                            await
                            self.api.get_ohlcv(chain, token_data['address'],
                                               '5m'),
                            '10m':
                            await self.api.get_ohlcv(chain,
                                                     token_data['address'],
                                                     '10m'),
                            '1h':
                            await self.api.get_ohlcv(chain,
                                                     token_data['address'],
                                                     '1h'),
                            '24h':
                            await self.api.get_ohlcv(chain,
                                                     token_data['address'],
                                                     '24h')
                        }
                        security_data = await self.api.get_token_security(
                            chain, token_data['address'])

                        if self.token_filter.matches_criteria(
                                token_data, ohlcv_data, security_data):
                            matching_tokens.append(token_data)
                elif isinstance(tokens_to_scan, dict):
                    # Handle case where API returns a dict instead of a list
                    for address, token_data in tokens_to_scan.items():
                        ohlcv_data = {
                            '5m': await
                            self.api.get_ohlcv(chain, address, '5m'),
                            '10m': await
                            self.api.get_ohlcv(chain, address, '10m'),
                            '1h': await
                            self.api.get_ohlcv(chain, address, '1h'),
                            '24h': await
                            self.api.get_ohlcv(chain, address, '24h')
                        }
                        security_data = await self.api.get_token_security(
                            chain, address)

                        if self.token_filter.matches_criteria(
                                token_data, ohlcv_data, security_data):
                            matching_tokens.append(token_data)
            except Exception as e:
                print(f"Error scanning chain {chain}: {str(e)}")

        return matching_tokens
