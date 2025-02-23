import random
import time
from src.action_handler import register_action
from src.image_generator import generate_meme_image
from src.trending import get_trending_crypto_topics

@register_action("post-meme")
def post_meme(agent, **kwargs):
    current_time = time.time()

    # Ensure last meme time is stored in agent state
    last_meme_time = agent.state.get("last_meme_time", 0)

    # Ensure agent has a meme interval (default to 1 hour)
    meme_interval = getattr(agent, "meme_interval", 3600)

    if current_time - last_meme_time >= meme_interval:
        agent.logger.info("\n🖼 GENERATING MEME CONTENT")

        trending_topics = get_trending_crypto_topics()
        topic = random.choice(trending_topics) if trending_topics else "crypto"
        meme_text = f"When {topic} goes to the moon! 🚀"

        meme_path = generate_meme_image(meme_text)
        if meme_path:
            agent.logger.info("\n🚀 Posting meme:")
            agent.logger.info(f"Meme Path: {meme_path}")
            agent.connection_manager.perform_action(
                connection_name="farcaster",
                action_name="post-image",
                params=[meme_path, meme_text]
            )
            agent.state["last_meme_time"] = current_time
            agent.logger.info("\n✅ Meme posted successfully!")
            return True
    else:
        agent.logger.info(f"\n👀 Delaying meme post. Next meme in {int(meme_interval - (current_time - last_meme_time))} seconds.")
        return False
