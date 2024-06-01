from sqlalchemy import select
from sqlalchemy.orm import load_only

from app.dependencies import logger


class DatabaseOperations:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    async def select(self, model, columns, where=None, offset=None, limit=None, order_by=None):
        async with self.db_helper() as session:
            try:

                statement = select(model).options(load_only(*columns))
                if where is not None:
                    statement = statement.where(*where)
                if order_by is not None:
                    statement = statement.order_by(order_by)
                if offset:
                    statement = statement.offset(offset)
                if limit:
                    statement = statement.limit(limit)

                result = await session.execute(statement)
                data = result.scalars().all()

                return True, data
            except Exception:
                logger.exception("select failed", exc_info=True)
        return False, {}

    async def insert(self, model, insert_data):
        async with self.db_helper() as session:
            async with session.begin():
                try:
                    instance = model(**insert_data)
                    session.add(instance)
                    return True
                except Exception:
                    logger.exception("insert failed", exc_info=True)
        return False
