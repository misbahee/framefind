from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.photo import Photo
from app.models.face_embedding import FaceEmbedding
from app.core.config import settings

async def search_similar_photos(
    db: AsyncSession,
    event_id: UUID,
    query_embedding: list[float],
    limit: int = 50,
):
    """
    Returns all the photos close to query embedding in the vector space.
    """
    distance = FaceEmbedding.embedding.cosine_distance(
        query_embedding
    )

    SIMILARITY_THRESHOLD = settings.SIMILARITY_THRESHOLD
   
    stmt = (
        select(
            Photo.id,
            Photo.filename,
            func.min(distance).label("distance"),
        )
        .join(FaceEmbedding, FaceEmbedding.photo_id == Photo.id)
        .where(
            Photo.event_id == event_id,
            Photo.processing_status == "COMPLETED",j
            distance < SIMILARITY_THRESHOLD,
        )
        .group_by(Photo.id, Photo.filename)
        .order_by(func.min(distance))
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "photo_id": str(row.id),
            "filename": row.filename,
            "cosine_distance": float(row.distance),
            "cosine_similarity": 1.0 - float(row.distance),
        }
        for row in rows
    ]