from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from PIL import Image
import io
from app.database.connection import supabase
from app.storage.storage_service import storage_service
from app.ai.embedding_service import embedding_service
from app.models.cat import CatCreate, CatResponse, SimilarCatResponse
import uuid

router = APIRouter()

@router.post("/upload")
async def upload_cat(
    image: UploadFile = File(...),
    status: str = Form(...),
    location: str = Form(...),
    description: str = Form(...)
):
    """
    Upload a cat image with metadata
    """
    try:
        # Read image file
        image_data = await image.read()
        
        # Validate image
        try:
            img = Image.open(io.BytesIO(image_data))
            img = img.convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Upload to Supabase Storage
        content_type = image.content_type or "image/jpeg"
        image_url = storage_service.upload_image(image_data, image.filename, content_type)
        
        if not image_url:
            raise HTTPException(status_code=500, detail="Failed to upload image")
        
        # Generate CLIP embedding
        embedding = embedding_service.generate_embedding(img)
        
        if not embedding:
            raise HTTPException(status_code=500, detail="Failed to generate embedding")
        
        # Save to database
        cat_id = str(uuid.uuid4())
        cat_data = {
            "id": cat_id,
            "status": status,
            "location": location,
            "description": description,
            "image_url": image_url,
            "embedding": embedding
        }
        
        result = supabase.table("cats").insert(cat_data).execute()
        
        return {
            "id": cat_id,
            "image_url": image_url,
            "message": "Cat uploaded successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading cat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("", response_model=List[CatResponse])
async def get_all_cats():
    """
    Get all uploaded cats
    """
    try:
        result = supabase.table("cats").select("*").order("created_at", desc=True).execute()
        return result.data
    except Exception as e:
        print(f"Error fetching cats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch cats")

@router.get("/{cat_id}", response_model=CatResponse)
async def get_cat(cat_id: str):
    """
    Get a single cat by ID
    """
    try:
        result = supabase.table("cats").select("*").eq("id", cat_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Cat not found")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching cat: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch cat")

@router.get("/similar/{cat_id}", response_model=List[SimilarCatResponse])
async def get_similar_cats(cat_id: str):
    """
    Find visually similar cats using CLIP embeddings
    Returns top 5 most similar cats
    """
    try:
        # Get target cat
        target_result = supabase.table("cats").select("*").eq("id", cat_id).execute()
        
        if not target_result.data:
            raise HTTPException(status_code=404, detail="Cat not found")
        
        target_cat = target_result.data[0]
        target_embedding = target_cat["embedding"]
        
        # Get all other cats
        all_cats_result = supabase.table("cats").select("*").neq("id", cat_id).execute()
        other_cats = all_cats_result.data
        
        # Calculate similarities
        similarities = []
        for cat in other_cats:
            similarity_score = embedding_service.compare_embeddings(
                target_embedding, 
                cat["embedding"]
            )
            
            similarities.append({
                "cat_id": cat["id"],
                "image_url": cat["image_url"],
                "similarity_score": similarity_score
            })
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Return top 5
        return similarities[:5]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error finding similar cats: {e}")
        raise HTTPException(status_code=500, detail="Failed to find similar cats")
