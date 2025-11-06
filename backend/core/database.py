from supabase import create_client, Client
from functools import lru_cache
from config import settings

@lru_cache
def get_supabase_client() -> Client:
    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_service_key
    )

@lru_cache
def get_supabase_anon_client() -> Client:
    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_anon_key
    )

class Database:
    def __init__(self):
        self.client = get_supabase_client()
    
    async def execute_query(self, table: str, query_type: str, **kwargs):
        try:
            if query_type == "select":
                return self.client.table(table).select(kwargs.get("columns", "*")).execute()
            elif query_type == "insert":
                return self.client.table(table).insert(kwargs.get("data")).execute()
            elif query_type == "update":
                return self.client.table(table).update(kwargs.get("data")).eq(
                    kwargs.get("match_column"), kwargs.get("match_value")
                ).execute()
            elif query_type == "delete":
                return self.client.table(table).delete().eq(
                    kwargs.get("match_column"), kwargs.get("match_value")
                ).execute()
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")
    
    async def get_by_id(self, table: str, id_value: str, id_column: str = "id"):
        result = self.client.table(table).select("*").eq(id_column, id_value).execute()
        return result.data[0] if result.data else None
    
    async def get_all(self, table: str, filters: dict = None, limit: int = 100):
        query = self.client.table(table).select("*")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        return query.limit(limit).execute()
    
    async def create(self, table: str, data: dict):
        return self.client.table(table).insert(data).execute()
    
    async def update_by_id(self, table: str, id_value: str, data: dict, id_column: str = "id"):
        return self.client.table(table).update(data).eq(id_column, id_value).execute()
    
    async def delete_by_id(self, table: str, id_value: str, id_column: str = "id"):
        return self.client.table(table).delete().eq(id_column, id_value).execute()

def get_database() -> Database:
    return Database()



