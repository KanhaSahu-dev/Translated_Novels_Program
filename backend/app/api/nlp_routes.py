from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import asyncio

from app.models.database import get_db, Novel, Chapter, GlossaryTerm, ProcessingLog
from app.modules.nlp_processor import TranslationRefiner, ContextTracker
from loguru import logger

router = APIRouter()

# Global instances
refiner = TranslationRefiner()
context_tracker = ContextTracker()

# Pydantic models
class RefineTextRequest(BaseModel):
    text: str
    use_glossary: bool = True
    novel_id: Optional[int] = None

class RefineChapterRequest(BaseModel):
    chapter_id: int
    use_glossary: bool = True

class BatchRefineRequest(BaseModel):
    novel_id: int
    chapter_ids: Optional[List[int]] = None  # If None, process all chapters
    use_glossary: bool = True

class RefinementResponse(BaseModel):
    original_text: str
    refined_text: str
    changes_made: List[dict]
    confidence_score: float
    processing_time: float

class ChapterRefinementResponse(BaseModel):
    chapter_id: int
    chapter_number: int
    title: str
    success: bool
    refinement_result: Optional[RefinementResponse]
    error_message: Optional[str]

@router.post("/initialize")
async def initialize_nlp_models():
    """Initialize NLP models (can take some time)"""
    try:
        if not refiner.loaded:
            await refiner.initialize()
        return {"message": "NLP models initialized successfully", "status": "ready"}
    except Exception as e:
        logger.error(f"Error initializing NLP models: {e}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

@router.post("/refine-text", response_model=RefinementResponse)
async def refine_text(request: RefineTextRequest, db: Session = Depends(get_db)):
    """Refine a piece of text using NLP processing"""
    try:
        # Get glossary terms if requested
        glossary_terms = []
        if request.use_glossary and request.novel_id:
            terms = db.query(GlossaryTerm).filter(
                GlossaryTerm.novel_id == request.novel_id,
                GlossaryTerm.is_active == True
            ).all()
            
            glossary_terms = [
                {
                    'original_term': term.original_term,
                    'preferred_term': term.preferred_term,
                    'term_type': term.term_type
                }
                for term in terms
            ]
        
        # Refine the text
        result = await refiner.refine_text(request.text, glossary_terms)
        
        return RefinementResponse(
            original_text=result.original_text,
            refined_text=result.refined_text,
            changes_made=result.changes_made,
            confidence_score=result.confidence_score,
            processing_time=result.processing_time
        )
    
    except Exception as e:
        logger.error(f"Error refining text: {e}")
        raise HTTPException(status_code=500, detail=f"Text refinement failed: {str(e)}")

@router.post("/refine-chapter", response_model=ChapterRefinementResponse)
async def refine_chapter(request: RefineChapterRequest, db: Session = Depends(get_db)):
    """Refine a specific chapter"""
    try:
        # Get chapter
        chapter = db.query(Chapter).filter(Chapter.id == request.chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        # Get glossary terms if requested
        glossary_terms = []
        if request.use_glossary:
            terms = db.query(GlossaryTerm).filter(
                GlossaryTerm.novel_id == chapter.novel_id,
                GlossaryTerm.is_active == True
            ).all()
            
            glossary_terms = [
                {
                    'original_term': term.original_term,
                    'preferred_term': term.preferred_term,
                    'term_type': term.term_type
                }
                for term in terms
            ]
        
        # Refine the chapter content
        result = await refiner.refine_text(chapter.original_content, glossary_terms)
        
        # Update chapter in database
        chapter.refined_content = result.refined_text
        chapter.is_processed = True
        
        # Log the processing
        processing_log = ProcessingLog(
            chapter_id=chapter.id,
            processing_type="refinement",
            changes_made=str(result.changes_made),
            processing_time=int(result.processing_time),
            success=True
        )
        
        db.add(processing_log)
        db.commit()
        
        # Update context tracker
        context_tracker.update_context(result.refined_text, chapter.chapter_number)
        
        return ChapterRefinementResponse(
            chapter_id=chapter.id,
            chapter_number=chapter.chapter_number,
            title=chapter.title or f"Chapter {chapter.chapter_number}",
            success=True,
            refinement_result=RefinementResponse(
                original_text=result.original_text,
                refined_text=result.refined_text,
                changes_made=result.changes_made,
                confidence_score=result.confidence_score,
                processing_time=result.processing_time
            ),
            error_message=None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refining chapter {request.chapter_id}: {e}")
        
        # Log the error
        try:
            processing_log = ProcessingLog(
                chapter_id=request.chapter_id,
                processing_type="refinement",
                success=False,
                error_message=str(e)
            )
            db.add(processing_log)
            db.commit()
        except:
            pass
        
        return ChapterRefinementResponse(
            chapter_id=request.chapter_id,
            chapter_number=0,
            title="Unknown",
            success=False,
            refinement_result=None,
            error_message=str(e)
        )

@router.post("/batch-refine")
async def batch_refine_chapters(
    request: BatchRefineRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start batch refinement of multiple chapters"""
    try:
        # Get novel
        novel = db.query(Novel).filter(Novel.id == request.novel_id).first()
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        # Get chapters to process
        if request.chapter_ids:
            chapters = db.query(Chapter).filter(
                Chapter.novel_id == request.novel_id,
                Chapter.id.in_(request.chapter_ids)
            ).all()
        else:
            chapters = db.query(Chapter).filter(
                Chapter.novel_id == request.novel_id
            ).all()
        
        if not chapters:
            raise HTTPException(status_code=404, detail="No chapters found")
        
        # Start background processing
        background_tasks.add_task(
            batch_refine_background,
            request.novel_id,
            [ch.id for ch in chapters],
            request.use_glossary,
            db
        )
        
        return {
            "message": f"Batch refinement started for {len(chapters)} chapters",
            "novel_id": request.novel_id,
            "chapter_count": len(chapters),
            "status": "processing"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting batch refinement: {e}")
        raise HTTPException(status_code=500, detail=f"Batch refinement failed: {str(e)}")

@router.get("/processing-status/{novel_id}")
async def get_processing_status(novel_id: int, db: Session = Depends(get_db)):
    """Get processing status for a novel"""
    try:
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        total_chapters = len(novel.chapters)
        processed_chapters = len([ch for ch in novel.chapters if ch.is_processed])
        
        # Get recent processing logs
        recent_logs = db.query(ProcessingLog).join(Chapter).filter(
            Chapter.novel_id == novel_id
        ).order_by(ProcessingLog.created_at.desc()).limit(10).all()
        
        return {
            "novel_id": novel_id,
            "novel_title": novel.title,
            "total_chapters": total_chapters,
            "processed_chapters": processed_chapters,
            "completion_percentage": (processed_chapters / total_chapters * 100) if total_chapters > 0 else 0,
            "recent_logs": [
                {
                    "chapter_id": log.chapter_id,
                    "processing_type": log.processing_type,
                    "success": log.success,
                    "processing_time": log.processing_time,
                    "created_at": log.created_at
                }
                for log in recent_logs
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.get("/context-analysis/{novel_id}")
async def get_context_analysis(novel_id: int, db: Session = Depends(get_db)):
    """Get context analysis and consistency suggestions for a novel"""
    try:
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        # Update context tracker with all processed chapters
        context_tracker.character_names.clear()
        context_tracker.place_names.clear()
        context_tracker.term_frequency.clear()
        context_tracker.chapter_context.clear()
        
        for chapter in novel.chapters:
            if chapter.is_processed and chapter.refined_content:
                context_tracker.update_context(chapter.refined_content, chapter.chapter_number)
            elif chapter.original_content:
                context_tracker.update_context(chapter.original_content, chapter.chapter_number)
        
        suggestions = context_tracker.get_consistency_suggestions()
        
        return {
            "novel_id": novel_id,
            "character_names": dict(list(context_tracker.character_names.items())[:20]),  # Top 20
            "place_names": dict(list(context_tracker.place_names.items())[:20]),
            "consistency_suggestions": suggestions,
            "total_unique_terms": len(context_tracker.term_frequency),
            "chapters_analyzed": len(context_tracker.chapter_context)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting context analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Context analysis failed: {str(e)}")

async def batch_refine_background(
    novel_id: int,
    chapter_ids: List[int],
    use_glossary: bool,
    db: Session
):
    """Background task for batch refinement"""
    try:
        logger.info(f"Starting batch refinement for novel {novel_id}, {len(chapter_ids)} chapters")
        
        # Get glossary terms
        glossary_terms = []
        if use_glossary:
            terms = db.query(GlossaryTerm).filter(
                GlossaryTerm.novel_id == novel_id,
                GlossaryTerm.is_active == True
            ).all()
            
            glossary_terms = [
                {
                    'original_term': term.original_term,
                    'preferred_term': term.preferred_term,
                    'term_type': term.term_type
                }
                for term in terms
            ]
        
        # Process each chapter
        for chapter_id in chapter_ids:
            try:
                chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
                if not chapter:
                    continue
                
                logger.info(f"Processing chapter {chapter.chapter_number}")
                
                # Refine the chapter
                result = await refiner.refine_text(chapter.original_content, glossary_terms)
                
                # Update chapter
                chapter.refined_content = result.refined_text
                chapter.is_processed = True
                
                # Log the processing
                processing_log = ProcessingLog(
                    chapter_id=chapter.id,
                    processing_type="batch_refinement",
                    changes_made=str(result.changes_made),
                    processing_time=int(result.processing_time),
                    success=True
                )
                
                db.add(processing_log)
                db.commit()
                
                # Update context tracker
                context_tracker.update_context(result.refined_text, chapter.chapter_number)
                
                # Small delay to avoid overwhelming the system
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing chapter {chapter_id}: {e}")
                
                # Log the error
                processing_log = ProcessingLog(
                    chapter_id=chapter_id,
                    processing_type="batch_refinement",
                    success=False,
                    error_message=str(e)
                )
                db.add(processing_log)
                db.commit()
        
        logger.info(f"Batch refinement completed for novel {novel_id}")
        
    except Exception as e:
        logger.error(f"Batch refinement background task failed: {e}")
        db.rollback()
    finally:
        db.close() 