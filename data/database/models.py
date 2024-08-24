from sqlalchemy import BigInteger, String, ForeignKey, Text, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from datetime import datetime
from config import TIME_ZONE


engine = create_async_engine(url='sqlite+aiosqlite:///data/database/db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    ...


class User(Base):
    __tablename__ = 'Users'

    id = mapped_column(BigInteger, primary_key=True, autoincrement=False, unique=True)
    firstname: Mapped[str] = mapped_column(String(128), unique=False, nullable=True)
    lastname: Mapped[str] = mapped_column(String(128), unique=False, nullable=True)

    free_requests: Mapped[int] = mapped_column(Integer(), nullable=True, default=5)

    balance: Mapped[str] = mapped_column(String(1024), default='0.0')
    referral_balance: Mapped[str] = mapped_column(String(1024), default='0.0')
    last_invoice: Mapped[str] = mapped_column(String(1024), default='0.0')
    subscription_end_date: Mapped[str] = mapped_column(String(128), nullable=True)
    has_subscription: Mapped[bool] = mapped_column(Boolean, default=False)
    
    first_promt: Mapped[str] = mapped_column(Text(2048), unique=False)
    second_promt: Mapped[str] = mapped_column(Text(2048), unique=False)

    referral_user: Mapped[str] = mapped_column(BigInteger, unique=False, nullable=True, default=0)
    referral_count: Mapped[str] = mapped_column(Integer(), default=0)

    dialog_titles: Mapped[str] = mapped_column(String(1024), default='Диалог 1, ')
    dialogue_models: Mapped[str] = mapped_column(String(512), default='gpt-4o, ')

    current_dialog_index: Mapped[int] = mapped_column(Integer(), nullable=True, default=None)

    message_history: Mapped[str] = mapped_column(Text, nullable=True, default="{}")

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def reset_free_requests():
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                update(User).values(free_requests=5)
            )
            await session.commit()
        print(f"free_requests были обновлены в {datetime.now()}")

scheduler = AsyncIOScheduler()
scheduler.add_job(reset_free_requests, 'cron', hour=0, minute=0, timezone=TIME_ZONE)
