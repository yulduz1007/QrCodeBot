from typing import Optional

from sqlalchemy import create_engine, func, DateTime, String, insert
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import DeclarativeBase, declared_attr, Session
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

engine = create_engine("postgresql+psycopg2://postgres:1@localhost:5432/qr_codedb")

session = Session(bind=engine)


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower() + 's'


class AbstractTime(Base):
    __abstract__ = True
    created_at: Mapped[DATETIME] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now())
    join_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


class QrCode(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[Optional[str]]


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(index=True)

    def __repr__(self) -> str:
        return (f"User(id={self.id!r},"
                f" is_active={self.is_active!r}")

    def insert(self):
        d = self.__dict__
        del d['cols']
        table_name = self.__class__.__name__.lower() + "s"
        keys = [k for k, v in d.items() if v is not None]
        col_names = " , ".join(keys)
        format = " , ".join(["%s"] * len(keys))
        params = [v for v in d.values() if v is not None]
        query = f"""
            insert into {table_name} ({col_names}) values ({format})
        """

        self.cur.execute(query, params)
        self.con.commit()

Base.metadata.create_all(engine)
