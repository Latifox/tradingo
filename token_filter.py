from datetime import datetime


class TokenFilter:

    def __init__(self, criteria):
        self.criteria = criteria

    def matches_criteria(self, token, ohlcv_data, security_data):
        if not self._check_volume(token, ohlcv_data):
            return False
        if not self._check_volume_usd(ohlcv_data):
            return False
        if not self._check_liquidity(token):
            return False
        if not self._check_market_cap(token):
            return False
        if not self._check_price_change(ohlcv_data):
            return False
        if not self._check_creator_ownership(security_data):
            return False
        if not self._check_supply_traded(token, ohlcv_data):
            return False
        if not self._check_token_security(security_data):
            return False
        if not self._check_first_mint_date(token):
            return False
        return True

    def _check_volume(self, token, ohlcv_data):
        for period, min_volume in self.criteria['min_volume'].items():
            if self._calculate_valid_volume(ohlcv_data[period]) < min_volume:
                return False
        return True

    def _check_volume_usd(self, ohlcv_data):
        for period, min_volume_usd in self.criteria['min_volume_usd'].items():
            if ohlcv_data[period]['volume_usd'] < min_volume_usd:
                return False
        return True

    def _check_liquidity(self, token):
        return token.get('liquidity', 0) >= self.criteria['min_liquidity']

    def _check_market_cap(self, token):
        market_cap = token.get('marketCap', 0)
        return self.criteria['min_market_cap'] <= market_cap <= self.criteria[
            'max_market_cap']

    def _check_price_change(self, ohlcv_data):
        for period, min_change in self.criteria['min_price_change'].items():
            if ohlcv_data[period]['price_change_percent'] < min_change:
                return False
        return True

    def _check_creator_ownership(self, security_data):
        return security_data.get('creator_ownership',
                                 100) <= self.criteria['max_creator_ownership']

    def _check_supply_traded(self, token, ohlcv_data):
        total_supply = token.get('totalSupply', 0)
        if total_supply == 0:
            return False
        volume_24h = ohlcv_data['24h']['volume']
        percent_traded = (volume_24h / total_supply) * 100
        return percent_traded >= self.criteria['min_supply_traded']

    def _check_token_security(self, security_data):
        return not self.criteria['token_security'] or security_data.get(
            'is_secure', False)

    def _check_first_mint_date(self, token):
        first_mint_date = datetime.fromisoformat(
            self.criteria['first_mint_date'])
        token_mint_date = datetime.fromisoformat(
            token.get('mintDate', '1970-01-01T00:00:00Z'))
        return token_mint_date >= first_mint_date

    def _calculate_valid_volume(self, ohlcv_data):
        valid_volume = 0
        for i, candle in enumerate(ohlcv_data):
            if i == 0 or candle['price_change_percent'] == 0:
                continue
            valid_volume += candle['volume']
        return valid_volume
