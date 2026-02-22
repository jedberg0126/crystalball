def update_market(market, new_probability):
    market.last_probability = market.current_probability
    market.current_probability = new_probability
    market.updated_at = datetime.utcnow()
