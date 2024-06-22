from os import environ
from datetime import datetime, timedelta
import asyncio
import dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo
import logger
import parsers


class LogBook:
    _client: AsyncIOMotorClient
    _database: AsyncIOMotorDatabase

    def __init__(self, connection_string: str, database_name: str) -> None:
        self._client = AsyncIOMotorClient(connection_string)
        self._database = self._client[database_name]

    async def login(self, playfab_id: str, user_name: str, date: datetime) -> str:
        collection = self._database["logbook"]
        payload = {"playfab_id": playfab_id, "user_name": user_name, "login": date}
        write = await collection.insert_one(payload)
        if not write.acknowledged:
            raise ValueError(f"Could not create document for {playfab_id} at {date}")
        return str(write.inserted_id)

    async def logout(self, playfab_id: str, date: datetime) -> int:
        collection = self._database["logbook"]
        put = await collection.find_one_and_update(
            {
                "playfab_id": playfab_id,
                "login": {"$gte": date - timedelta(hours=2)},
                "logout": {"$exists": False},
            },
            {"$set": {"logout": date}},
            sort=[("login", pymongo.DESCENDING)],
        )
        if not put:
            raise ValueError(f"Failed to update session for {playfab_id} at {date}")
        login_date: datetime = put["login"]
        session_duration = date - login_date
        session_minutes = session_duration.total_seconds() / 60
        return round(session_minutes)

    def hours(self, playfab_id: str):
        pass


login_event = {
    "eventType": "Login",
    "date": "2024.06.21-23.05.13",
    "userName": "userName",
    "playfabId": "playfabId",
    "order": "out",
}
logout_event = {
    "eventType": "Login",
    "date": "2024.06.21-23.26.34",
    "userName": "userName",
    "playfabId": "playfabId",
    "order": "out",
}


async def main():
    logger.use_date_time_logger()
    dotenv.load_dotenv()
    log_book = LogBook(
        environ["DB_CONNECTION_STRING"], environ.get("DB_NAME", "mordhau")
    )
    session_id = await log_book.login(
        login_event["playfabId"],
        login_event["userName"],
        parsers.parse_date(login_event["date"]),
    )
    logger.debug(f"session id {session_id}")
    await asyncio.sleep(5)
    logout_r = await log_book.logout(
        logout_event["playfabId"], parsers.parse_date(logout_event["date"])
    )
    print(logout_r)


asyncio.run(main())
