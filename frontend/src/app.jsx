import React, { useState, useEffect, useRef } from 'react';
import { BookOpen, Send, User, Bot, Loader, TrendingUp, Award, Target } from 'lucide-react';

const EducationalAIAgent = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m your AI Learning Assistant. I\'m here to help you learn about artificial intelligence and its latest features. What would you like to learn today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [learnerProfile, setLearnerProfile] = useState({
    name: 'Student',
    level: 'Beginner',
    progress: 0,
    topics: []
  });
  const [sessionData, setSessionData] = useState({
    questionsAsked: 0,
    topicsExplored: [],
    sessionTime: 0
  });
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const timer = setInterval(() => {
      setSessionData(prev => ({ ...prev, sessionTime: prev.sessionTime + 1 }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const aiTopics = [
    { name: 'Machine Learning Basics', keywords: ['machine learning', 'ml', 'training', 'model'] },
    { name: 'Neural Networks', keywords: ['neural', 'network', 'deep learning', 'neurons'] },
    { name: 'Natural Language Processing', keywords: ['nlp', 'language', 'text', 'chatbot'] },
    { name: 'Computer Vision', keywords: ['vision', 'image', 'recognition', 'detection'] },
    { name: 'AI Ethics', keywords: ['ethics', 'bias', 'fairness', 'responsible'] },
    { name: 'Generative AI', keywords: ['generative', 'gpt', 'llm', 'generate'] },
  ];

  const generateResponse = async (userMessage) => {
    const lowerMsg = userMessage.toLowerCase();
    
    // Detect topic
    let detectedTopic = null;
    for (const topic of aiTopics) {
      if (topic.keywords.some(kw => lowerMsg.includes(kw))) {
        detectedTopic = topic.name;
        break;
      }
    }

    if (detectedTopic && !sessionData.topicsExplored.includes(detectedTopic)) {
      setSessionData(prev => ({
        ...prev,
        topicsExplored: [...prev.topicsExplored, detectedTopic]
      }));
      setLearnerProfile(prev => ({
        ...prev,
        progress: Math.min(100, prev.progress + 15),
        topics: [...new Set([...prev.topics, detectedTopic])]
      }));
    }

    // Simulate AI processing
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Generate contextual responses based on topics
    if (lowerMsg.includes('machine learning') || lowerMsg.includes('ml')) {
      return "Machine Learning is a subset of AI where computers learn from data without being explicitly programmed. Think of it like teaching a child to recognize animals - you show them examples, and they learn patterns. There are three main types:\n\n1. **Supervised Learning**: Learning from labeled examples (like flashcards)\n2. **Unsupervised Learning**: Finding patterns in unlabeled data\n3. **Reinforcement Learning**: Learning through trial and error\n\nWould you like to explore any of these in more detail?";
    }
    
    if (lowerMsg.includes('neural') || lowerMsg.includes('deep learning')) {
      return "Neural Networks are inspired by the human brain! They consist of layers of interconnected 'neurons' that process information. Imagine water flowing through a series of filters - each layer extracts different features.\n\n**Key Concepts:**\n- Input Layer: Receives raw data\n- Hidden Layers: Process and transform data\n- Output Layer: Makes predictions\n\nDeep Learning uses many hidden layers, allowing it to learn complex patterns. This is what powers things like image recognition and language translation!";
    }
    
    if (lowerMsg.includes('nlp') || lowerMsg.includes('language')) {
      return "Natural Language Processing (NLP) helps computers understand human language! It's what allows chatbots, translators, and voice assistants to work.\n\n**Cool Applications:**\n- Chatbots (like me!)\n- Language translation\n- Sentiment analysis (understanding emotions in text)\n- Text summarization\n\nRecent advances like GPT models have revolutionized NLP by understanding context much better than before!";
    }
    
    if (lowerMsg.includes('vision') || lowerMsg.includes('image')) {
      return "Computer Vision teaches computers to 'see' and understand images! It's used in:\n\n- Facial recognition\n- Self-driving cars\n- Medical image analysis\n- Object detection\n\nModern computer vision uses Convolutional Neural Networks (CNNs) that learn to recognize features like edges, shapes, and textures automatically!";
    }
    
    if (lowerMsg.includes('ethics') || lowerMsg.includes('bias')) {
      return "AI Ethics is crucial! As AI becomes more powerful, we must ensure it's fair and beneficial. Key concerns include:\n\n1. **Bias**: AI can inherit human biases from training data\n2. **Privacy**: Protecting personal information\n3. **Transparency**: Understanding how AI makes decisions\n4. **Accessibility**: Ensuring AI benefits everyone, not just the privileged\n\nRemember: AI should empower people, not replace human judgment in critical decisions!";
    }
    
    if (lowerMsg.includes('generative') || lowerMsg.includes('gpt') || lowerMsg.includes('llm')) {
      return "Generative AI creates new content - text, images, music, and more! Large Language Models (LLMs) like GPT are trained on massive amounts of text to understand and generate human-like responses.\n\n**How it works:**\n1. Training on billions of text examples\n2. Learning patterns and relationships\n3. Predicting what comes next\n\n**Applications:**\n- Writing assistance\n- Code generation\n- Creative content\n- Education (like this conversation!)\n\nThese models are democratizing access to knowledge and creativity!";
    }
    
    if (lowerMsg.includes('start') || lowerMsg.includes('begin') || lowerMsg.includes('learn')) {
      return "Great! Let's start your AI journey. Here are beginner-friendly topics:\n\n1. **What is AI?** - Understanding the basics\n2. **Machine Learning** - How computers learn\n3. **Real-world Applications** - AI in daily life\n4. **Getting Started with Coding** - Python basics for AI\n\nWhich topic interests you most? Or ask me anything specific!";
    }

    return "That's a great question! AI is a vast and exciting field. I can help you learn about:\n\n- Machine Learning fundamentals\n- Neural Networks and Deep Learning\n- Natural Language Processing\n- Computer Vision\n- AI Ethics and Responsible AI\n- Generative AI and LLMs\n\nWhat specific aspect would you like to explore? Feel free to ask anything!";
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setIsLoading(true);
    setSessionData(prev => ({ ...prev, questionsAsked: prev.questionsAsked + 1 }));

    const response = await generateResponse(userMessage);
    
    setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    setIsLoading(false);
  };

  const formatTime = (seconds) => {
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
          <div className="flex items-center justify-between">
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

export default EducationalAIAgent;
