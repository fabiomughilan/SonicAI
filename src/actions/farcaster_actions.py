import time, threading
from src.action_handler import register_action
from src.helpers import print_h_bar
from src.prompts import POST_CAST_PROMPT
from src.prompts import REPLY_CAST_PROMPT
import random
import time
from src.prompts import MEME_PROMPT
from src.image_generator import generate_meme_image
from src.trending import get_trending_crypto_topics

@register_action("post-cast")
def post_cast(agent, **kwargs):
    current_time = time.time()
    last_cast_time = agent.state.get("last_cast_time", 0)

    if current_time - last_cast_time >= agent.cast_interval:
        agent.logger.info("\n📝 GENERATING NEW CAST")
        print_h_bar()

        prompt = POST_CAST_PROMPT.format(agent_name=agent.name)
        cast_text = agent.prompt_llm(prompt)

        if not cast_text:
            agent.logger.error("❌ Failed to generate cast text!")
            return False

        agent.logger.info(f"\n🚀 Posting cast: '{cast_text}'")
        response = agent.connection_manager.perform_action(
            connection_name="farcaster",
            action_name="post-cast",
            params=[cast_text]
        )

        if isinstance(response, dict) and response.get("success"):
            agent.state["last_cast_time"] = current_time
            agent.logger.info("\n✅ Cast posted successfully!")
            return True
        else:
            agent.logger.error(f"❌ Failed to post cast: {response}")
            return False
    else:
        agent.logger.info("\n👀 Waiting for cast interval...")
        return False

@register_action("reply-to-cast")
def reply_to_cast(agent, **kwargs):
    if "timeline_casts" in agent.state and agent.state["timeline_casts"] is not None and len(agent.state["timeline_casts"]) > 0:
        cast = agent.state["timeline_casts"].pop(0)
        if not isinstance(cast, dict):
            agent.logger.error(f"❌ Unexpected cast format: {cast}")
            return False

        cast_id = cast.get('id')

        agent.logger.info(f"\n💬 GENERATING REPLY to: {cast.get('text', '')[:50]}...")

        base_prompt = REPLY_CAST_PROMPT.format(cast_text=cast.get('text'))
        system_prompt = agent._construct_system_prompt()
        reply_text = agent.prompt_llm(prompt=base_prompt, system_prompt=system_prompt)

        if reply_text:
            agent.logger.info(f"\n🚀 Posting reply: '{reply_text}'")
            agent.connection_manager.perform_action(
                connection_name="farcaster",
                action_name="reply-to-cast",
                params=[cast_id, reply_text]
            )
            agent.logger.info("✅ Reply posted successfully!")
            return True
    else:
        agent.logger.info("\n👀 No casts found to reply to...")
        return False

@register_action("like-cast")
def like_cast(agent, **kwargs):
    if "timeline_casts" in agent.state and agent.state["timeline_casts"] is not None and len(agent.state["timeline_casts"]) > 0:
        cast = agent.state["timeline_casts"].pop(0)
        cast_id = cast.get('id')
        if not cast_id:
            return False
        
        is_own_cast = cast.get('author_username', '').lower() == agent.username
        if is_own_cast:
            replies = agent.connection_manager.perform_action(
                connection_name="farcaster",
                action_name="get-cast-replies",
                params=[cast.get('author_id')]
            )
            if replies:
                agent.state["timeline_casts"].extend(replies[:agent.own_cast_replies_count])
            return True 

        agent.logger.info(f"\n👍 LIKING CAST: {cast.get('text', '')[:50]}...")

        agent.connection_manager.perform_action(
            connection_name="farcaster",
            action_name="like-cast",
            params=[cast_id]
        )
        agent.logger.info("✅ Cast liked successfully!")
        return True
    else:
        agent.logger.info("\n👀 No casts found to like...")
    return False



@register_action("post-meme")
def post_meme(agent, **kwargs):
    """
    Generates a viral meme based on crypto trends and posts it to Farcaster.
    """
    current_time = time.time()
    last_meme_time = agent.state.get("last_meme_time", 0)
    
    if current_time - last_meme_time >= agent.meme_interval:
        agent.logger.info("\n😂 GENERATING NEW MEME")
        print_h_bar()

        # Fetch trending crypto topics
        trending_topics = get_trending_crypto_topics()
        topic = random.choice(trending_topics) if trending_topics else "crypto"

        # Generate meme text
        prompt = MEME_PROMPT.format(agent_name=agent.name, topic=topic)
        meme_text = agent.prompt_llm(prompt)
        
        # Generate meme image
        meme_image_url = generate_meme_image(meme_text)
        
        if meme_text and meme_image_url:
            agent.logger.info("\n🚀 Posting meme:")
            agent.logger.info(f"'{meme_text}' with image: {meme_image_url}")
            
            agent.connection_manager.perform_action(
                connection_name="farcaster",
                action_name="post-cast",
                params=[f"{meme_text} {meme_image_url}"]
            )
            
            agent.state["last_meme_time"] = current_time
            agent.logger.info("\n✅ Meme posted successfully!")
            return True
    else:
        agent.logger.info("\n👀 Waiting before posting another meme...")
        return False

@register_action("respond-to-mentions")
def respond_to_mentions(agent, **kwargs):
    filter_str = f"@{agent.username} -is:retweet"
    stream_function = agent.connection_manager.perform_action(
        connection_name="farcaster",
        action_name="stream-casts",
        params=[filter_str]
    )
    def process_casts():
        for cast_data in stream_function:
            cast_id = cast_data["id"]
            cast_text = cast_data["text"]
            agent.logger.info(f"Received a mention: {cast_text}")

    processing_thread = threading.Thread(target=process_casts)
    processing_thread.daemon = True
    processing_thread.start()
