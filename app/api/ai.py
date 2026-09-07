from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.system import NaturalLanguageQueryRequest, NaturalLanguageQueryResponse
from app.ai.nlp_search import process_natural_language_query

router = APIRouter(prefix="/ai", tags=["AI & Intelligent Capabilities"])

@router.post("/query", response_model=NaturalLanguageQueryResponse)
def natural_language_search(query_in: NaturalLanguageQueryRequest, db: Session = Depends(get_db)):
    """
    Translates freeform natural queries (e.g. 'Show agricultural parcels in Yeola with discrepancy')
    into safe structured SQL filters and executes them against the database.
    """
    return process_natural_language_query(query_in.query, db)
