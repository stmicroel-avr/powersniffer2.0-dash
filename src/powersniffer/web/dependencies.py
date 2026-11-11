from fastapi import Request
from pymongo.asynchronous.database import AsyncDatabase


def get_db(request: Request) -> AsyncDatabase:
    """ Get database connection """
    return request.app.state.db