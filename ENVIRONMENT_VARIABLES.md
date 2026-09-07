# Environment Variables Configuration

These environment variables need to be configured for the application to work properly on Render.

## Required Variables

### Security
- `SECRET_KEY`: Secret key for JWT token generation (Render will auto-generate this)
- `DATABASE_URL`: PostgreSQL connection string (Render will auto-provide this from the database)

### Application Configuration
- `LAND_DATA_PROVIDER`: Set to "mock" for demonstration mode or "official" for production
- `PORT`: Application port (default: 8000)

## Optional Variables

### Official API Integration
- `OFFICIAL_LAND_API_URL`: URL for official Maharashtra land records API
- `OFFICIAL_LAND_API_KEY`: API key for official land records integration

## Render Configuration

In the render.yaml file, these variables are automatically configured:
- `DATABASE_URL` is linked to the PostgreSQL database
- `SECRET_KEY` is auto-generated
- `LAND_DATA_PROVIDER` defaults to "mock"
- `PORT` is set to 8000

## Local Development

For local development, you can create a `.env` file with:
```
SECRET_KEY=your-local-secret-key
DATABASE_URL=sqlite:///./rural_land.db
LAND_DATA_PROVIDER=mock
PORT=8000
```