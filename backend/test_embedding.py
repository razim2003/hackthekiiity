import sys
sys.path.insert(0, '.')

from app.ai.embedding_service import embedding_service
from PIL import Image

# Create a simple test image
img = Image.new('RGB', (224, 224), color='red')

try:
    emb = embedding_service.generate_embedding(img)
    print(f'Success! Embedding length: {len(emb)}')
    print(f'First 5 values: {emb[:5]}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
