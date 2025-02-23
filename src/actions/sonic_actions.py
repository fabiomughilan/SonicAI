import logging
import os
from dotenv import load_dotenv
from src.action_handler import register_action

logger = logging.getLogger("actions.sonic_actions")

@register_action("get-token-by-ticker")
def get_token_by_ticker(agent, **kwargs):
    """Get token address by ticker symbol"""
    try:
        ticker = kwargs.get("ticker")
        if not ticker:
            logger.error("No ticker provided")
            return {"error": "No ticker provided"}

        return agent.connection_manager.connections["sonic"].get_token_by_ticker(ticker)

    except Exception as e:
        logger.exception("Failed to get token by ticker")
        return {"error": str(e)}

@register_action("get-sonic-balance")
def get_sonic_balance(agent, **kwargs):
    """Get $S or token balance."""
    try:
        address = kwargs.get("address")
        token_address = kwargs.get("token_address")

        if not address:
            load_dotenv()
            private_key = os.getenv('SONIC_PRIVATE_KEY')
            if not private_key:
                logger.error("SONIC_PRIVATE_KEY not set in environment")
                return {"error": "SONIC_PRIVATE_KEY missing"}

            web3 = agent.connection_manager.connections["sonic"]._web3
            account = web3.eth.account.from_key(private_key)
            address = account.address

        return agent.connection_manager.connections["sonic"].get_balance(
            address=address,
            token_address=token_address
        )

    except Exception as e:
        logger.exception("Failed to get balance")
        return {"error": str(e)}

@register_action("send-sonic")
def send_sonic(agent, **kwargs):
    """Send $S tokens to an address."""
    try:
        to_address = kwargs.get("to_address")
        amount = kwargs.get("amount")

        if not to_address or not amount:
            logger.error("Missing required parameters: to_address or amount")
            return {"error": "Missing to_address or amount"}

        return agent.connection_manager.connections["sonic"].transfer(
            to_address=to_address,
            amount=float(amount)
        )

    except Exception as e:
        logger.exception("Failed to send $S")
        return {"error": str(e)}

@register_action("send-sonic-token")
def send_sonic_token(agent, **kwargs):
    """Send tokens on Sonic chain."""
    try:
        to_address = kwargs.get("to_address")
        token_address = kwargs.get("token_address")
        amount = kwargs.get("amount")

        if not to_address or not token_address or not amount:
            logger.error("Missing required parameters: to_address, token_address, or amount")
            return {"error": "Missing required parameters"}

        return agent.connection_manager.connections["sonic"].transfer(
            to_address=to_address,
            amount=float(amount),
            token_address=token_address
        )

    except Exception as e:
        logger.exception("Failed to send tokens")
        return {"error": str(e)}

@register_action("swap-sonic")
def swap_sonic(agent, **kwargs):
    """Swap tokens on Sonic chain."""
    try:
        token_in = kwargs.get("token_in")
        token_out = kwargs.get("token_out")
        amount = kwargs.get("amount")
        slippage = kwargs.get("slippage", 0.5)

        if not token_in or not token_out or not amount:
            logger.error("Missing required parameters: token_in, token_out, or amount")
            return {"error": "Missing required parameters"}

        return agent.connection_manager.connections["sonic"].swap(
            token_in=token_in,
            token_out=token_out,
            amount=float(amount),
            slippage=float(slippage)
        )

    except Exception as e:
        logger.exception("Failed to swap tokens")
        return {"error": str(e)}

@register_action("deploy-nft")
def deploy_nft(agent, **kwargs):
    """Deploy an NFT on Sonic chain."""
    try:
        uri = kwargs.get("uri")
        name = kwargs.get("name")
        symbol = kwargs.get("symbol")

        if not uri or not name or not symbol:
            logger.error("Missing required parameters: uri, name, or symbol")
            return {"error": "Missing required parameters"}

        return agent.connection_manager.connections["sonic"].deploy_nft(
            uri=uri,
            name=name,
            symbol=symbol
        )

    except Exception as e:
        logger.exception("Failed to deploy NFT")
        return {"error": str(e)}
