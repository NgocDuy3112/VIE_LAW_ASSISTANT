import asyncpg
import asyncio


class AsyncPostgresDatabase:
    def __init__(
        self,
        dbname: str | None = None,
        host: str = 'postgresql',
        user: str = 'user',
        password: str = 'password',
        port: int = 5432,
        echo: bool = True
    ):
        self.user = user
        self.password = password
        self.dbname = dbname
        self.host = host
        self.port = port
        self.conn: asyncpg.Connection | None = None
        self.echo = echo

    async def connect(self, retries: int = 10, delay: float = 1.0):
        for attempt in range(1, retries + 1):
            try:
                self.conn = await asyncpg.connect(
                    user=self.user,
                    password=self.password,
                    database=self.dbname if self.dbname else "postgres",
                    host=self.host,
                    port=self.port
                )
                if self.echo:
                    print("✅ Connected to PostgreSQL")
                return
            except Exception as e:
                if self.echo:
                    print(f"⏳ Attempt {attempt}/{retries} failed: {e}")
                await asyncio.sleep(delay * (2 ** (attempt - 1)))

        raise RuntimeError("❌ PostgreSQL connection failed after multiple attempts")

    async def is_connected(self) -> bool:
        if self.conn is None:
            return False
        try:
            await self.conn.execute("SELECT 1")
            return True
        except Exception as e:
            if self.echo:
                print(f"🔌 Connection check failed: {e}")
            return False

    async def execute(self, query: str):
        if not self.conn:
            if self.echo:
                print("⚠️ No active database connection.")
            return
        try:
            await self.conn.execute(query)
        except Exception as e:
            if self.echo:
                print(f"⚠️ Query execution error: {e}")

    async def close(self):
        if self.conn:
            try:
                await self.conn.close()
                if self.echo:
                    print("🔒 PostgreSQL connection closed.")
            except Exception as e:
                if self.echo:
                    print(f"⚠️ Error while closing connection: {e}")

    def get_connection_string(self) -> str:
        db_part = f"/{self.dbname}" if self.dbname else ""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}{db_part}"