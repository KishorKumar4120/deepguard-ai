"""
Suspicious Behavior Analysis
"""
import numpy as np
from collections import deque
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple
import math

logger = logging.getLogger(__name__)

class BehaviorAnalyzer:
    """Analyze person behavior for suspicious activities"""
    
    def __init__(self):
        self.tracked_persons = {}  # person_id -> tracking data
        self.loitering_threshold = 300  # 5 minutes in seconds
        self.aggressive_movement_threshold = 50  # pixels per second
        
    def update_tracking(self, person_id: str, position: Tuple[int, int], timestamp: datetime):
        """Update person tracking data"""
        if person_id not in self.tracked_persons:
            self.tracked_persons[person_id] = {
                'positions': deque(maxlen=100),
                'timestamps': deque(maxlen=100),
                'start_time': timestamp
            }
        
        self.tracked_persons[person_id]['positions'].append(position)
        self.tracked_persons[person_id]['timestamps'].append(timestamp)
    
    def detect_loitering(self, person_id: str) -> bool:
        """Detect if person is loitering (staying in same area too long)"""
        if person_id not in self.tracked_persons:
            return False
        
        data = self.tracked_persons[person_id]
        if len(data['positions']) < 10:
            return False
        
        # Calculate movement area
        positions = list(data['positions'])
        x_coords = [p[0] for p in positions]
        y_coords = [p[1] for p in positions]
        
        area = (max(x_coords) - min(x_coords)) * (max(y_coords) - min(y_coords))
        
        # Calculate duration
        duration = (data['timestamps'][-1] - data['timestamps'][0]).total_seconds()
        
        # Loitering if small area for long time
        return area < 5000 and duration > self.loitering_threshold
    
    def detect_aggressive_movement(self, person_id: str) -> Tuple[bool, float]:
        """Detect rapid/aggressive movements"""
        if person_id not in self.tracked_persons:
            return False, 0
        
        data = self.tracked_persons[person_id]
        if len(data['positions']) < 5:
            return False, 0
        
        # Calculate velocity
        velocities = []
        for i in range(1, len(data['positions'])):
            dx = data['positions'][i][0] - data['positions'][i-1][0]
            dy = data['positions'][i][1] - data['positions'][i-1][1]
            dt = (data['timestamps'][i] - data['timestamps'][i-1]).total_seconds()
            
            if dt > 0:
                velocity = math.sqrt(dx*dx + dy*dy) / dt
                velocities.append(velocity)
        
        if velocities:
            avg_velocity = np.mean(velocities)
            return avg_velocity > self.aggressive_movement_threshold, avg_velocity
        
        return False, 0
    
    def analyze_behavior(self, person_id: str) -> Dict:
        """Comprehensive behavior analysis"""
        result = {
            'is_loitering': self.detect_loitering(person_id),
            'is_aggressive': False,
            'aggression_score': 0,
            'behavior_summary': 'Normal'
        }
        
        is_aggressive, velocity = self.detect_aggressive_movement(person_id)
        result['is_aggressive'] = is_aggressive
        result['aggression_score'] = min(1.0, velocity / 100)
        
        if result['is_loitering'] and result['is_aggressive']:
            result['behavior_summary'] = 'SUSPICIOUS - Loitering + Aggressive'
            result['risk_level'] = 'HIGH'
        elif result['is_loitering']:
            result['behavior_summary'] = 'Suspicious - Loitering'
            result['risk_level'] = 'MEDIUM'
        elif result['is_aggressive']:
            result['behavior_summary'] = 'Suspicious - Aggressive Movement'
            result['risk_level'] = 'MEDIUM'
        else:
            result['behavior_summary'] = 'Normal'
            result['risk_level'] = 'LOW'
        
        return result

# Singleton
behavior_analyzer = BehaviorAnalyzer()