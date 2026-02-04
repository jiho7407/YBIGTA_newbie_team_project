from fastapi import APIRouter, HTTPException, Path
from database.mongodb_connection import mongo_client
from review_analysis.preprocessing.common_processor import CommonProcessor
from pydantic import BaseModel

class PreprocessResponse(BaseModel):
    message: str
    site_name: str
    processed_documents: int

review = APIRouter(
    tags=["Review Preprocessing"]
)

VALID_SITES = ["imdb", "metacritic", "rottentomatoes"]
DB_NAME = "review_db"

@review.post("/review/preprocess/{site_name}", response_model=PreprocessResponse)
def preprocess_reviews(site_name: str = Path(..., description=f"The site to preprocess. Valid sites: {', '.join(VALID_SITES)}")):
    """
    Crawled data from MongoDB for the {site_name} is retrieved,
    preprocessed using the implemented preprocessing class,
    and then saved back to MongoDB.
    """
    if site_name not in VALID_SITES:
        raise HTTPException(status_code=400, detail=f"Invalid site name. Please use one of {VALID_SITES}")

    try:
        # CommonProcessor 인스턴스 생성 (MongoDB 클라이언트 전달)
        processor = CommonProcessor(db_client=mongo_client, db_name=DB_NAME, site_name=site_name)
        
        # 전처리 실행
        processor.preprocess()
        
        # 피처 엔지니어링 실행
        processor.feature_engineering()
        
        # 결과 저장
        processor.save_to_database()
        
        processed_count = len(processor.engineered_data) if processor.engineered_data is not None else 0

        return {
            "message": "Preprocessing completed successfully.",
            "site_name": site_name,
            "processed_documents": processed_count
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
