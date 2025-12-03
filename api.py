"""FastAPI REST endpoints"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from hash_chain import Amendment, HashChain, LLMSummaryGenerator
from data_ingestion import DataIngestionPipeline

app = FastAPI(
    title="Legal Act Change Tracker",
    description="Track legal amendments with hash chain verification",
    version="1.0.0"
)

llm_generator = LLMSummaryGenerator()
current_chain: Optional[HashChain] = None

class AmendmentRequest(BaseModel):
    content: str
    change_type: str
    author: str
    summary: Optional[str] = None

@app.get("/")
def root():
    """API root"""
    return {
        "api": "Legal Act Change Tracker",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/amendments")
def list_amendments(skip: int = 0, limit: int = 10):
    """List amendments"""
    if not current_chain:
        return {"error": "No chain loaded"}
    
    history = current_chain.get_history()
    return {"amendments": history[skip:skip + limit], "total": len(history)}

@app.post("/amendments")
def add_amendment(request: AmendmentRequest):
    """Add amendment"""
    if not current_chain:
        raise HTTPException(status_code=404, detail="No chain loaded")
    
    amendment = Amendment(
        content=request.content,
        change_type=request.change_type,
        author=request.author,
        summary=request.summary,
        llm=llm_generator
    )
    
    hash_val = current_chain.add_amendment(amendment)
    return {"success": True, "hash": hash_val}

@app.get("/verify")
def verify():
    """Verify chain integrity"""
    if not current_chain:
        raise HTTPException(status_code=404, detail="No chain loaded")
    
    is_valid = current_chain.verify_integrity()
    return {
        "valid": is_valid,
        "amendments": len(current_chain.chain),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/statistics")
def statistics():
    """Get statistics"""
    if not current_chain:
        raise HTTPException(status_code=404, detail="No chain loaded")
    
    history = current_chain.get_history()
    substantive = sum(1 for e in history if e['amendment']['change_type'] == 'substantive')
    editorial = sum(1 for e in history if e['amendment']['change_type'] == 'editorial')
    
    return {
        "total": len(history),
        "substantive": substantive,
        "editorial": editorial
    }
