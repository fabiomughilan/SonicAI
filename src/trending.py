import requests
def get_trending_crypto_topics():
    """
    Fetches trending crypto topics from a public API.
    """
    try:
        response = requests.get("https://api.coingecko.com/api/v3/search/trending")
        data = response.json()
        trending_topics = [coin['item']['name'] for coin in data['coins']]
        return trending_topics
    except Exception as e:
        print(f"Error fetching trending topics: {e}")
        return ["Sonic", "Ethereum", "DeFi", "NFT", "Bitcoin",'DWFlabs']