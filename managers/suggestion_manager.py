import discord

import program
from managers import database_manager
from utilities import logger


def get_submission_count(user_id):
    db = database_manager.get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM suggestions WHERE user_id = %s", (user_id,))
    retval = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return retval


def set_pending(user_id, message_id, suggestion):
    db = database_manager.get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO suggestions(user_id, message_id, suggestion) VALUES (%s, %s, %s)",
        (user_id, message_id, suggestion)
    )

    db.commit()
    cursor.close()
    db.close()


def get_data(column_name, message_id):
    db = database_manager.get_db()
    cursor = db.cursor()

    cursor.execute(f"SELECT {column_name} FROM suggestions WHERE message_id = %s", (message_id,))
    retval = cursor.fetchone()

    db.commit()
    cursor.close()
    db.close()
    return retval[0]


def remove_pending(message_id):
    db = database_manager.get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM suggestions WHERE message_id = %s", (message_id,))

    db.commit()
    cursor.close()
    db.close()


async def send_suggestion(user, channel, suggestion):
    try:  # Send suggestion message
        embed = discord.Embed(title="SUGGESTION! :bulb:",
                              description=suggestion,
                              colour=program.colour)
        embed.set_footer(text=f"{user.global_name}", icon_url=user.avatar)

        message = await channel.send(embed=embed)
        await message.add_reaction('👍')
        await message.add_reaction('👎')
    except AttributeError:
        logger.critical(f"Failed to send a message, does the channel still exist?")
