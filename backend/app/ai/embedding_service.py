import math
from typing import List, Optional

from PIL import Image


class EmbeddingService:
    embedding_dimension = 512

    def __init__(self):
        self.model = None
        self.preprocess = None
        self.torch = None
        self.device = None
        self.backend_name = "openclip"
        self._clip_load_attempted = False

    def generate_embedding(self, image: Image.Image) -> List[float]:
        """
        Generate a CLIP image embedding.
        """
        clip_embedding = self._generate_clip_embedding(image)
        if clip_embedding is None:
            raise RuntimeError("CLIP embedding generation is unavailable")

        print(f"Generated embedding length: {len(clip_embedding)}")
        return clip_embedding

    def is_clip_embedding(self, embedding: Optional[List[float]]) -> bool:
        return bool(embedding) and len(embedding) == self.embedding_dimension

    def compare_embeddings(self, embedding1: Optional[List[float]], embedding2: Optional[List[float]]) -> float:
        if not self.is_clip_embedding(embedding1) or not self.is_clip_embedding(embedding2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = math.sqrt(sum(value * value for value in embedding1))
        norm2 = math.sqrt(sum(value * value for value in embedding2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return max(0.0, min(1.0, float(similarity)))

    def _generate_clip_embedding(self, image: Image.Image) -> Optional[List[float]]:
        if not self._load_clip():
            return None

        try:
            image_input = self.preprocess(image.convert("RGB")).unsqueeze(0).to(self.device)
            with self.torch.no_grad():
                embedding = self.model.encode_image(image_input)
                embedding = embedding / embedding.norm(dim=-1, keepdim=True)
            embedding_list = embedding.cpu().numpy()[0].tolist()
            print(f"CLIP embedding length: {len(embedding_list)}")
            return embedding_list
        except Exception as exc:
            print(f"CLIP embedding failed: {exc}")
            return None

    def _load_clip(self) -> bool:
        if self.model:
            return True

        if self._clip_load_attempted:
            return False

        self._clip_load_attempted = True

        try:
            import open_clip
            import torch

            self.torch = torch
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
            print(f"Loading OpenCLIP model on {self.device}...")
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32",
                pretrained="laion2b_s34b_b79k",
            )
            self.model = self.model.to(self.device)
            self.model.eval()
            self.backend_name = f"openclip-{self.device}"
            print(f"OpenCLIP model loaded successfully on {self.device}")
            print(f"OpenCLIP embedding dimension: {self.embedding_dimension}")
            return True
        except ImportError as exc:
            print(f"OpenCLIP library not installed: {exc}")
            print("Install with: pip install open-clip-torch")
            return False
        except Exception as exc:
            print(f"OpenCLIP unavailable: {exc}")
            return False


embedding_service = EmbeddingService()
