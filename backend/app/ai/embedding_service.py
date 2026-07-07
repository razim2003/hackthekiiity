import math
from typing import List, Optional

from PIL import Image


class EmbeddingService:
    def __init__(self):
        self.model = None
        self.preprocess = None
        self.torch = None
        self.device = None
        self.backend_name = "pixel-fallback"
        self._clip_load_attempted = False

    def generate_embedding(self, image: Image.Image) -> List[float]:
        """
        Generate a visual embedding.

        OpenCLIP is used when its heavy dependencies are installed. For the
        hackathon demo, the pixel fallback keeps matching functional without
        requiring a large model download on a fresh laptop.
        """
        clip_embedding = self._generate_clip_embedding(image)
        if clip_embedding:
            return clip_embedding

        return self._generate_pixel_embedding(image)

    def compare_embeddings(self, embedding1: Optional[List[float]], embedding2: Optional[List[float]]) -> float:
        if not embedding1 or not embedding2:
            return 0.0

        length = min(len(embedding1), len(embedding2))
        if length == 0:
            return 0.0

        vec1 = embedding1[:length]
        vec2 = embedding2[:length]
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(value * value for value in vec1))
        norm2 = math.sqrt(sum(value * value for value in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return max(0.0, min(1.0, float(similarity)))

    def _generate_clip_embedding(self, image: Image.Image) -> Optional[List[float]]:
        if not self._load_clip():
            return None

        try:
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            with self.torch.no_grad():
                embedding = self.model.encode_image(image_input)
                embedding = embedding / embedding.norm(dim=-1, keepdim=True)
            return embedding.cpu().numpy()[0].tolist()
        except Exception as exc:
            print(f"OpenCLIP embedding failed; using fallback: {exc}")
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
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32",
                pretrained="laion2b_s34b_b79k",
            )
            self.model = self.model.to(self.device)
            self.model.eval()
            self.backend_name = f"openclip-{self.device}"
            print(f"OpenCLIP model loaded on {self.device}")
            return True
        except Exception as exc:
            print(f"OpenCLIP unavailable; using pixel fallback: {exc}")
            return False

    def _generate_pixel_embedding(self, image: Image.Image) -> List[float]:
        small_image = image.convert("RGB").resize((16, 16))
        pixels = list(small_image.getdata())

        values: List[float] = []
        for red, green, blue in pixels:
            values.extend([red / 255.0, green / 255.0, blue / 255.0])

        return values


embedding_service = EmbeddingService()
