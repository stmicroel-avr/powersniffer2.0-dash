from pymongo.asynchronous.database import AsyncDatabase

from powersniffer.web.dto import MeasurementQueryParams


async def get_measurements(db: AsyncDatabase, query: MeasurementQueryParams):
    """ Get measurements """
    return await db.measurements_vcc.find().to_list(None)