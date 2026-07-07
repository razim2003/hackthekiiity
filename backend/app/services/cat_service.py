from typing import Any, Dict, List, Optional

from app.database.connection import supabase


def create_cat(cat_data: Dict[str, Any]) -> Dict[str, Any]:
    result = supabase.table("cats").insert(cat_data).execute()

    if not result.data:
        raise RuntimeError("Cat record was not created")

    return result.data[0]


def list_cats() -> List[Dict[str, Any]]:
    result = supabase.table("cats").select("*").order("created_at", desc=True).execute()
    return result.data or []


def get_cat_by_id(cat_id: str) -> Optional[Dict[str, Any]]:
    result = supabase.table("cats").select("*").eq("id", cat_id).execute()
    if not result.data:
        return None
    return result.data[0]


def list_cats_except(cat_id: str) -> List[Dict[str, Any]]:
    result = supabase.table("cats").select("*").neq("id", cat_id).execute()
    return result.data or []


def update_cat_embedding(cat_id: str, embedding: List[float]) -> None:
    supabase.table("cats").update({"embedding": embedding}).eq("id", cat_id).execute()
