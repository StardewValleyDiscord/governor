# Functions related to Discord server events (not API events)

import discord, db, requests, os, shutil
from config import ADMIN_ACCESS, PUZZLE_EVENTS, XP_PER_LVL, CURRENT_EVENTS, VERIFY_EVENTS
from tracker import Tracker

async def award_event_prize(reaction, reactor, tr, us):
    # Only give reward if giver is an admin, and correct emoji was used
    # Can't use requires_admin wrapper as there is no message object from the event
    check_roles = [x.id for x in reactor.roles]
    if ADMIN_ACCESS in check_roles:
        emoji_name = reaction.emoji if type(reaction.emoji) == str else reaction.emoji.name
        for event in CURRENT_EVENTS:
            if emoji_name == event['emoji_name']:
                # Need to check if we are reacting to an archived post by ourselves
                if reaction.message.author == us and len(reaction.message.mentions) == 1:
                    author = reaction.message.mentions[0]
                    channel = reaction.message.channel_mentions[0].id
                else:
                    author = reaction.message.author
                    channel = reaction.message.channel.id

                # Award three levels
                await tr.give_xp(author, 3 * XP_PER_LVL)
                user_roles = author.roles
                for role in event['ids']:
                    new_role = discord.utils.get(author.guild.roles, id=role)
                    if new_role != None and new_role not in user_roles:
                        user_roles.append(new_role)

                await author.edit(roles=user_roles)
                if db.add_raffle(author.id, channel):
                    # Add our own emoji, so we can show that it went through
                    emoji = discord.utils.get(author.guild.emojis, name=emoji_name)
                    await reaction.message.add_reaction(emoji)

                break

async def event_check(message):
    await _check_hidden_task(message)

async def _check_hidden_task(message):
    # For events where other members shouldn't see entries we need to:
    # - Do basic checking to see if this is valid entry
    # - Delete their post in chat
    # - Ping them with a thumbs up, showing their entry was received
    # - Repost into hidden channel for staff member to approve later

    # If this isn't a valid event channel, leave
    if message.channel.id not in PUZZLE_EVENTS:
        return

    # Limit to image/videos
    files = [await a.to_file() for a in message.attachments if a.height != None]

    if files:
        validation_channel = discord.utils.get(message.guild.text_channels, id=VERIFY_EVENTS)
        if validation_channel is not None:
            await validation_channel.send(f"Entry from <@{message.author.id}> in <#{message.channel.id}>", files=files)
            await message.channel.send(f"<@{message.author.id}> :thumbsup:")

    # Valid entry or not, we want to delete it
    await message.delete()
