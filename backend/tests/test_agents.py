"""
Tests for Agent Orchestrator
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from agents.orchestrator import EducationalAgentOrchestrator
from agents.tools import WebSearchTool, MemoryTool, AnalyticsTool


class TestEducationalAgentOrchestrator:
    """Test suite for the main agent orchestrator"""
    
    @pytest.fixture
    def mock_anthropic_client(self):
        """Mock Anthropic client"""
        with patch('agents.orchestrator.anthropic.Anthropic') as mock:
            client = Mock()
            response = Mock()
            response.content = [Mock(text="Machine learning is a subset of AI...")]
            client.messages.create.return_value = response
            mock.return_value = client
            yield mock
    
    @pytest.fixture
    def orchestrator(self, mock_anthropic_client):
        """Create orchestrator instance for testing"""
        return EducationalAgentOrchestrator(
            anthropic_api_key="test_key",
            student_id="test_student_123"
        )
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator.student_id == "test_student_123"
        assert orchestrator.session_id is not None
        assert isinstance(orchestrator.web_search, WebSearchTool)
        assert isinstance(orchestrator.memory, MemoryTool)
        assert isinstance(orchestrator.analytics, AnalyticsTool)
        assert len(orchestrator.conversation_history) == 0
    
    def test_session_id_generation(self, orchestrator):
        """Test session ID is generated correctly"""
        session_id = orchestrator.session_id
        assert session_id.startswith("session_test_student_123_")
        assert len(session_id) > 30  # Has timestamp
    
    def test_collect_session_data(self, orchestrator):
        """Test session data collection"""
        orchestrator._collect_session_data("What is machine learning?")
        
        # Check that session manager has the event
        assert len(orchestrator.session_manager.events) > 0
    
    def test_retrieve_context(self, orchestrator):
        """Test context retrieval"""
        context = orchestrator._retrieve_context("Tell me about neural networks")
        
        assert 'recent_conversation' in context
        assert 'learned_topics' in context
        assert 'student_level' in context
        assert context['student_level'] == 'Beginner'
    
    def test_should_search_with_current_keywords(self, orchestrator):
        """Test search detection for current info keywords"""
        assert orchestrator._should_search("What are the latest AI developments?", True)
        assert orchestrator._should_search("Recent breakthroughs in ML", True)
        assert orchestrator._should_search("Current state of AI in 2024", True)
        
        # Should not search for static content
        assert not orchestrator._should_search("What is machine learning?", True)
        assert not orchestrator._should_search("Explain neural networks", True)
    
    def test_should_not_search_when_disabled(self, orchestrator):
        """Test search is disabled when flag is False"""
        assert not orchestrator._should_search("Latest AI news", False)
    
    def test_detect_topics(self, orchestrator):
        """Test topic detection in responses"""
        content = """
        Machine learning is a subset of AI where computers learn from data.
        Neural networks are inspired by the human brain and consist of layers.
        """
        
        topics = orchestrator._detect_topics(content)
        
        assert 'Machine Learning' in topics
        assert 'Neural Networks' in topics
        assert len(topics) >= 2
    
    def test_process_message_flow(self, orchestrator, mock_anthropic_client):
        """Test complete message processing flow"""
        response = orchestrator.process_message(
            user_message="What is machine learning?",
            allow_web_search=False
        )
        
        # Check response structure
        assert 'message' in response
        assert 'session_id' in response
        assert 'student_level' in response
        assert 'progress' in response
        assert 'topics_detected' in response
        assert 'tools_used' in response
        
        # Check that Claude was called
        client = mock_anthropic_client.return_value
        assert client.messages.create.called
    
    def test_update_learning_graph(self, orchestrator):
        """Test learning graph updates"""
        initial_progress = orchestrator.student_profile['progress']
        
        response = {
            'content': 'Test response',
            'topics': ['Machine Learning', 'Neural Networks'],
            'tools_used': []
        }
        
        orchestrator._update_learning_graph("Test question", response)
        
        # Check progress increased
        assert orchestrator.student_profile['progress'] >= initial_progress
        
        # Check topics added
        assert 'Machine Learning' in orchestrator.student_profile['topics']
        assert 'Neural Networks' in orchestrator.student_profile['topics']
    
    def test_calculate_level_progression(self, orchestrator):
        """Test level calculation based on progress"""
        assert orchestrator._calculate_level(0, 0) == 'Beginner'
        assert orchestrator._calculate_level(15, 1) == 'Beginner'
        assert orchestrator._calculate_level(35, 4) == 'Intermediate'
        assert orchestrator._calculate_level(65, 7) == 'Advanced'
        assert orchestrator._calculate_level(90, 10) == 'Expert'
    
    def test_teacher_override(self, orchestrator):
        """Test teacher override functionality"""
        override_data = {
            'message': 'Corrected explanation: ML is...',
            'reason': 'Student needed more clarity',
            'topics': ['Machine Learning']
        }
        
        response = orchestrator._apply_teacher_override(override_data)
        
        assert response['message'] == override_data['message']
        assert 'teacher_override' in response['tools_used']
        assert response['override_reason'] == override_data['reason']
    
    def test_get_session_summary(self, orchestrator):
        """Test session summary generation"""
        # Add some conversation
        orchestrator.conversation_history.append({
            'role': 'user',
            'content': 'What is AI?'
        })
        orchestrator.conversation_history.append({
            'role': 'assistant',
            'content': 'AI is...'
        })
        
        summary = orchestrator.get_session_summary()
        
        assert 'session_id' in summary
        assert 'student_id' in summary
        assert 'messages_count' in summary
        assert summary['messages_count'] == 2
        assert 'progress' in summary
        assert 'level' in summary
    
    def test_conversation_history_tracking(self, orchestrator):
        """Test conversation history is maintained"""
        orchestrator.conversation_history.append({
            'role': 'user',
            'content': 'Question 1'
        })
        orchestrator.conversation_history.append({
            'role': 'assistant',
            'content': 'Answer 1'
        })
        
        assert len(orchestrator.conversation_history) == 2
        assert orchestrator.conversation_history[0]['role'] == 'user'
        assert orchestrator.conversation_history[1]['role'] == 'assistant'
    
    def test_reset_session(self, orchestrator):
        """Test session reset"""
        old_session_id = orchestrator.session_id
        
        # Add some data
        orchestrator.conversation_history.append({'test': 'data'})
        
        # Reset
        orchestrator.reset_session()
        
        # Check new session created
        assert orchestrator.session_id != old_session_id
        assert len(orchestrator.conversation_history) == 0


class TestAgentTools:
    """Test suite for agent tools"""
    
    def test_web_search_tool_schema(self):
        """Test web search tool returns correct schema"""
        tool = WebSearchTool()
        schema = tool.get_schema()
        
        assert schema['name'] == 'web_search'
        assert 'parameters' in schema
        assert 'query' in schema['parameters']
    
    def test_web_search_simulation(self):
        """Test web search falls back to simulation"""
        tool = WebSearchTool(api_key=None)
        results = tool.search("machine learning")
        
        assert isinstance(results, str)
        assert len(results) > 0
    
    def test_memory_tool_schema(self):
        """Test memory tool returns correct schema"""
        tool = MemoryTool(student_id="test_123")
        schema = tool.get_schema()
        
        assert schema['name'] == 'memory_retrieve'
        assert 'parameters' in schema
    
    def test_memory_tool_find_similar(self):
        """Test memory tool finds similar queries"""
        tool = MemoryTool(student_id="test_123")
        results = tool.find_similar("What is AI?")
        
        assert isinstance(results, list)
    
    def test_analytics_tool_recording(self):
        """Test analytics tool records events"""
        tool = AnalyticsTool(student_id="test_123")
        
        event = {
            'session_id': 'test_session',
            'topics': ['Machine Learning'],
            'tools_used': ['web_search']
        }
        
        tool.record_interaction(event)
        
        assert len(tool.analytics_store) > 0
    
    def test_analytics_progress_summary(self):
        """Test analytics generates progress summary"""
        tool = AnalyticsTool(student_id="test_123")
        
        # Add some events
        tool.record_interaction({
            'topics': ['Machine Learning', 'Neural Networks']
        })
        tool.record_interaction({
            'topics': ['NLP']
        })
        
        summary = tool.get_progress_summary()
        
        assert summary['total_interactions'] == 2
        assert len(summary['topics_explored']) == 3


@pytest.fixture
def sample_student_profile():
    """Sample student profile for testing"""
    return {
        'student_id': 'test_student',
        'level': 'Beginner',
        'progress': 25,
        'topics': ['Machine Learning'],
        'total_questions': 10
    }


def test_agent_with_context(mock_anthropic_client, sample_student_profile):
    """Test agent uses context appropriately"""
    orchestrator = EducationalAgentOrchestrator(
        anthropic_api_key="test_key",
        student_id="test_student"
    )
    
    # Set profile
    orchestrator.student_profile = sample_student_profile
    
    # Process message
    context = orchestrator._retrieve_context("Tell me more about ML")
    
    assert context['student_level'] == 'Beginner'
    assert context['progress'] == 25
    assert 'Machine Learning' in context['learned_topics']
