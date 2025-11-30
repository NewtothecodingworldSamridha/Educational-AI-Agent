"""
Session Memory Management
Handles short-term context and conversation history
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import deque


class SessionManager:
    """
    Manages session state and conversation history
    In production, this would use Redis for distributed sessions
    """
    
    def __init__(self, session_id: str, max_history: int = 50):
        self.session_id = session_id
        self.max_history = max_history
        self.start_time = datetime.now()
        
        # Session data structures
        self.messages = deque(maxlen=max_history)
        self.events = []
        self.metadata = {
            'session_id': session_id,
            'start_time': self.start_time.isoformat(),
            'message_count': 0,
            'topics_discussed': set()
        }
        
    def add_message(self, message: Dict[str, Any]):
        """
        Add message to session history
        
        Args:
            message: Message dict with role, content, timestamp
        """
        self.messages.append(message)
        self.metadata['message_count'] += 1
        
        # Track topics if present
        if 'topics' in message:
            self.metadata['topics_discussed'].update(message['topics'])
    
    def add_event(self, event: Dict[str, Any]):
        """
        Add session event for analytics
        
        Args:
            event: Event data (user action, system state change, etc.)
        """
        event['event_id'] = f"{self.session_id}_{len(self.events)}"
        event['timestamp'] = event.get('timestamp', datetime.now().isoformat())
        self.events.append(event)
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent messages from session
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of recent messages
        """
        messages_list = list(self.messages)
        return messages_list[-limit:] if messages_list else []
    
    def get_message_history(self) -> List[Dict[str, Any]]:
        """Get complete message history"""
        return list(self.messages)
    
    def get_duration(self) -> float:
        """Get session duration in seconds"""
        duration = datetime.now() - self.start_time
        return duration.total_seconds()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get session summary with key metrics
        
        Returns:
            Dict with session statistics
        """
        duration = self.get_duration()
        messages = list(self.messages)
        
        # Calculate metrics
        user_messages = [m for m in messages if m.get('role') == 'user']
        ai_messages = [m for m in messages if m.get('role') == 'assistant']
        
        return {
            'session_id': self.session_id,
            'duration_seconds': duration,
            'duration_formatted': self._format_duration(duration),
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'ai_responses': len(ai_messages),
            'topics_discussed': list(self.metadata['topics_discussed']),
            'start_time': self.metadata['start_time'],
            'end_time': datetime.now().isoformat(),
            'events_count': len(self.events)
        }
    
    def get_context_summary(self) -> str:
        """
        Get textual summary of session context
        Useful for providing context to the LLM
        """
        messages = list(self.messages)
        if not messages:
            return "New session, no previous context."
        
        recent = messages[-5:]
        summary_parts = [
            f"Session Duration: {self._format_duration(self.get_duration())}",
            f"Messages Exchanged: {len(messages)}",
            f"Topics Discussed: {', '.join(self.metadata['topics_discussed']) if self.metadata['topics_discussed'] else 'None yet'}",
            "\nRecent Conversation:"
        ]
        
        for msg in recent:
            role = msg.get('role', 'unknown').title()
            content = msg.get('content', '')[:100]  # Truncate long messages
            summary_parts.append(f"  {role}: {content}...")
        
        return "\n".join(summary_parts)
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def clear_history(self):
        """Clear message history (keeping metadata)"""
        self.messages.clear()
        self.metadata['message_count'] = 0
    
    def export_session(self) -> Dict[str, Any]:
        """
        Export complete session data for storage/analysis
        
        Returns:
            Complete session data
        """
        return {
            'session_id': self.session_id,
            'metadata': {
                **self.metadata,
                'topics_discussed': list(self.metadata['topics_discussed'])
            },
            'messages': list(self.messages),
            'events': self.events,
            'summary': self.get_summary()
        }


class ContextWindow:
    """
    Manages context window for LLM calls
    Handles token limits and context prioritization
    """
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        
    def build_context(
        self,
        system_prompt: str,
        messages: List[Dict[str, Any]],
        additional_context: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build context for LLM call within token limits
        
        Args:
            system_prompt: System prompt
            messages: Conversation messages
            additional_context: Additional context to include
            
        Returns:
            Formatted messages for LLM
        """
        # Estimate tokens (rough approximation: 4 chars = 1 token)
        def estimate_tokens(text: str) -> int:
            return len(text) // 4
        
        formatted_messages = []
        current_tokens = estimate_tokens(system_prompt)
        
        if additional_context:
            current_tokens += estimate_tokens(additional_context)
        
        # Add messages from most recent backwards
        for msg in reversed(messages):
            msg_tokens = estimate_tokens(msg.get('content', ''))
            
            if current_tokens + msg_tokens > self.max_tokens:
                break
            
            formatted_messages.insert(0, {
                'role': msg['role'],
                'content': msg['content']
            })
            current_tokens += msg_tokens
        
        return formatted_messages
    
    def prioritize_context(
        self,
        messages: List[Dict[str, Any]],
        important_topics: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Prioritize context based on importance
        Keeps recent messages and those related to important topics
        """
        if not messages:
            return []
        
        # Always keep most recent messages
        recent_count = min(3, len(messages))
        recent = messages[-recent_count:]
        
        # Find messages related to important topics
        relevant = []
        for msg in messages[:-recent_count]:
            content_lower = msg.get('content', '').lower()
            if any(topic.lower() in content_lower for topic in important_topics):
                relevant.append(msg)
        
        # Combine and return
        return relevant + recent
