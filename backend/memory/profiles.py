"""
Student Profile Management
Handles long-term student data and learning progress
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path


class StudentProfileManager:
    """
    Manages persistent student profiles and learning history
    In production, this would use PostgreSQL or similar database
    """
    
    def __init__(self, student_id: str, storage_dir: str = "data/profiles"):
        self.student_id = student_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.profile_path = self.storage_dir / f"{student_id}.json"
        
    def get_or_create_profile(self) -> Dict[str, Any]:
        """
        Get existing profile or create new one
        
        Returns:
            Student profile dict
        """
        if self.profile_path.exists():
            return self._load_profile()
        else:
            return self._create_profile()
    
    def _create_profile(self) -> Dict[str, Any]:
        """Create new student profile with defaults"""
        profile = {
            'student_id': self.student_id,
            'created_at': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat(),
            'level': 'Beginner',
            'progress': 0,
            'topics': [],
            'total_questions': 0,
            'total_sessions': 0,
            'learning_streak_days': 0,
            'achievements': [],
            'preferences': {
                'learning_pace': 'normal',
                'preferred_examples': 'everyday',
                'explanation_style': 'simple'
            },
            'goals': [],
            'weak_areas': [],
            'strong_areas': []
        }
        
        self._save_profile(profile)
        return profile
    
    def _load_profile(self) -> Dict[str, Any]:
        """Load profile from storage"""
        try:
            with open(self.profile_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading profile: {e}")
            return self._create_profile()
    
    def _save_profile(self, profile: Dict[str, Any]):
        """Save profile to storage"""
        try:
            with open(self.profile_path, 'w') as f:
                json.dump(profile, f, indent=2)
        except Exception as e:
            print(f"Error saving profile: {e}")
    
    def update_profile(self, updates: Dict[str, Any]):
        """
        Update profile with new data
        
        Args:
            updates: Dict of fields to update
        """
        profile = self.get_or_create_profile()
        
        # Update fields
        for key, value in updates.items():
            if key in profile:
                profile[key] = value
        
        # Update last active time
        profile['last_active'] = datetime.now().isoformat()
        
        # Save updated profile
        self._save_profile(profile)
    
    def add_topic(self, topic: str):
        """Add newly learned topic"""
        profile = self.get_or_create_profile()
        
        if topic not in profile['topics']:
            profile['topics'].append(topic)
            self._save_profile(profile)
    
    def increment_progress(self, amount: int = 5):
        """Increment learning progress"""
        profile = self.get_or_create_profile()
        profile['progress'] = min(100, profile['progress'] + amount)
        self._save_profile(profile)
    
    def add_achievement(self, achievement: Dict[str, Any]):
        """
        Add learning achievement
        
        Args:
            achievement: Dict with name, description, earned_at
        """
        profile = self.get_or_create_profile()
        
        achievement['earned_at'] = datetime.now().isoformat()
        profile['achievements'].append(achievement)
        
        self._save_profile(profile)
    
    def update_learning_streak(self):
        """Update learning streak (consecutive days of activity)"""
        profile = self.get_or_create_profile()
        
        last_active = datetime.fromisoformat(profile['last_active'])
        today = datetime.now().date()
        last_date = last_active.date()
        
        # Check if consecutive day
        days_diff = (today - last_date).days
        
        if days_diff == 1:
            # Consecutive day
            profile['learning_streak_days'] += 1
        elif days_diff > 1:
            # Streak broken
            profile['learning_streak_days'] = 1
        # If same day, no change
        
        self._save_profile(profile)
    
    def get_learning_history(self) -> Dict[str, Any]:
        """
        Get comprehensive learning history
        
        Returns:
            Learning history with stats and progress
        """
        profile = self.get_or_create_profile()
        
        return {
            'student_id': self.student_id,
            'level': profile['level'],
            'progress': profile['progress'],
            'topics_learned': profile['topics'],
            'topics_count': len(profile['topics']),
            'total_questions': profile['total_questions'],
            'total_sessions': profile['total_sessions'],
            'learning_streak': profile['learning_streak_days'],
            'achievements': profile['achievements'],
            'created_at': profile['created_at'],
            'last_active': profile['last_active'],
            'days_since_created': self._days_since_created(profile['created_at'])
        }
    
    def _days_since_created(self, created_at: str) -> int:
        """Calculate days since profile creation"""
        created = datetime.fromisoformat(created_at)
        now = datetime.now()
        return (now - created).days
    
    def get_recommendations(self) -> List[Dict[str, str]]:
        """
        Get personalized learning recommendations
        
        Returns:
            List of recommended topics/activities
        """
        profile = self.get_or_create_profile()
        learned_topics = set(profile['topics'])
        
        # Topic prerequisites and recommendations
        recommendations = []
        
        # Beginner recommendations
        if profile['level'] == 'Beginner':
            if 'Machine Learning' not in learned_topics:
                recommendations.append({
                    'topic': 'Machine Learning Basics',
                    'reason': 'Great starting point for AI learning',
                    'difficulty': 'Beginner'
                })
            if 'AI Ethics' not in learned_topics:
                recommendations.append({
                    'topic': 'AI Ethics',
                    'reason': 'Understanding responsible AI is important',
                    'difficulty': 'Beginner'
                })
        
        # Intermediate recommendations
        elif profile['level'] == 'Intermediate':
            if 'Machine Learning' in learned_topics and 'Neural Networks' not in learned_topics:
                recommendations.append({
                    'topic': 'Neural Networks',
                    'reason': 'Natural next step after Machine Learning',
                    'difficulty': 'Intermediate'
                })
            if 'NLP' not in learned_topics:
                recommendations.append({
                    'topic': 'Natural Language Processing',
                    'reason': 'Exciting applications in language AI',
                    'difficulty': 'Intermediate'
                })
        
        # Advanced recommendations
        else:
            if 'Neural Networks' in learned_topics and 'Generative AI' not in learned_topics:
                recommendations.append({
                    'topic': 'Generative AI',
                    'reason': 'Cutting-edge AI technology',
                    'difficulty': 'Advanced'
                })
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def export_profile(self) -> Dict[str, Any]:
        """
        Export complete profile for backup/analysis
        
        Returns:
            Complete profile data
        """
        return self.get_or_create_profile()
