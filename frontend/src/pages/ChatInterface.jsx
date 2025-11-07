/**
 * Chat interface for students to ask questions
 */
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { coursesAPI, qaAPI } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import CitationBadge from '../components/CitationBadge';
import Navbar from '../components/Navbar';

const ChatInterface = () => {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [question, setQuestion] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(true);
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    loadCourse();
  }, [courseId]);

  const loadCourse = async () => {
    try {
      const response = await coursesAPI.get(courseId);
      setCourse(response.data);
    } catch (error) {
      console.error('Error loading course:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAskQuestion = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userMessage = {
      type: 'question',
      text: question,
      timestamp: new Date(),
    };

    setConversation([...conversation, userMessage]);
    setQuestion('');
    setAsking(true);

    try {
      const response = await qaAPI.ask(courseId, question);
      const answer = response.data;

      const aiMessage = {
        type: 'answer',
        text: answer.answer,
        sources: answer.sources,
        was_refused: answer.was_refused,
        timestamp: new Date(),
      };

      setConversation((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error asking question:', error);
      const errorMessage = {
        type: 'error',
        text: 'Sorry, I encountered an error processing your question. Please try again.',
        timestamp: new Date(),
      };
      setConversation((prev) => [...prev, errorMessage]);
    } finally {
      setAsking(false);
    }
  };

  const handleNewConversation = () => {
    if (window.confirm('Start a new conversation? Current history will be lost.')) {
      setConversation([]);
      setQuestion('');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" text="Loading course..." />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <Link
            to="/student"
            className="text-blue-600 hover:text-blue-700 mb-4 inline-block"
          >
            ← Back to Courses
          </Link>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{course?.name}</h1>
              <p className="text-gray-600">{course?.term}</p>
            </div>
            {conversation.length > 0 && (
              <button
                onClick={handleNewConversation}
                className="px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 transition-colors"
              >
                New Conversation
              </button>
            )}
          </div>
        </div>

        {/* Chat Container */}
        <div className="bg-white rounded-lg shadow-lg">
          {/* Conversation History */}
          <div className="h-[500px] overflow-y-auto p-6 space-y-6">
            {conversation.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🤖</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  AI Teaching Assistant
                </h3>
                <p className="text-gray-600">
                  Ask me anything about {course?.name}!
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  I'll answer based on course materials with citations.
                </p>
              </div>
            ) : (
              conversation.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.type === 'question' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.type === 'question' ? (
                    // User Question
                    <div className="max-w-[70%] bg-blue-600 text-white rounded-lg p-4">
                      <div className="font-medium mb-1">You</div>
                      <div className="whitespace-pre-wrap">{message.text}</div>
                      <div className="text-xs text-blue-100 mt-2">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  ) : message.type === 'error' ? (
                    // Error Message
                    <div className="max-w-[80%] bg-red-50 border border-red-200 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xl">⚠️</span>
                        <span className="font-medium text-red-900">Error</span>
                      </div>
                      <div className="text-red-700">{message.text}</div>
                    </div>
                  ) : (
                    // AI Answer
                    <div className="max-w-[80%] bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-xl">🤖</span>
                        <span className="font-medium text-gray-900">
                          AI Teaching Assistant
                        </span>
                        {message.was_refused && (
                          <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs font-medium rounded">
                            Policy Violation
                          </span>
                        )}
                      </div>

                      <div className="prose max-w-none mb-4">
                        <p className="text-gray-900 whitespace-pre-wrap">
                          {message.text}
                        </p>
                      </div>

                      {message.sources && message.sources.length > 0 && (
                        <div className="border-t border-gray-200 pt-3 mt-3">
                          <div className="text-sm font-semibold text-gray-700 mb-2">
                            📚 Sources:
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {message.sources.map((source, idx) => (
                              <CitationBadge key={idx} source={source} index={idx} />
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="text-xs text-gray-500 mt-3">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}

            {asking && (
              <div className="flex justify-start">
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center gap-3">
                    <LoadingSpinner size="sm" />
                    <span className="text-gray-600">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input Form */}
          <div className="border-t border-gray-200 p-4 bg-gray-50">
            <form onSubmit={handleAskQuestion} className="flex gap-3">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about the course..."
                rows={2}
                disabled={asking}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleAskQuestion(e);
                  }
                }}
              />
              <button
                type="submit"
                disabled={asking || !question.trim()}
                className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors self-end"
              >
                {asking ? <LoadingSpinner size="sm" /> : 'Send'}
              </button>
            </form>
            <p className="text-xs text-gray-500 mt-2">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </div>

        {/* Course Info Card */}
        {(course?.late_policy || course?.office_hours) && (
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">Course Information</h3>
            {course.office_hours && (
              <p className="text-sm text-blue-800 mb-1">
                🕐 Office Hours: {course.office_hours}
              </p>
            )}
            {course.location && (
              <p className="text-sm text-blue-800 mb-1">
                📍 Location: {course.location}
              </p>
            )}
            {course.late_policy && (
              <div className="mt-2">
                <p className="text-sm font-medium text-blue-900">Late Policy:</p>
                <p className="text-sm text-blue-800">{course.late_policy}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
