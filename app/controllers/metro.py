from fastapi import HTTPException
from typing import Union
from datetime import datetime, timedelta

def next_metro(station: Union[str, None] = None):
    # Validation
    if not station:
        raise HTTPException(status_code=400, detail="missing station parameter")
    
    # Simulation : ajouter 5 minutes à l'heure actuelle
    now = datetime.now()
    next_time = now + timedelta(minutes=5)
    next_time_str = next_time.strftime("%H:%M")
    
    return {
        "station": station,
        "line": "M1",
        "nextArrival": next_time_str,
        "headwayMin": 5
    }