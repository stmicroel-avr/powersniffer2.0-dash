from pymongo import ASCENDING
from pymongo.asynchronous.database import AsyncDatabase

from powersniffer.web.dto import MeasurementParams


async def find_measurements(db: AsyncDatabase, unit: str, params: MeasurementParams):
    """ Get measurements """
    query = {
        "timestamp": {
            "$gte": params.date_from,
            **({"$lte": params.date_to} if params.date_to is not None else {})
        }
    }

    cursor = (db[f'measurements_{unit}']
              .find(query)
              .sort("timestamp", ASCENDING)
              .limit(1000)
              )

    return await cursor.to_list()