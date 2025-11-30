# System Architecture

## Overview

The Educational AI Agent is built using modern agentic AI principles to provide adaptive, personalized AI education to underprivileged learners. This document details the system architecture, design decisions, and component interactions.

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Frontend Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │   Chat UI    │  │  Progress    │  │   Profile    │                │
│  │  Component   │  │   Tracker    │  │   Display    │                │
│  └──────────────┘  └──────────────┘  └──────────────┘                │
│         │                  │                  │                         │
│         └──────────────────┴──────────────────┘                        │
│                            │                                            │
│                     WebSocket / REST API                               │
└────────────────────────────┼──────────────────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────────────────┐
│                      API Gateway Layer (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │    Routes    │  │  WebSocket   │  │ Middleware   │                │
│  │   Handler    │  │   Handler    │  │  (CORS/Auth) │                │
│  └──────────────┘  └──────────────┘  └──────────────┘                │
└────────────────────────────┼──────────────────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────────────────┐
│                   Agent Orchestrator Layer                              │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │           Educational Agent Orchestrator                         │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │  Planning &  │  │    Tool      │  │   Context    │          │  │
│  │  │  Reasoning   │  │  Selection   │  │  Management  │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  │         │                  │                  │                   │  │
│  └─────────┼──────────────────┼──────────────────┼──────────────────┘  │
│            │                  │                  │                      │
│     ┌──────▼──────┐    ┌─────▼─────┐     ┌─────▼─────┐               │
│     │   Session   │    │  Student  │     │ Learning  │               │
│     │   Manager   │    │  Profile  │     │   Graph   │               │
│     └─────────────┘    └───────────┘     └───────────┘               │
└────────────────────────────┼──────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌─────────▼────────┐  ┌───────▼────────┐
│  Claude API    │  │  Agent Tools     │  │  Memory Store  │
│  (Sonnet 4.5)  │  │  ┌────────────┐  │  │  ┌──────────┐  │
│                │  │  │Web Search  │  │  │  │  Redis   │  │
│  - Reasoning   │  │  ├────────────┤  │  │  │ (Session)│  │
│  - Understanding│  │  │Knowledge  │  │  │  ├──────────┤  │
│  - Generation  │  │  │   Base     │  │  │  │PostgreSQL│  │
└────────────────┘  │  ├────────────┤  │  │  │(Profiles)│  │
                     │  │ Analytics  │  │  │  └──────────┘  │
                     │  └────────────┘  │  └────────────────┘
                     └──────────────────┘
```

## Core Components

### 1. Frontend Layer (React + TypeScript)

**Purpose**: Provides the user interface for students to interact with the AI agent.

**Key Components**:
- **Chat Interface**: Real-time conversation with the AI agent
- **Progress Tracker**: Visualizes learning progress and milestones
- **Profile Display**: Shows student level, topics learned, achievements
- **Topic Browser**: Allows students to explore available AI topics

**Technologies**:
- React 18 with Hooks
- TypeScript for type safety
- Tailwind CSS for styling
- Lucide React for icons
- Recharts for visualizations
- WebSocket for real-time updates

**Accessibility Features**:
- Keyboard navigation
- Screen reader support
- High contrast mode
- Mobile-responsive design
- Offline capabilities (PWA)

### 2. API Gateway Layer (FastAPI)

**Purpose**: Routes requests, handles authentication, and manages WebSocket connections.

**Endpoints**:
```
POST   /api/message              # Send message to agent
GET    /api/student/{id}/profile # Get student profile
GET    /api/session/{id}/summary # Get session summary
POST   /api/teacher/override     # Teacher correction
WS     /ws/chat/{student_id}     # WebSocket chat
GET    /api/topics               # Available topics
GET    /api/health               # Health check
```

**Features**:
- REST API for synchronous operations
- WebSocket for real-time chat
- Request validation with Pydantic
- Rate limiting
- CORS middleware
- Error handling and logging

### 3. Agent Orchestrator

**Purpose**: Core agentic reasoning engine that coordinates tools and manages conversation flow.

**Key Responsibilities**:

1. **Planning & Reasoning**
   - Interprets student questions
   - Determines appropriate teaching strategy
   - Plans multi-turn learning paths
   - Adapts to student level

2. **Tool Selection**
   - Decides which tools to use (web search, knowledge base, memory)
   - Coordinates tool execution
   - Synthesizes results from multiple tools

3. **Context Management**
   - Maintains conversation history
   - Tracks student progress
   - Retrieves relevant past interactions
   - Manages session state

**Agent Loop**:
```python
while conversation_active:
    1. Receive student message
    2. Retrieve context (history, profile, learned topics)
    3. Determine if tools needed (search for current info?)
    4. Plan response strategy
    5. Execute tools if needed
    6. Generate response with Claude
    7. Update learning graph
    8. Store interaction
    9. Update analytics
```

### 4. Claude Integration (LLM)

**Model**: Claude Sonnet 4.5 (`claude-sonnet-4-20250514`)

**Why Claude**:
- Excellent reasoning capabilities
- Strong instruction following
- Good with educational content
- Cost-effective for scaling
- Good safety characteristics

**Prompt Engineering**:
```python
system_prompt = f"""
You are an Educational AI Agent for underprivileged learners.

Student Context:
- Level: {student_level}
- Progress: {progress}%
- Learned Topics: {topics}

Recent Conversation:
{conversation_history}

Guidelines:
{educational_guidelines}
"""
```

**Token Management**:
- Context window: ~200K tokens
- Typical usage: 2K-4K tokens per interaction
- Caching for system prompts (future optimization)

### 5. Tool System (MCP-Compatible)

**Web Search Tool**
- Searches for current AI news and developments
- Uses Brave Search API
- Falls back to simulated results for demo
- Triggered by keywords: "latest", "recent", "current", "2024", "2025"

**Memory Tool**
- Retrieves similar past interactions
- Stores successful explanations
- Vector similarity search (future: using embeddings)
- Helps maintain consistency in teaching

**Analytics Tool**
- Records interaction events
- Generates progress summaries
- Creates learning graphs
- Tracks topics explored

**Knowledge Base Tool**
- Curated educational content
- Topic-specific exercises
- Level-appropriate materials
- Code examples and analogies

**Tool Schema (MCP)**:
```python
{
    'name': 'web_search',
    'description': 'Search web for current AI information',
    'parameters': {
        'query': {'type': 'string', 'required': True},
        'num_results': {'type': 'integer', 'default': 5}
    }
}
```

### 6. Memory System

**Two-Tier Storage**:

**Short-term (Redis)**:
- Session state
- Conversation history (last 50 messages)
- Real-time analytics
- Cache for frequent queries
- TTL: Session duration (60 min default)

**Long-term (PostgreSQL)**:
- Student profiles
- Learning history
- Progress tracking
- Achievement records
- Persistent across sessions

**Session Manager**:
```python
class SessionManager:
    - add_message()      # Store conversation
    - get_recent()       # Retrieve context
    - get_summary()      # Session statistics
    - export_session()   # For analysis
```

**Profile Manager**:
```python
class StudentProfileManager:
    - get_or_create_profile()
    - update_profile()
    - add_topic()
    - track_progress()
    - get_recommendations()
```

### 7. Learning Graph System

**Purpose**: Implements "Build Long-Term Learning Graphs" from flowchart.

**Tracks**:
- Topics learned over time
- Skill progression
- Knowledge dependencies
- Learning patterns
- Areas needing reinforcement

**Graph Structure**:
```
Student Progress Graph:
{
    'student_id': 'abc123',
    'timeline': [
        {
            'date': '2024-11-01',
            'topics': ['Machine Learning'],
            'interactions': 5,
            'progress': 15
        },
        {
            'date': '2024-11-02',
            'topics': ['Neural Networks', 'ML'],
            'interactions': 8,
            'progress': 30
        }
    ],
    'topic_mastery': {
        'Machine Learning': 0.7,
        'Neural Networks': 0.4
    }
}
```

## Data Flow

### Request Flow

1. **Student sends message**
   ```
   Student → Frontend → WebSocket/API → FastAPI
   ```

2. **API processes request**
   ```
   FastAPI → Validation → Agent Orchestrator
   ```

3. **Agent reasoning**
   ```
   Orchestrator → Context Retrieval → Tool Selection → Claude API
   ```

4. **Response generation**
   ```
   Claude → Orchestrator → Updates (Profile, Session, Analytics)
   ```

5. **Response delivered**
   ```
   Orchestrator → FastAPI → Frontend → Student
   ```

### Flowchart Implementation

The system implements all four steps from the provided flowchart:

**1. Integrate AI with Systems**
- Connected to LMS-like student profile system
- Integration with educational content database
- API-first design for easy integration
- MCP-compatible tool interfaces

**2. Collect Data in Real Time**
- Every interaction captured in SessionManager
- Real-time feedback on student understanding
- Immediate adaptation to student responses
- Session analytics updated continuously

**3. Maintain Human Control**
- Teacher override endpoint (`/api/teacher/override`)
- Dashboard for educators (future feature)
- Ability to review and correct AI responses
- Transparency in AI decision-making

**4. Build Long-Term Learning Graphs**
- StudentProfileManager tracks progress over time
- Analytics tool generates learning graphs
- Topic mastery tracked across sessions
- Personalized recommendations based on history

## Scalability

### Horizontal Scaling

**Backend**:
- Stateless API design
- Session data in Redis (shared state)
- Load balancer distributes requests
- Can scale to N instances

**Database**:
- PostgreSQL read replicas
- Redis cluster for session data
- Database connection pooling
- Caching layer

### Performance Optimizations

1. **Caching**:
   - Response caching for common queries
   - Profile caching in Redis
   - Static content CDN

2. **Async Processing**:
   - FastAPI async endpoints
   - Background tasks for analytics
   - Batch database updates

3. **Database**:
   - Indexed queries
   - Optimized schema
   - Partitioned tables for history

4. **Claude API**:
   - Request batching where possible
   - Response streaming
   - Prompt caching (future)

## Security

### Authentication & Authorization
- JWT tokens for API access
- Session-based auth for students
- Teacher role-based access control
- API key authentication

### Data Protection
- HTTPS/TLS encryption
- Database encryption at rest
- PII handling compliance
- Student data privacy (FERPA, COPPA)

### Rate Limiting
- Per-user limits
- IP-based throttling
- Cost protection
- DDoS prevention

## Monitoring & Observability

### Metrics
- API response times
- Claude API usage/costs
- Database query performance
- Error rates
- User engagement

### Logging
- Structured JSON logs
- Error tracking (Sentry)
- Audit logs for teacher actions
- Student privacy-compliant logging

### Dashboards
- Grafana for metrics
- Custom teacher dashboard
- Student progress visualization
- System health monitoring

## Deployment

### Development
```bash
docker-compose up
```

### Production
- Container orchestration (Kubernetes/ECS)
- Auto-scaling based on load
- Blue-green deployments
- Health checks and automatic restarts

## Future Enhancements

### Technical
- Vector database for semantic search
- Prompt caching for efficiency
- Multi-modal support (voice, images)
- Offline-first architecture
- Edge deployment for low-latency

### Features
- Multi-language support
- Voice interaction
- Peer learning (group sessions)
- Gamification and achievements
- Parent/guardian dashboard
- Integration with popular LMS platforms

### AI Capabilities
- Fine-tuned models for education
- Personalized learning paths
- Automatic assessment generation
- Adaptive difficulty adjustment
- Multimodal explanations (text + diagrams)

## Design Decisions

### Why This Architecture?

1. **Microservices Approach**: Separates concerns, allows independent scaling
2. **Agentic Design**: Enables autonomous decision-making and tool use
3. **Two-tier Storage**: Balances performance and persistence
4. **API-First**: Enables multiple frontends (web, mobile, API clients)
5. **MCP-Compatible Tools**: Standard interfaces for tool interoperability
6. **Event-Driven Analytics**: Real-time insights without blocking requests

### Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Claude Sonnet 4.5 | Strong reasoning, cost-effective | API dependency |
| PostgreSQL | Reliable, full-featured | Requires management |
| Redis | Fast session management | Additional service |
| Docker | Easy deployment | Learning curve |
| React | Rich ecosystem | Bundle size |

## Conclusion

This architecture provides a robust, scalable foundation for delivering AI education to millions of students. The agentic design enables adaptive, personalized learning while maintaining transparency and human oversight. The modular structure allows for easy extension and integration with existing educational systems.
