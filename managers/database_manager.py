import mysql.connector as mysql

from utilities import logger


def get_db():
    return mysql.connect(host='HOST_HERE',
                         database='DATABASE_HERE',
                         user='USER_HERE',
                         password='PASSWORD_HERE')


async def connect():
    logger.log("Connecting to mysql database...")

    try:
        db = get_db()
        cursor = db.cursor()

        # Create table
        cursor.execute('''CREATE TABLE IF NOT EXISTS suggestions (
                            message_id BIGINT PRIMARY KEY,
                            user_id BIGINT,
                            suggestion VARCHAR(255)
                        )''')

        db.commit()
        cursor.close()
        db.close()

        logger.connection(f'Successfully connected to {db.get_server_info()}')
    except Exception as err:  # noqa
        logger.critical(err)
