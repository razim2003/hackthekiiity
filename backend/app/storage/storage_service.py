import os
import uuid
from typing import Optional
from supabase import Client
from app.database.connection import supabase

BUCKET_NAME = "pet-pics"

class StorageService:
    def __init__(self):
        self.supabase = supabase
        self.bucket_name = BUCKET_NAME
    
    def upload_image(self, file_data: bytes, file_name: str, content_type: str) -> Optional[str]:
        """
        Upload image to Supabase Storage and return public URL
        """
        try:
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}_{file_name}"
            
            # Upload to Supabase Storage
            self.supabase.storage.from_(self.bucket_name).upload(
                path=unique_filename,
                file=file_data,
                file_options={"content-type": content_type}
            )
            
            # Get public URL
            public_url = f"{self.supabase.storage.from_(self.bucket_name).get_public_url(unique_filename)}"
            
            return public_url
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None
    
    def delete_image(self, file_path: str) -> bool:
        """
        Delete image from Supabase Storage
        """
        try:
            self.supabase.storage.from_(self.bucket_name).remove([file_path])
            return True
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False

storage_service = StorageService()
