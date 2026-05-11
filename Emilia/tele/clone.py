# ============================================
# FIXED BROADCAST FUNCTION - Works on both main bot and cloned bots
# ============================================
# Yeh file clone.py me broadcast function ko replace karne ke liye hai
# Copy the code below and paste it in your Emilia/tele/clone.py file

# ALSO UPDATE THESE IMPORTS at the top of clone.py:
# from telethon import TelegramClient, errors
# (already present, no change needed)


@register(pattern="broadcast")
async def broadcast(event):
    """Broadcast a replied message to all users and/or chats.
    
    Usage: Reply to any message with /broadcast -all / -users / -chats
    """
    # Check if user is authorized (Owner for main bot, Clone owner for cloned bots)
    is_clone = getattr(event.client, "is_clone", False)
    
    if is_clone:
        # For cloned bots - check if sender is the clone owner
        me = await event.client.get_me()
        bot_id = me.id
        clone_info = await get_clone_info_by_bot_id(bot_id)
        
        if not clone_info or event.sender_id != clone_info["_id"]:
            return await event.reply("You are not authorized to use this command.")
    else:
        # For main bot - only OWNER can broadcast
        if event.sender_id != OWNER_ID:
            return await event.reply("You are not authorized to use this command. Only the bot owner can broadcast.")
    
    if not event.reply_to_msg_id:
        return await event.reply("Please reply to a message to broadcast it!")
    
    # Get bot_id for database queries
    me = await event.client.get_me()
    bot_id = me.id
    
    # Check if this is main bot or cloned bot
    is_main_bot = not is_clone
    
    args = event.text.split(None, 1)
    if len(args) < 2 or args[1].lower() not in ["-all", "-users", "-chats"]:
        # For main bot: count all users/chats
        # For cloned bots: count only users/chats with bot_ids
        if is_main_bot:
            user_count = await db.users.count_documents({})
            chat_count = await db.chats.count_documents({})
        else:
            user_count = await db.users.count_documents({"bot_ids": bot_id})
            chat_count = await db.chats.count_documents({"bot_ids": bot_id})
        return await event.reply(
            f"Please provide a mode: `/broadcast -all`, `/broadcast -users`, or `/broadcast -chats`\n\n"
            f"**Users**: {user_count}\n"
            f"**Chats**: {chat_count}"
        )
    
    mode = args[1].lower()
    reply = await event.get_reply_message()
    wait = await event.reply("Starting broadcast...")
    
    try:
        if mode == "-all":
            us, uf = await broadcast_to_users(bot_id, reply, event.client, is_main_bot, wait)
            cs, cf = await broadcast_to_chats(bot_id, reply, event.client, is_main_bot, wait)
            await wait.edit(
                f"**Broadcast Complete**\n\n"
                f"Users: {us} success, {uf} failed\n"
                f"Chats: {cs} success, {cf} failed"
            )
        elif mode == "-users":
            s, f = await broadcast_to_users(bot_id, reply, event.client, is_main_bot, wait)
            await wait.edit(f"**User Broadcast Complete**\n\nUsers: {s} success, {f} failed")
        else:
            s, f = await broadcast_to_chats(bot_id, reply, event.client, is_main_bot, wait)
            await wait.edit(f"**Chat Broadcast Complete**\n\nChats: {s} success, {f} failed")
    except Exception as e:
        LOGGER.error(f"Broadcast error: {e}", exc_info=True)
        await wait.edit(f"Broadcast failed: {str(e)}")


async def broadcast_to_users(bot_id, message, client, is_main_bot=False, progress_msg=None):
    """Broadcast message to all users with proper error handling and retry logic.
    
    Args:
        bot_id: Bot ID for filtering cloned bot users
        message: Telethon Message object to broadcast
        client: Telethon client instance
        is_main_bot: Whether this is the main bot or a clone
        progress_msg: Optional message object to edit with progress updates
    
    Returns:
        tuple: (success_count, failed_count)
    """
    # For main bot: get ALL users
    # For cloned bots: get only users with this bot_id in bot_ids
    if is_main_bot:
        cursor = db.users.find({}, {"user_id": 1, "username": 1})
    else:
        cursor = db.users.find({"bot_ids": bot_id}, {"user_id": 1, "username": 1})
    
    success, failed = 0, 0
    total = 0
    flood_wait_count = 0
    
    # First count total for progress tracking
    if progress_msg:
        total = await cursor.clone().to_list(length=1)
        total = await db.users.count_documents({} if is_main_bot else {"bot_ids": bot_id})
    
    processed = 0
    last_progress_update = 0
    
    async for doc in cursor:
        processed += 1
        
        # Validate document - skip if user_id field is missing or invalid
        uid = doc.get("user_id")
        if not uid or not isinstance(uid, int):
            LOGGER.warning(f"Skipping user document with missing/invalid user_id: {doc.get('_id')}")
            failed += 1
            continue
        
        # Send message with retry logic
        sent = await _send_with_retry(client, uid, message, is_main_bot, bot_id, "user")
        if sent:
            success += 1
        else:
            failed += 1
        
        # Progress update every 50 users
        if progress_msg and total > 0 and (processed - last_progress_update) >= 50:
            try:
                await progress_msg.edit(
                    f"Broadcasting to users... {processed}/{total}\n"
                    f"Success: {success} | Failed: {failed}"
                )
                last_progress_update = processed
            except Exception:
                pass  # Ignore progress update errors
        
        # Sleep to avoid flood wait - 0.1s base delay
        await asyncio.sleep(0.1)
    
    LOGGER.info(f"User broadcast complete: {success} success, {failed} failed, {processed} total")
    return success, failed


async def broadcast_to_chats(bot_id, message, client, is_main_bot=False, progress_msg=None):
    """Broadcast message to all chats with proper error handling and retry logic.
    
    Args:
        bot_id: Bot ID for filtering cloned bot chats
        message: Telethon Message object to broadcast
        client: Telethon client instance
        is_main_bot: Whether this is the main bot or a clone
        progress_msg: Optional message object to edit with progress updates
    
    Returns:
        tuple: (success_count, failed_count)
    """
    # For main bot: get ALL chats
    # For cloned bots: get only chats with this bot_id in bot_ids
    if is_main_bot:
        cursor = db.chats.find({}, {"chat_id": 1, "chat_title": 1})
    else:
        cursor = db.chats.find({"bot_ids": bot_id}, {"chat_id": 1, "chat_title": 1})
    
    success, failed = 0, 0
    total = 0
    
    # First count total for progress tracking
    if progress_msg:
        total = await db.chats.count_documents({} if is_main_bot else {"bot_ids": bot_id})
    
    processed = 0
    last_progress_update = 0
    
    async for doc in cursor:
        processed += 1
        
        # Validate document - skip if chat_id field is missing or invalid
        cid = doc.get("chat_id")
        if not cid or not isinstance(cid, int):
            LOGGER.warning(f"Skipping chat document with missing/invalid chat_id: {doc.get('_id')}")
            failed += 1
            continue
        
        # Send message with retry logic
        sent = await _send_with_retry(client, cid, message, is_main_bot, bot_id, "chat")
        if sent:
            success += 1
        else:
            failed += 1
        
        # Progress update every 50 chats
        if progress_msg and total > 0 and (processed - last_progress_update) >= 50:
            try:
                await progress_msg.edit(
                    f"Broadcasting to chats... {processed}/{total}\n"
                    f"Success: {success} | Failed: {failed}"
                )
                last_progress_update = processed
            except Exception:
                pass  # Ignore progress update errors
        
        # Sleep to avoid flood wait - 0.1s base delay (slightly higher for groups)
        await asyncio.sleep(0.15)
    
    LOGGER.info(f"Chat broadcast complete: {success} success, {failed} failed, {processed} total")
    return success, failed


async def _send_with_retry(client, entity, message, is_main_bot, bot_id, entity_type, max_retries=2):
    """Send/forward message to an entity with retry logic.
    
    Args:
        client: Telethon client
        entity: User ID or Chat ID
        message: Message to forward
        is_main_bot: Whether main bot or clone
        bot_id: Bot ID for cleanup
        entity_type: 'user' or 'chat'
        max_retries: Maximum retry attempts for flood wait
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    retries = 0
    
    while retries <= max_retries:
        try:
            await client.forward_messages(entity, message)
            return True
            
        except errors.FloodWaitError as e:
            wait_time = min(e.seconds, 120)  # Cap at 2 minutes
            LOGGER.warning(
                f"FloodWaitError for {entity_type} {entity}: "
                f"waiting {wait_time}s (retry {retries+1}/{max_retries})"
            )
            await asyncio.sleep(wait_time)
            retries += 1
            
        except errors.UserIsBlockedError:
            LOGGER.info(f"User {entity} has blocked the bot")
            if not is_main_bot and entity_type == "user":
                try:
                    await db.users.update_one(
                        {"user_id": entity}, 
                        {"$pull": {"bot_ids": bot_id}}
                    )
                except Exception as cleanup_err:
                    LOGGER.error(f"Failed to cleanup blocked user {entity}: {cleanup_err}")
            return False
            
        except (errors.ChatWriteForbiddenError, errors.UserNotParticipantError) as e:
            LOGGER.info(f"Cannot write to chat {entity}: {type(e).__name__}")
            if not is_main_bot and entity_type == "chat":
                try:
                    await db.chats.update_one(
                        {"chat_id": entity}, 
                        {"$pull": {"bot_ids": bot_id}}
                    )
                except Exception as cleanup_err:
                    LOGGER.error(f"Failed to cleanup inaccessible chat {entity}: {cleanup_err}")
            return False
            
        except errors.PeerIdInvalidError:
            LOGGER.warning(f"Invalid peer ID: {entity}")
            return False
            
        except errors.InputUserDeactivatedError:
            LOGGER.info(f"User {entity} account is deactivated")
            return False
            
        except errors.ChannelPrivateError:
            LOGGER.info(f"Chat {entity} is private and bot is not a member")
            return False
            
        except errors.MessageTooLongError:
            LOGGER.warning(f"Message too long for {entity_type} {entity}")
            return False
            
        except Exception as e:
            LOGGER.error(
                f"Unexpected error sending to {entity_type} {entity}: "
                f"{type(e).__name__}: {e}"
            )
            return False
    
    # Max retries exceeded (only for FloodWaitError)
    LOGGER.warning(f"Max retries exceeded for {entity_type} {entity}")
    return False
