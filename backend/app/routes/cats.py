from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from PIL import Image
import io
import uuid
from urllib.request import urlopen

from app.config import get_settings
from app.ai.embedding_service import embedding_service
from app.models.cat import CatResponse, SimilarCatResponse
from app.services.cat_service import (
    create_cat,
    get_cat_by_id,
    list_cats,
    list_cats_except,
    update_cat_embedding,
)
from app.storage.storage_service import storage_service

router = APIRouter()
settings = get_settings()


def ensure_embedding(cat: dict) -> List[float]:
    """
    Backfill or refresh embeddings for older rows created before CLIP matching.
    """
    existing_embedding = cat.get("embedding")
    if embedding_service.is_clip_embedding(existing_embedding):
        return existing_embedding

    if existing_embedding:
        print(
            f"[similar] regenerating legacy embedding for cat {cat.get('id')} "
            f"length: {len(existing_embedding)}"
        )

    try:
        with urlopen(cat["image_url"], timeout=10) as response:
            image_data = response.read()
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        embedding = embedding_service.generate_embedding(image)
        update_cat_embedding(cat["id"], embedding)
        cat["embedding"] = embedding
        return embedding
    except RuntimeError as exc:
        print(f"Could not generate CLIP embedding for cat {cat.get('id')}: {exc}")
        return []
    except Exception as exc:
        print(f"Could not backfill embedding for cat {cat.get('id')}: {exc}")
        return []

@router.post("/upload")
async def upload_cat(
    image: UploadFile = File(...),
    status: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    owner_name: str = Form(""),
    contact_phone: str = Form(""),
    contact_email: str = Form("")
):
    """
    Upload a cat image with metadata
    """
    try:
        if status not in settings.allowed_cat_statuses:
            raise HTTPException(status_code=400, detail="Invalid cat status")

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
        image_url = storage_service.upload_image(
            image_data,
            image.filename or "cat-image",
            content_type
        )
        
        if not image_url:
            raise HTTPException(status_code=500, detail="Failed to upload image")

        try:
            embedding = embedding_service.generate_embedding(img)
        except RuntimeError as exc:
            storage_service.delete_image_by_url(image_url)
            error_msg = str(exc)
            if "OpenCLIP" in error_msg or "unavailable" in error_msg:
                raise HTTPException(
                    status_code=503,
                    detail="Image embedding model is unavailable. Please ensure open-clip-torch and torch are installed correctly."
                ) from exc
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate embedding: {error_msg}"
            ) from exc
        
        # Save to database
        cat_id = str(uuid.uuid4())
        cat_data = {
            "id": cat_id,
            "status": status,
            "location": location,
            "description": description,
            "image_url": image_url,
            "embedding": embedding,
            "owner_name": owner_name.strip() or None,
            "contact_phone": contact_phone.strip() or None,
            "contact_email": contact_email.strip() or None
        }
        
        try:
            create_cat(cat_data)
        except Exception as exc:
            storage_service.delete_image_by_url(image_url)
            if "schema cache" in str(exc) and "contact_" in str(exc):
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Database contact columns are missing. Run "
                        "database/add_contact_fields.sql in Supabase SQL Editor."
                    )
                )
            raise
        
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
        return list_cats()
    except Exception as e:
        print(f"Error fetching cats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch cats")

@router.get("/similar/{cat_id}", response_model=List[SimilarCatResponse])
async def get_similar_cats(cat_id: str):
    """
    Find visually similar cats using CLIP embeddings
    Returns top 5 most similar cats
    """
    try:
        print(f"[similar] target id: {cat_id}")

        if not settings.enable_ai_matching:
            raise HTTPException(
                status_code=501,
                detail="AI image matching is not enabled yet"
            )

        # Get target cat
        target_cat = get_cat_by_id(cat_id)
        
        if not target_cat:
            raise HTTPException(status_code=404, detail="Cat not found")
        
        target_embedding = ensure_embedding(target_cat)
        if not embedding_service.is_clip_embedding(target_embedding):
            raise HTTPException(
                status_code=503,
                detail="Target cat embedding is unavailable"
            )
        print(f"[similar] target embedding length: {len(target_embedding)}")
        
        # Get all other cats
        other_cats = list_cats_except(cat_id)
        print(f"[similar] number of cats fetched: {len(other_cats)}")
        
        # Calculate similarities
        similarities = []
        for cat in other_cats:
            cat_embedding = ensure_embedding(cat)
            if not embedding_service.is_clip_embedding(cat_embedding):
                print(f"[similar] skipping non-CLIP embedding for cat id: {cat['id']}")
                continue

            similarity_score = embedding_service.compare_embeddings(
                target_embedding, 
                cat_embedding
            )

            print(
                "[similar] compared cat id: "
                f"{cat['id']} score: {similarity_score}"
            )
            
            similarities.append({
                "cat_id": cat["id"],
                "image_url": cat["image_url"],
                "status": cat["status"],
                "location": cat["location"],
                "description": cat["description"],
                "owner_name": cat.get("owner_name"),
                "contact_phone": cat.get("contact_phone"),
                "contact_email": cat.get("contact_email"),
                "similarity_score": similarity_score
            })
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        print(
            "[similar] top 5 after descending sort: "
            f"{[(item['cat_id'], item['similarity_score']) for item in similarities[:5]]}"
        )
        
        # Return top 5
        return similarities[:5]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error finding similar cats: {e}")
        raise HTTPException(status_code=500, detail="Failed to find similar cats")

@router.get("/{cat_id}", response_model=CatResponse)
async def get_cat(cat_id: str):
    """
    Get a single cat by ID
    """
    try:
        cat = get_cat_by_id(cat_id)
        
        if not cat:
            raise HTTPException(status_code=404, detail="Cat not found")
        
        return cat
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching cat: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch cat")
