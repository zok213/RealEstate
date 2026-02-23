"""Estate management routes."""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.routes.dxf_routes import sessions

logger = logging.getLogger(__name__)
router = APIRouter()

# Estate database (in-memory)
estates_db = {}


class EstateMetadata(BaseModel):
    """Estate metadata model."""
    name: str
    location: str
    description: str = ""
    owner: str = ""


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session data by ID."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Return session data but exclude non-serializable Polygon object
    session_data = sessions[session_id].copy()
    session_data.pop("polygon", None)
    
    return session_data


@router.post("/session/{session_id}/metadata")
async def update_session_metadata(session_id: str, metadata: dict):
    """Update session metadata - accepts flexible dict to support all frontend fields."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Update session with all metadata fields from frontend
    sessions[session_id]["metadata"].update(metadata)
    
    # Store in estates database
    estates_db[session_id] = {
        "session_id": session_id,
        "metadata": sessions[session_id]["metadata"],
        "boundary": sessions[session_id]["boundary"]
    }
    
    estate_name = metadata.get("estate_name") or metadata.get("name", "Unknown")
    logger.info(f"[ESTATE] Updated metadata for session {session_id}: {estate_name}")
    
    return {
        "success": True,
        "message": "Metadata updated successfully",
        "session_id": session_id
    }


@router.get("/estates")
async def list_estates():
    """List all estates."""
    return {
        "estates": list(estates_db.values()),
        "count": len(estates_db)
    }


@router.get("/estate/{session_id}")
async def get_estate(session_id: str):
    """Get estate details."""
    if session_id in estates_db:
        return estates_db[session_id]
    elif session_id in sessions:
        return {
            "session_id": session_id,
            "metadata": sessions[session_id]["metadata"],
            "boundary": sessions[session_id]["boundary"]
        }
    else:
        raise HTTPException(status_code=404, detail=f"Estate {session_id} not found")
