import numpy as np
from PIL import Image
import open_clip
from typing import List, Optional
import torch

class EmbeddingService:
    def __init__(self):
        # Load CLIP model once at startup
        print("Loading CLIP model...")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.model.eval()
        print(f"CLIP model loaded on {self.device}")
    
    def generate_embedding(self, image: Image.Image) -> Optional[List[float]]:
        """
        Generate CLIP embedding for an image
        Returns embedding as a list of floats
        """
        try:
            # Preprocess image
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Generate embedding
            with torch.no_grad():
                embedding = self.model.encode_image(image_input)
                embedding = embedding / embedding.norm(dim=-1, keepdim=True)
            
            # Convert to list of floats
            embedding_list = embedding.cpu().numpy()[0].tolist()
            return embedding_list
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def compare_embeddings(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        Returns similarity score between 0 and 1
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            
            # Ensure similarity is between 0 and 1
            similarity = max(0, min(1, similarity))
            
            return float(similarity)
        except Exception as e:
            print(f"Error comparing embeddings: {e}")
            return 0.0

# Initialize embedding service globally
embedding_service = EmbeddingService()
