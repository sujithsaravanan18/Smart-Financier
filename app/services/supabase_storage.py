import os
from supabase import create_client, Client
import uuid

class SupabaseStorageClient:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if url and key:
            self.client: Client = create_client(url, key)
            self.bucket_name = "profile-photos"
        else:
            self.client = None

    def upload_profile_photo(self, file_path, original_filename):
        if not self.client:
            return None
            
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
        filename = f"{uuid.uuid4()}.{ext}"
        
        with open(file_path, 'rb') as f:
            res = self.client.storage.from_(self.bucket_name).upload(
                file=f,
                path=filename,
                file_options={"content-type": f"image/{ext}"}
            )
            
        public_url = self.client.storage.from_(self.bucket_name).get_public_url(filename)
        return public_url
