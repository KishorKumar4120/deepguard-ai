"""
Alert Management API
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from backend.api.auth import get_current_active_user
from backend.alerts.alert_manager import alert_manager_instance

router = APIRouter()

class AlertFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    camera_id: Optional[str] = None

@router.get("/history")
async def get_alert_history(
    limit: int = 100,
    offset: int = 0,
    filter: AlertFilter = None,
    current_user = Depends(get_current_active_user)
):
    """Get alert history"""
    alerts = await alert_manager_instance.get_alert_history(
        limit=limit, 
        offset=offset, 
        filter=filter.dict() if filter else None
    )
    return {
        "alerts": alerts,
        "total": len(alerts),
        "limit": limit,
        "offset": offset
    }

@router.get("/statistics")
async def get_alert_statistics(
    days: int = 7,
    current_user = Depends(get_current_active_user)
):
    """Get alert statistics"""
    stats = await alert_manager_instance.get_statistics(days=days)
    return stats

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user = Depends(get_current_active_user)
):
    """Acknowledge an alert"""
    result = await alert_manager_instance.acknowledge_alert(
        alert_id, 
        current_user.username
    )
    if result:
        return {"message": "Alert acknowledged", "alert": result}
    raise HTTPException(status_code=404, detail="Alert not found")

@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    notes: Optional[str] = None,
    current_user = Depends(get_current_active_user)
):
    """Resolve an alert"""
    result = await alert_manager_instance.resolve_alert(
        alert_id, 
        current_user.username,
        notes
    )
    if result:
        return {"message": "Alert resolved", "alert": result}
    raise HTTPException(status_code=404, detail="Alert not found")

@router.get("/active")
async def get_active_alerts(current_user = Depends(get_current_active_user)):
    """Get all active (unresolved) alerts"""
    alerts = await alert_manager_instance.get_active_alerts()
    return {"alerts": alerts, "count": len(alerts)}

@router.post("/test")
async def send_test_alert(
    background_tasks: BackgroundTasks
):
    """Send a test alert"""
    # Create a test alert
    test_alert = {
        'alert_id': f"test_{datetime.now().timestamp()}",
        'type': 'TEST_ALERT',
        'severity': 'LOW',
        'camera_name': 'Test Camera',
        'timestamp': datetime.now().isoformat(),
        'status': 'active',
        'details': {'message': 'This is a test alert from DeepGuard AI'}
    }
    
    # Add to alert history
    alert_manager_instance.alert_history.append(test_alert)
    alert_manager_instance.active_alerts[test_alert['alert_id']] = test_alert
    
    # Log the test alert
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Test alert generated: {test_alert}")
    
    return {
        "message": "Test alert sent successfully", 
        "alert": test_alert
    }