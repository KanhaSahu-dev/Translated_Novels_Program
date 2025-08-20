from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import asyncio

from app.models.database import get_db, Novel, Chapter
from app.modules.scraper import NovelHiScraper
from loguru import logger

router = APIRouter()

# Pydantic models for request/response
class NovelSearchRequest(BaseModel):
    novel_name: str

class ChapterExtractionRequest(BaseModel):
    novel_url: str
    max_chapters: Optional[int] = None
    use_selenium: bool = False

class NovelSearchResponse(BaseModel):
    title: str
    url: str
    description: str

class ChapterResponse(BaseModel):
    id: int
    chapter_number: int
    title: str
    url: str
    is_processed: bool
    word_count: int

class NovelResponse(BaseModel):
    id: int
    title: str
    url: str
    description: str
    author: str
    status: str
    total_chapters: int
    chapters: List[ChapterResponse]

@router.post("/search", response_model=List[NovelSearchResponse])
async def search_novels(request: NovelSearchRequest):
    """Search for novels on novelhi.com"""
    try:
        scraper = NovelHiScraper()
        results = await scraper.search_novel(request.novel_name)
        
        return [
            NovelSearchResponse(
                title=novel['title'],
                url=novel['url'],
                description=novel['description']
            )
            for novel in results
        ]
    
    except Exception as e:
        logger.error(f"Error searching novels: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/extract")
async def extract_novel_chapters(
    request: ChapterExtractionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start extraction of novel chapters"""
    try:
        # Check if novel already exists
        existing_novel = db.query(Novel).filter(Novel.url == request.novel_url).first()
        if existing_novel:
            raise HTTPException(
                status_code=400, 
                detail="Novel already exists in database"
            )
        
        # Start background extraction task
        background_tasks.add_task(
            extract_novel_background,
            request.novel_url,
            request.max_chapters,
            request.use_selenium,
            db
        )
        
        return {
            "message": "Novel extraction started",
            "novel_url": request.novel_url,
            "status": "processing"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting extraction: {e}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@router.get("/novels", response_model=List[NovelResponse])
async def get_novels(db: Session = Depends(get_db)):
    """Get all novels in database"""
    try:
        novels = db.query(Novel).all()
        
        result = []
        for novel in novels:
            chapters = [
                ChapterResponse(
                    id=chapter.id,
                    chapter_number=chapter.chapter_number,
                    title=chapter.title or f"Chapter {chapter.chapter_number}",
                    url=chapter.url,
                    is_processed=chapter.is_processed,
                    word_count=chapter.word_count
                )
                for chapter in novel.chapters
            ]
            
            result.append(NovelResponse(
                id=novel.id,
                title=novel.title,
                url=novel.url,
                description=novel.description or "",
                author=novel.author or "",
                status=novel.status,
                total_chapters=len(chapters),
                chapters=chapters
            ))
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting novels: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get novels: {str(e)}")

@router.get("/novels/{novel_id}", response_model=NovelResponse)
async def get_novel_by_id(novel_id: int, db: Session = Depends(get_db)):
    """Get specific novel by ID"""
    try:
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        chapters = [
            ChapterResponse(
                id=chapter.id,
                chapter_number=chapter.chapter_number,
                title=chapter.title or f"Chapter {chapter.chapter_number}",
                url=chapter.url,
                is_processed=chapter.is_processed,
                word_count=chapter.word_count
            )
            for chapter in novel.chapters
        ]
        
        return NovelResponse(
            id=novel.id,
            title=novel.title,
            url=novel.url,
            description=novel.description or "",
            author=novel.author or "",
            status=novel.status,
            total_chapters=len(chapters),
            chapters=chapters
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting novel {novel_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get novel: {str(e)}")

@router.get("/chapters/{chapter_id}")
async def get_chapter_content(chapter_id: int, db: Session = Depends(get_db)):
    """Get chapter content by ID"""
    try:
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        return {
            "id": chapter.id,
            "novel_id": chapter.novel_id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "url": chapter.url,
            "original_content": chapter.original_content,
            "refined_content": chapter.refined_content,
            "is_processed": chapter.is_processed,
            "word_count": chapter.word_count,
            "created_at": chapter.created_at,
            "updated_at": chapter.updated_at
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chapter {chapter_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chapter: {str(e)}")

@router.delete("/novels/{novel_id}")
async def delete_novel(novel_id: int, db: Session = Depends(get_db)):
    """Delete a novel and all its chapters"""
    try:
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        db.delete(novel)
        db.commit()
        
        return {"message": f"Novel '{novel.title}' deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting novel {novel_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete novel: {str(e)}")

async def extract_novel_background(
    novel_url: str, 
    max_chapters: Optional[int], 
    use_selenium: bool,
    db: Session
):
    """Background task for novel extraction"""
    try:
        logger.info(f"Starting background extraction for {novel_url}")
        
        scraper = NovelHiScraper(use_selenium=use_selenium)
        novel_data = await scraper.extract_novel_chapters(novel_url, max_chapters)
        
        if not novel_data:
            logger.error(f"Failed to extract novel data from {novel_url}")
            return
        
        # Save to database
        db_novel = Novel(
            title=novel_data.title,
            url=novel_data.url,
            description=novel_data.description,
            author=novel_data.author,
            status="ongoing"
        )
        
        db.add(db_novel)
        db.commit()
        db.refresh(db_novel)
        
        # Save chapters
        for chapter_data in novel_data.chapters:
            db_chapter = Chapter(
                novel_id=db_novel.id,
                chapter_number=chapter_data.chapter_number,
                title=chapter_data.title,
                url=chapter_data.url,
                original_content=chapter_data.content,
                word_count=chapter_data.word_count,
                is_processed=False
            )
            db.add(db_chapter)
        
        db.commit()
        
        logger.info(f"Successfully extracted and saved {len(novel_data.chapters)} chapters for '{novel_data.title}'")
        
    except Exception as e:
        logger.error(f"Background extraction failed: {e}")
        db.rollback()
    finally:
        db.close() 