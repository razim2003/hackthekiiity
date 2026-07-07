import uuid
from typing import Optional
from urllib.parse import unquote, urlparse

from app.config import get_settings
from app.database.connection import supabase


class StorageService:
    def __init__(self):
        self.supabase = supabase
        self.bucket_name = get_settings().supabase_storage_bucket
    
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

    def delete_image_by_url(self, image_url: str) -> bool:
        """
        Delete an uploaded image using the public URL returned by Supabase.
        """
        file_path = self._path_from_public_url(image_url)
        if not file_path:
            return False

        return self.delete_image(file_path)

    def _path_from_public_url(self, image_url: str) -> Optional[str]:
        parsed_path = urlparse(image_url).path
        bucket_marker = f"/{self.bucket_name}/"

        if bucket_marker not in parsed_path:
            return None

        return unquote(parsed_path.split(bucket_marker, 1)[1])

storage_service = StorageService()
