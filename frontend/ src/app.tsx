import React, { useState, useEffect, useRef } from 'react';
import { BookOpen, Send, User, Bot, Loader, Target } from 'lucide-react';
import './App.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  topics?: string[];
}

interface LearnerProfile {
  name: string;
  level: string;
  progress: number;
  topics: string[];
}

interface SessionData {
  questionsAsked: number;
  topicsExplored: string[];
  sessionTime: number;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { 
      role: 'assistant', 
      content: 'Hello! I\'m your AI Learning Assistant. I\'m here to help you learn about artificial intelligence and its latest features. What would you like to learn today?' 
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [studentId] = useState(() => {
    const saved = localStorage.getItem('studentId');
    return saved || `student_${Date.now()}`;
  });
  const [learnerProfile, setLearnerProfile] = useState<LearnerProfile>({
    name: 'Student',
    level: 'Beginner',
    progress: 0,
    topics: []
  });
  const [sessionData, setSessionData] = useState<SessionData>({
    questionsAsked: 0,
    topicsExplored: [],
    sessionTime: 0
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    localStorage.setItem('studentId', studentId);
    fetchProfile();
  }, [studentId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const timer = setInterval(() => {
      setSessionData(prev => ({ ...prev, sessionTime: prev.sessionTime + 1 }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // WebSocket connection (optional - for real-time updates)
  useEffect(() => {
    if (process.env.REACT_APP_USE_WEBSOCKET === 'true') {
      const ws = new WebSocket(`${WS_URL}/ws/chat/${studentId}`);
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'message') {
          handleServerResponse(data.data);
        } else if (data.type === 'progress') {
          updateProfile(data.data);
        }
      };

      wsRef.current = ws;

      return () => {
        ws.close();
      };
    }
  }, [studentId]);

  const fetchProfile = async () => {
    try {
      const response = await fetch(`${API_URL}/api/student/${studentId}/profile`);
      if (response.ok) {
        const data = await response.json();
        setLearnerProfile({
          name: 'Student',
          level: data.level,
          progress: data.progress,
          topics: data.topics || []
        });
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setIsLoading(true);
    setSessionData(prev => ({ ...prev, questionsAsked: prev.questionsAsked + 1 }));

    try {
      // Use REST API
      const response = await fetch(`${API_URL}/api/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_id: studentId,
          message: userMessage,
          allow_web_search: true
        })
      });

      if (response.ok) {
        const data = await response.json();
        handleServerResponse(data);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'I\'m having trouble connecting right now. Please try again in a moment.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleServerResponse = (data: any) => {
    setMessages(prev => [...prev, { 
      role: 'assistant', 
      content: data.message,
      topics: data.topics_detected 
    }]);

    // Update profile
    setLearnerProfile(prev => ({
      ...prev,
      level: data.student_level,
      progress: data.progress,
      topics: [...new Set([...prev.topics, ...(data.topics_detected || [])])]
    }));

    // Update session data
    if (data.topics_detected?.length > 0) {
      setSessionData(prev => ({
        ...prev,
        topicsExplored: [...new Set([...prev.topicsExplored, ...data.topics_detected])]
      }));
    }
  };

  const updateProfile = (data: any) => {
    setLearnerProfile(prev => ({
      ...prev,
      level: data.level || prev.level,
      progress: data.progress || prev.progress,
      topics: data.topics || prev.topics
    }));
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const quickPrompts = [
    "What is Machine Learning?",
    "Explain Neural Networks",
    "How does NLP work?",
    "Tell me about AI Ethics"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <BookOpen className="w-8 h-8 text-indigo-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-800">AI Learning Assistant</h1>
                <p className="text-sm text-gray-600">Free education for everyone, powered by AI</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-600">{sessionData.questionsAsked}</div>
                <div className="text-xs text-gray-600">Questions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{sessionData.topicsExplored.length}</div>
                <div className="text-xs text-gray-600">Topics</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{formatTime(sessionData.sessionTime)}</div>
                <div className="text-xs text-gray-600">Session</div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          {/* Learner Profile */}
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <User className="w-5 h-5" />
                Your Profile
              </h2>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Level</p>
                  <p className="font-semibold text-indigo-600">{learnerProfile.level}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-2">Progress</p>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-indigo-600 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${learnerProfile.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-600 mt-1">{learnerProfile.progress}% Complete</p>
                </div>
                {learnerProfile.topics.length > 0 && (
                  <div>
                    <p className="text-sm text-gray-600 mb-2">Topics Learned</p>
                    <div className="flex flex-wrap gap-1">
                      {learnerProfile.topics.map((topic, idx) => (
                        <span key={idx} className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Target className="w-5 h-5" />
                Quick Topics
              </h2>
              <div className="space-y-2">
                {quickPrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInput(prompt)}
                    className="w-full text-left text-sm p-2 rounded hover:bg-indigo-50 transition-colors text-gray-700"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-3 bg-white rounded-lg shadow-lg flex flex-col" style={{ height: '600px' }}>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  )}
                  <div className={`max-w-2xl rounded-lg p-4 ${
                    msg.role === 'user' 
                      ? 'bg-indigo-600 text-white' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-gray-100 rounded-lg p-4">
                    <Loader className="w-5 h-5 animate-spin text-indigo-600" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t p-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Ask me anything about AI..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                  disabled={isLoading}
                />
                <button
                  onClick={handleSend}
                  disabled={isLoading || !input.trim()}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
