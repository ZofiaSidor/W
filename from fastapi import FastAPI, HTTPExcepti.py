from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from hash_chain import Amendment, HashChain, LLMSummaryGenerator
from data_ingestion import DataIngestionPipeline

app = FastAPI(
    title="Legal Act Change Tracker API",
    description="Track legal amendments with hash chain verification",
    version="1.0.0"
)

llm_generator = LLMSummaryGenerator()
ingestion_pipeline = DataIngestionPipeline(llm_generator=llm_generator)
current_chain: Optional[HashChain] = None

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AmendmentRequest(BaseModel):
    content: str
    change_type: str
    author: str
    summary: Optional[str] = None

class AmendmentResponse(BaseModel):
    version: int
    hash: str
    parent_hash: Optional[str]
    content: str
    change_type: str
    author: str
    summary: str
    timestamp: str

class VerificationReport(BaseModel):
    valid: bool
    total_amendments: int
    last_hash: str
    timestamp: str
    message: str

# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """API information"""
    return {
        "api_name": "Legal Act Change Tracker",
        "version": "1.0.0",
        "status": "running",
        "current_act": current_chain.act_title if current_chain else "No act loaded"
    }

@app.get("/health")
def health_check():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ============================================================================
# AMENDMENT ENDPOINTS
# ============================================================================

@app.get("/amendments", response_model=List[AmendmentResponse])
def list_amendments(
    author: Optional[str] = Query(None),
    change_type: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(10)
):
    """Get all amendments with optional filtering"""
    if not current_chain:
        raise HTTPException(status_code=404, detail="No legal act loaded")
    
    history = current_chain.get_history()
    
    if author:
        history = [a for a in history if a['amendment']['author'].lower() == author.lower()]
    if change_type:
        history = [a for a in history if a['amendment']['change_type'] == change_type]
    
    history = history[skip:skip + limit]
    
    responses = []
    for entry in history:
        responses.append(AmendmentResponse(
            version=entry['version'],
            hash=entry['hash'],
            parent_hash=entry['parent_hash'],
            content=entry['amendment']['content'],
            change_type=entry['amendment']['change_type'],
            author=entry['amendment']['author'],
            summary=entry['amendment']['summary'],
            timestamp=entry['amendment']['timestamp']
        ))
    
    return responses

@app.post("/amendments", response_model=AmendmentResponse)
def create_amendment(request: AmendmentRequest):
    """Add new amendment"""
    if not current_chain:
        raise HTTPException(status_code=404, detail="No legal act loaded")
    
    amendment = Amendment(
        content=request.content,
        change_type=request.change_type,
        author=request.author,
        summary=request.summary,
        llm_generator=llm_generator if request.summary is None else None
    )
    
    current_chain.add_amendment(amendment)
    history = current_chain.get_history()
    last_entry = history[-1]
    
    return AmendmentResponse(
        version=last_entry['version'],
        hash=last_entry['hash'],
        parent_hash=last_entry['parent_hash'],
        content=last_entry['amendment']['content'],
        change_type=last_entry['amendment']['change_type'],
        author=last_entry['amendment']['author'],
        summary=last_entry['amendment']['summary'],
        timestamp=last_entry['amendment']['timestamp']
    )

@app.get("/amendments/{version}", response_model=AmendmentResponse)
def get_amendment(version: int):
    """Get specific amendment by version"""
    if not current_chain:
        raise HTTPException(status_code=404, detail="No legal act loaded")
    
    history = current_chain.get_history()
    for entry in history:
        if entry['version'] == version:
            return AmendmentResponse(
                version=entry['version'],
                hash=entry['hash'],
                parent_hash=entry['parent_hash'],
                content=entry['amendment']['content'],
                change_type=entry['amendment']['change_type'],
                author=entry['amendment']['author'],
                summary=entry['amendment']['summary'],
                timestamp=entry['amendment']['timestamp']
            )
    
    raise HTTPException(status_code=404, detail=f"Amendment {version} not found")

# ============================================================================
# VERIFICATION ENDPOINTS
# ============================================================================

@app.get("/verify", response_model=VerificationReport)
def verify_chain():
    """Verify chain integrity"""
    if not current_chain:
        raise HTTPException(status_code=404, detail="No legal act loaded")
    
    is_valid = current_chain.verify_integrity()
    history = current_chain.get_history()
    last_hash = history[-1]['hash'] if history else "N/A"
    
    return VerificationReport(
        valid=is_valid,
        total_amendments=len(history),
        last_hash=last_hash,
        timestamp=datetime.now().isoformat(),
        message="✓ Chain valid" if is_valid else "✗ Chain invalid"
    )

# ============================================================================
# DATA INGESTION ENDPOINTS
# ============================================================================

@app.post("/ingest")
def ingest_xml(filepath: str):
    """Ingest amendments from XML file"""
    global current_chain
    
    try:
        current_chain = ingestion_pipeline.ingest_xml_file(filepath)
        if not current_chain:
            raise HTTPException(status_code=400, detail="Failed to ingest XML")
        
        history = current_chain.get_history()
        return {
            "success": True,
            "act_id": current_chain.act_id,
            "act_title": current_chain.act_title,
            "amendments_imported": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ingestion failed: {str(e)}")

@app.get("/ingest/status")
def ingest_status():
    """Get status of current act"""
    if not current_chain:
        return {"loaded": False, "message": "No act loaded"}
    
    history = current_chain.get_history()
    return {
        "loaded": True,
        "act_id": current_chain.act_id,
        "act_title": current_chain.act_title,
        "total_amendments": len(history)
    }

# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@app.get("/search")
def search_amendments(query: str):
    """Search amendments by content"""
    if not current_chain:
        raise HTTPException(status_code=404, detail="No legal act loaded")
    
    history = current_chain.get_history()
    query_lower = query.lower()
    
    results = []
    for entry in history:
        if (query_lower in entry['amendment']['content'].lower() or
            query_lower in entry['amendment']['summary'].lower()):
            results.append({
                "version": entry['version'],
                "hash": entry['hash'],
                "author": entry['amendment']['author'],
                "summary": entry['amendment']['summary']
            })
    
    return {"query": query, "results_count": len(results), "results": results}

# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@app.get("/export/json")
def export_json():
    """Export entire chain as JSON"""
    if not current_chain:
        raise HTTPException(status_code=404, detail="No legal act loaded")
    
    data = {
        'act_id': current_chain.act_id,
        'act_title': current_chain.act_title,
        'exported_at': datetime.now().isoformat(),
        'history': current_chain.get_history()
    }
    
    return JSONResponse(content=data)

# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@app.get("/statistics")
def get_statistics():
    """Get statistics about amendments"""
    if not current_chain:
        raise HTTPException(status_code=404, detail="No legal act loaded")
    
    history = current_chain.get_history()
    substantive_count = sum(1 for e in history if e['amendment']['change_type'] == 'substantive')
    editorial_count = sum(1 for e in history if e['amendment']['change_type'] == 'editorial')
    
    authors = {}
    for entry in history:
        author = entry['amendment']['author']
        authors[author] = authors.get(author, 0) + 1
    
    return {
        "total_amendments": len(history),
        "by_type": {"substantive": substantive_count, "editorial": editorial_count},
        "by_author": authors
    }
