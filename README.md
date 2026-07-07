# Pet Rescue & Rehoming System with AI Image Matching

A full-stack web application that allows users to upload cat images (lost, found, stray, adoptable), store them, and find visually similar cats using AI image similarity powered by CLIP.

## Features

- **Upload Cat Images**: Upload cat photos with status, location, and description
- **AI-Powered Matching**: Uses CLIP (OpenCLIP) model to generate image embeddings
- **Similarity Search**: Find visually similar cats using cosine similarity
- **Gallery View**: Browse all uploaded cats with filtering by status
- **Modern UI**: Clean, responsive design with vanilla HTML/CSS/JavaScript

## Tech Stack

### Backend
- **FastAPI**: Python web framework
- **Supabase**: PostgreSQL database and Storage
- **OpenCLIP/CLIP**: AI model for image embeddings
- **PyTorch**: Deep learning framework
- **Pillow**: Image processing

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling with modern design
- **Vanilla JavaScript**: No frameworks

## Project Structure

```
hackthekitty/
├── backend/
│   └── app/
│       ├── main.py                 # FastAPI application entry point
│       ├── routes/
│       │   └── cats.py             # API endpoints for cats
│       ├── models/
│       │   └── cat.py              # Pydantic models
│       ├── database/
│       │   └── connection.py       # Supabase database connection
│       ├── storage/
│       │   └── storage_service.py  # Supabase storage operations
│       └── ai/
│           └── embedding_service.py # CLIP embedding generation
├── frontend/
│   ├── index.html                  # Home page
│   ├── upload.html                 # Upload page
│   ├── gallery.html                # Gallery page
│   ├── similar.html                # Similar cats results page
│   ├── style.css                   # Styles
│   └── script.js                   # Frontend JavaScript
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Supabase account (free tier works)
- CUDA-capable GPU (optional, for faster CLIP inference)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hackthekitty
```

### 2. Set Up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to Settings > API and copy:
   - Project URL
   - anon/public API Key
3. Create a storage bucket named `pet-pics` with public access
4. Run the following SQL in the Supabase SQL Editor to create the table:

```sql
CREATE TABLE cats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status TEXT NOT NULL CHECK (status IN ('lost', 'found', 'stray', 'adoptable')),
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    image_url TEXT NOT NULL,
    embedding JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS (optional, for production)
ALTER TABLE cats ENABLE ROW LEVEL SECURITY;

-- Allow public read access (adjust as needed)
CREATE POLICY "Public read access" ON cats
    FOR SELECT USING (true);

-- Allow public insert access (adjust as needed)
CREATE POLICY "Public insert access" ON cats
    FOR INSERT WITH CHECK (true);
```

### 3. Set Up Environment Variables

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Supabase credentials:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note**: On Windows, if you encounter issues with PyTorch installation, visit [pytorch.org](https://pytorch.org/get-started/locally/) for the correct installation command for your system.

### 5. Run the Application

```bash
cd backend
python -m app.main
```

The server will start on `http://localhost:8000`

### 6. Access the Application

- Home page: http://localhost:8000/index.html
- Upload page: http://localhost:8000/upload.html
- Gallery page: http://localhost:8000/gallery.html

## API Endpoints

### POST /api/cats/upload
Upload a cat image with metadata.

**Request**: multipart/form-data
- `image`: Image file
- `status`: "lost" | "found" | "stray" | "adoptable"
- `location`: Location string
- `description`: Description string

**Response**:
```json
{
  "id": "uuid",
  "image_url": "https://...",
  "message": "Cat uploaded successfully"
}
```

### GET /api/cats
Get all uploaded cats.

**Response**:
```json
[
  {
    "id": "uuid",
    "status": "lost",
    "location": "Downtown Park",
    "description": "Orange tabby cat...",
    "image_url": "https://...",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### GET /api/cats/{id}
Get a single cat by ID.

### GET /api/cats/similar/{id}
Find visually similar cats using CLIP embeddings.

**Response**:
```json
[
  {
    "cat_id": "uuid",
    "image_url": "https://...",
    "similarity_score": 0.95
  }
]
```

## How It Works

1. **Upload Flow**:
   - User uploads image via frontend
   - FastAPI receives the image
   - Image is uploaded to Supabase Storage
   - CLIP model generates embedding vector
   - Metadata and embedding saved to Supabase PostgreSQL

2. **Similarity Search**:
   - Target cat's embedding is retrieved
   - Compared with all other cat embeddings using cosine similarity
   - Results sorted by similarity score (highest first)
   - Top 5 matches returned

## Development

### Running in Development Mode

For auto-reload during development:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### CLIP Model Loading Issues
- If the model fails to load, ensure you have enough RAM (at least 4GB available)
- The first run will download the model (~600MB), which may take time

### Supabase Connection Issues
- Verify your SUPABASE_URL and SUPABASE_KEY are correct
- Check that your Supabase project is active
- Ensure the storage bucket exists and has public access

### Image Upload Failures
- Check that the storage bucket name is exactly `cat-images`
- Verify the bucket has public read access enabled
- Check Supabase storage policies

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
