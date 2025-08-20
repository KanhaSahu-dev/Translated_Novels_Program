from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.models.database import get_db, Novel, GlossaryTerm
from loguru import logger

router = APIRouter()

# Pydantic models
class GlossaryTermCreate(BaseModel):
    novel_id: int
    original_term: str
    preferred_term: str
    term_type: str  # character, place, skill, item, organization, etc.
    context: Optional[str] = None

class GlossaryTermUpdate(BaseModel):
    preferred_term: Optional[str] = None
    term_type: Optional[str] = None
    context: Optional[str] = None
    is_active: Optional[bool] = None

class GlossaryTermResponse(BaseModel):
    id: int
    novel_id: int
    original_term: str
    preferred_term: str
    term_type: str
    context: Optional[str]
    frequency: int
    is_active: bool
    created_at: str
    updated_at: str

class BulkGlossaryImport(BaseModel):
    novel_id: int
    terms: List[dict]  # List of {original_term, preferred_term, term_type, context}

@router.post("/terms", response_model=GlossaryTermResponse)
async def create_glossary_term(term: GlossaryTermCreate, db: Session = Depends(get_db)):
    """Create a new glossary term"""
    try:
        # Check if novel exists
        novel = db.query(Novel).filter(Novel.id == term.novel_id).first()
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        # Check if term already exists
        existing_term = db.query(GlossaryTerm).filter(
            GlossaryTerm.novel_id == term.novel_id,
            GlossaryTerm.original_term == term.original_term
        ).first()
        
        if existing_term:
            raise HTTPException(
                status_code=400, 
                detail="Term already exists in glossary"
            )
        
        # Create new term
        db_term = GlossaryTerm(
            novel_id=term.novel_id,
            original_term=term.original_term,
            preferred_term=term.preferred_term,
            term_type=term.term_type,
            context=term.context,
            frequency=1,
            is_active=True
        )
        
        db.add(db_term)
        db.commit()
        db.refresh(db_term)
        
        return GlossaryTermResponse(
            id=db_term.id,
            novel_id=db_term.novel_id,
            original_term=db_term.original_term,
            preferred_term=db_term.preferred_term,
            term_type=db_term.term_type,
            context=db_term.context,
            frequency=db_term.frequency,
            is_active=db_term.is_active,
            created_at=db_term.created_at.isoformat(),
            updated_at=db_term.updated_at.isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating glossary term: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create term: {str(e)}")

@router.get("/terms/{novel_id}", response_model=List[GlossaryTermResponse])
async def get_glossary_terms(
    novel_id: int, 
    term_type: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get glossary terms for a novel"""
    try:
        # Check if novel exists
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        # Build query
        query = db.query(GlossaryTerm).filter(GlossaryTerm.novel_id == novel_id)
        
        if term_type:
            query = query.filter(GlossaryTerm.term_type == term_type)
        
        if active_only:
            query = query.filter(GlossaryTerm.is_active == True)
        
        terms = query.order_by(GlossaryTerm.frequency.desc()).all()
        
        return [
            GlossaryTermResponse(
                id=term.id,
                novel_id=term.novel_id,
                original_term=term.original_term,
                preferred_term=term.preferred_term,
                term_type=term.term_type,
                context=term.context,
                frequency=term.frequency,
                is_active=term.is_active,
                created_at=term.created_at.isoformat(),
                updated_at=term.updated_at.isoformat()
            )
            for term in terms
        ]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting glossary terms: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get terms: {str(e)}")

@router.put("/terms/{term_id}", response_model=GlossaryTermResponse)
async def update_glossary_term(
    term_id: int, 
    term_update: GlossaryTermUpdate, 
    db: Session = Depends(get_db)
):
    """Update a glossary term"""
    try:
        term = db.query(GlossaryTerm).filter(GlossaryTerm.id == term_id).first()
        if not term:
            raise HTTPException(status_code=404, detail="Term not found")
        
        # Update fields
        if term_update.preferred_term is not None:
            term.preferred_term = term_update.preferred_term
        if term_update.term_type is not None:
            term.term_type = term_update.term_type
        if term_update.context is not None:
            term.context = term_update.context
        if term_update.is_active is not None:
            term.is_active = term_update.is_active
        
        db.commit()
        db.refresh(term)
        
        return GlossaryTermResponse(
            id=term.id,
            novel_id=term.novel_id,
            original_term=term.original_term,
            preferred_term=term.preferred_term,
            term_type=term.term_type,
            context=term.context,
            frequency=term.frequency,
            is_active=term.is_active,
            created_at=term.created_at.isoformat(),
            updated_at=term.updated_at.isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating glossary term: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update term: {str(e)}")

@router.delete("/terms/{term_id}")
async def delete_glossary_term(term_id: int, db: Session = Depends(get_db)):
    """Delete a glossary term"""
    try:
        term = db.query(GlossaryTerm).filter(GlossaryTerm.id == term_id).first()
        if not term:
            raise HTTPException(status_code=404, detail="Term not found")
        
        db.delete(term)
        db.commit()
        
        return {"message": f"Term '{term.original_term}' deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting glossary term: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete term: {str(e)}")

@router.post("/bulk-import")
async def bulk_import_glossary(import_data: BulkGlossaryImport, db: Session = Depends(get_db)):
    """Bulk import glossary terms"""
    try:
        # Check if novel exists
        novel = db.query(Novel).filter(Novel.id == import_data.novel_id).first()
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        created_count = 0
        updated_count = 0
        errors = []
        
        for term_data in import_data.terms:
            try:
                original_term = term_data.get('original_term', '').strip()
                preferred_term = term_data.get('preferred_term', '').strip()
                term_type = term_data.get('term_type', 'general').strip()
                context = term_data.get('context', '')
                
                if not original_term or not preferred_term:
                    errors.append(f"Missing required fields for term: {term_data}")
                    continue
                
                # Check if term exists
                existing_term = db.query(GlossaryTerm).filter(
                    GlossaryTerm.novel_id == import_data.novel_id,
                    GlossaryTerm.original_term == original_term
                ).first()
                
                if existing_term:
                    # Update existing term
                    existing_term.preferred_term = preferred_term
                    existing_term.term_type = term_type
                    existing_term.context = context
                    existing_term.is_active = True
                    updated_count += 1
                else:
                    # Create new term
                    new_term = GlossaryTerm(
                        novel_id=import_data.novel_id,
                        original_term=original_term,
                        preferred_term=preferred_term,
                        term_type=term_type,
                        context=context,
                        frequency=1,
                        is_active=True
                    )
                    db.add(new_term)
                    created_count += 1
                
            except Exception as e:
                errors.append(f"Error processing term {term_data}: {str(e)}")
        
        db.commit()
        
        return {
            "message": "Bulk import completed",
            "created_count": created_count,
            "updated_count": updated_count,
            "total_processed": created_count + updated_count,
            "errors": errors
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk import: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk import failed: {str(e)}")

@router.get("/term-types/{novel_id}")
async def get_term_types(novel_id: int, db: Session = Depends(get_db)):
    """Get all term types used in a novel's glossary"""
    try:
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        # Get distinct term types
        term_types = db.query(GlossaryTerm.term_type).filter(
            GlossaryTerm.novel_id == novel_id,
            GlossaryTerm.is_active == True
        ).distinct().all()
        
        # Count terms for each type
        type_counts = {}
        for term_type_tuple in term_types:
            term_type = term_type_tuple[0]
            count = db.query(GlossaryTerm).filter(
                GlossaryTerm.novel_id == novel_id,
                GlossaryTerm.term_type == term_type,
                GlossaryTerm.is_active == True
            ).count()
            type_counts[term_type] = count
        
        return {
            "novel_id": novel_id,
            "term_types": type_counts,
            "total_active_terms": sum(type_counts.values())
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting term types: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get term types: {str(e)}")

@router.post("/export/{novel_id}")
async def export_glossary(novel_id: int, db: Session = Depends(get_db)):
    """Export glossary terms for a novel"""
    try:
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        terms = db.query(GlossaryTerm).filter(
            GlossaryTerm.novel_id == novel_id,
            GlossaryTerm.is_active == True
        ).order_by(GlossaryTerm.term_type, GlossaryTerm.original_term).all()
        
        export_data = {
            "novel_title": novel.title,
            "novel_id": novel_id,
            "export_date": "today",  # You might want to use datetime.now().isoformat()
            "total_terms": len(terms),
            "terms": [
                {
                    "original_term": term.original_term,
                    "preferred_term": term.preferred_term,
                    "term_type": term.term_type,
                    "context": term.context,
                    "frequency": term.frequency
                }
                for term in terms
            ]
        }
        
        return export_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting glossary: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}") 