"""
Educational AI Agent Orchestrator
Implements the core agentic reasoning and tool coordination
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import anthropic
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from .tools import WebSearchTool, MemoryTool, AnalyticsTool
from .prompts import SYSTEM_PROMPT, EDUCATIONAL_GUIDELINES
from memory.session import SessionManager
from memory.profiles import StudentProfileManager


class EducationalAgentOrchestrator:
    """
    Main agent orchestrator following the flowchart:
    1. Integrate AI with Systems (LMS, CMS integration)
    2. Collect Data in Real Time (session feedback)
    3. Maintain Human Control (teacher override)
    4. Build Long-Term Learning Graphs (progress tracking)
    """
    
    def __init__(
        self,
        anthropic_api_key: str,
        student_id: str,
        session_id: Optional[str] = None
    ):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.student_id = student_id
        self.session_id = session_id or self._generate_session_id()
        
        # Initialize tools (Tool interoperability)
        self.web_search = WebSearchTool()
        self.memory = MemoryTool(student_id=student_id)
        self.analytics = AnalyticsTool(student_id=student_id)
        
        # Session and context management
        self.session_manager = SessionManager(self.session_id)
        self.profile_manager = StudentProfileManager(student_id)
        
        # Initialize student profile
        self.student_profile = self.profile_manager.get_or_create_profile()
        
        # Tool registry for dynamic selection
        self.tools = {
            'web_search': self.web_search,
            'memory_retrieve': self.memory,
            'analytics_update': self.analytics
        }
        
        # Conversation history for context
        self.conversation_history = []
        
    def _generate_session_id(self) -> str:
        """Generate unique session identifier"""
        return f"session_{self.student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def process_message(
        self,
        user_message: str,
        allow_web_search: bool = True,
        teacher_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user message with agentic reasoning
        
        Args:
            user_message: The student's question/message
            allow_web_search: Whether to allow web search (for current info)
            teacher_override: Optional teacher guidance/corrections
            
        Returns:
            Response dict with message, tools used, and updated context
        """
        # Step 1: Collect real-time data (flowchart step 2)
        self._collect_session_data(user_message)
        
        # Step 2: Retrieve relevant context from memory
        relevant_context = self._retrieve_context(user_message)
        
        # Step 3: Apply teacher override if present (flowchart step 3)
        if teacher_override:
            return self._apply_teacher_override(teacher_override)
        
        # Step 4: Determine if we need additional tools
        needs_search = self._should_search(user_message, allow_web_search)
        
        # Step 5: Execute agentic reasoning with Claude
        response = self._generate_response(
            user_message=user_message,
            context=relevant_context,
            use_search=needs_search
        )
        
        # Step 6: Update long-term learning graph (flowchart step 4)
        self._update_learning_graph(user_message, response)
        
        # Step 7: Update session and analytics
        self._update_session(user_message, response)
        
        return {
            'message': response['content'],
            'tools_used': response['tools_used'],
            'topics_detected': response['topics'],
            'student_level': self.student_profile['level'],
            'progress': self.student_profile['progress'],
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat()
        }
    
    def _collect_session_data(self, user_message: str):
        """Collect real-time feedback during session (Flowchart Step 2)"""
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'message': user_message,
            'student_level': self.student_profile['level'],
            'topics_explored': self.student_profile.get('topics', [])
        }
        self.session_manager.add_event(session_data)
        
    def _retrieve_context(self, user_message: str) -> Dict[str, Any]:
        """Retrieve relevant context from student memory"""
        # Get recent conversation history
        recent_history = self.session_manager.get_recent_messages(limit=5)
        
        # Get student's learned topics
        learned_topics = self.student_profile.get('topics', [])
        
        # Get relevant examples from past successful explanations
        similar_queries = self.memory.find_similar(user_message, limit=3)
        
        return {
            'recent_conversation': recent_history,
            'learned_topics': learned_topics,
            'similar_past_queries': similar_queries,
            'student_level': self.student_profile['level'],
            'progress': self.student_profile['progress']
        }
    
    def _should_search(self, user_message: str, allow_search: bool) -> bool:
        """Determine if web search is needed for current information"""
        if not allow_search:
            return False
            
        # Keywords indicating need for current information
        current_info_keywords = [
            'latest', 'recent', 'new', 'current', 'today',
            'breakthrough', 'announcement', 'news', '2024', '2025'
        ]
        
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in current_info_keywords)
    
    def _generate_response(
        self,
        user_message: str,
        context: Dict[str, Any],
        use_search: bool
    ) -> Dict[str, Any]:
        """Generate response using Claude with agentic reasoning"""
        
        # Build context-aware system prompt
        system_prompt = self._build_system_prompt(context)
        
        # Prepare messages
        messages = []
        
        # Add conversation history
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # Add current message
        messages.append({
            'role': 'user',
            'content': user_message
        })
        
        # Perform web search if needed
        search_results = None
        if use_search:
            search_results = self.web_search.search(user_message)
            # Append search context to message
            if search_results:
                search_context = f"\n\n[Current Information]: {search_results}"
                messages[-1]['content'] += search_context
        
        # Call Claude with extended thinking
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=messages,
            temperature=0.7
        )
        
        # Extract content and detect topics
        content = response.content[0].text
        detected_topics = self._detect_topics(content)
        
        # Track conversation
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': content
        })
        
        return {
            'content': content,
            'tools_used': ['web_search'] if search_results else [],
            'topics': detected_topics,
            'model': 'claude-sonnet-4'
        }
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build context-aware system prompt"""
        base_prompt = SYSTEM_PROMPT
        
        # Add student context
        student_context = f"""

Student Profile:
- Level: {context['student_level']}
- Progress: {context['progress']}%
- Previously Learned Topics: {', '.join(context['learned_topics']) if context['learned_topics'] else 'None yet'}

Recent Conversation Context:
{self._format_recent_context(context['recent_conversation'])}

{EDUCATIONAL_GUIDELINES}
"""
        
        return base_prompt + student_context
    
    def _format_recent_context(self, recent_messages: List[Dict]) -> str:
        """Format recent conversation for context"""
        if not recent_messages:
            return "This is the start of a new session."
        
        formatted = []
        for msg in recent_messages[-3:]:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:200]  # Limit length
            formatted.append(f"{role.title()}: {content}")
        
        return "\n".join(formatted)
    
    def _detect_topics(self, content: str) -> List[str]:
        """Detect AI topics mentioned in the response"""
        topics = {
            'Machine Learning': ['machine learning', 'ml', 'training', 'model'],
            'Neural Networks': ['neural', 'network', 'deep learning', 'layers'],
            'NLP': ['nlp', 'language', 'text', 'chatbot', 'sentiment'],
            'Computer Vision': ['vision', 'image', 'detection', 'recognition'],
            'AI Ethics': ['ethics', 'bias', 'fairness', 'responsible'],
            'Generative AI': ['generative', 'gpt', 'llm', 'generate'],
            'Reinforcement Learning': ['reinforcement', 'reward', 'agent', 'policy']
        }
        
        content_lower = content.lower()
        detected = []
        
        for topic, keywords in topics.items():
            if any(kw in content_lower for kw in keywords):
                detected.append(topic)
        
        return detected
    
    def _update_learning_graph(
        self,
        user_message: str,
        response: Dict[str, Any]
    ):
        """Update long-term learning graph (Flowchart Step 4)"""
        # Update profile with new topics
        new_topics = response['topics']
        current_topics = set(self.student_profile.get('topics', []))
        updated_topics = list(current_topics.union(set(new_topics)))
        
        # Calculate progress increase
        if new_topics:
            progress_increase = min(15, len(new_topics) * 5)
            new_progress = min(100, self.student_profile['progress'] + progress_increase)
        else:
            new_progress = self.student_profile['progress']
        
        # Determine level progression
        new_level = self._calculate_level(new_progress, len(updated_topics))
        
        # Update profile
        self.profile_manager.update_profile({
            'topics': updated_topics,
            'progress': new_progress,
            'level': new_level,
            'last_active': datetime.now().isoformat(),
            'total_questions': self.student_profile.get('total_questions', 0) + 1
        })
        
        # Update in-memory profile
        self.student_profile['topics'] = updated_topics
        self.student_profile['progress'] = new_progress
        self.student_profile['level'] = new_level
    
    def _calculate_level(self, progress: int, topics_count: int) -> str:
        """Calculate student level based on progress and topics"""
        if progress < 20 or topics_count < 2:
            return 'Beginner'
        elif progress < 50 or topics_count < 5:
            return 'Intermediate'
        elif progress < 80 or topics_count < 8:
            return 'Advanced'
        else:
            return 'Expert'
    
    def _update_session(self, user_message: str, response: Dict[str, Any]):
        """Update session analytics"""
        self.session_manager.add_message({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        self.session_manager.add_message({
            'role': 'assistant',
            'content': response['content'],
            'timestamp': datetime.now().isoformat(),
            'topics': response['topics']
        })
        
        # Update analytics
        self.analytics.record_interaction({
            'session_id': self.session_id,
            'topics': response['topics'],
            'tools_used': response['tools_used'],
            'timestamp': datetime.now().isoformat()
        })
    
    def _apply_teacher_override(
        self,
        override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply teacher override for human control (Flowchart Step 3)"""
        return {
            'message': override['message'],
            'tools_used': ['teacher_override'],
            'topics_detected': override.get('topics', []),
            'student_level': self.student_profile['level'],
            'progress': self.student_profile['progress'],
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'override_reason': override.get('reason', 'Teacher correction')
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary"""
        return {
            'session_id': self.session_id,
            'student_id': self.student_id,
            'duration': self.session_manager.get_duration(),
            'messages_count': len(self.conversation_history),
            'topics_explored': list(set(self.student_profile.get('topics', []))),
            'progress': self.student_profile['progress'],
            'level': self.student_profile['level'],
            'session_data': self.session_manager.get_summary()
        }
    
    def reset_session(self):
        """Start a new session while maintaining student profile"""
        self.session_id = self._generate_session_id()
        self.session_manager = SessionManager(self.session_id)
        self.conversation_history = []
