/**
 * Course detail page for instructors - manage materials, policies, and analytics
 */
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  coursesAPI,
  materialsAPI,
  policiesAPI,
  qaAPI,
  analyticsAPI,
} from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import CitationBadge from '../components/CitationBadge';
import Navbar from '../components/Navbar';

const CourseDetail = () => {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [materials, setMaterials] = useState([]);
  const [policy, setPolicy] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [activeTab, setActiveTab] = useState('materials');
  const [loading, setLoading] = useState(true);

  // Material upload state
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState('');

  // Policy form state
  const [policyForm, setPolicyForm] = useState({
    persona: 'friendly',
    allowed_topics: '',
    disallowed_actions: '',
    custom_instructions: '',
  });

  // Test query state
  const [testQuestion, setTestQuestion] = useState('');
  const [testAnswer, setTestAnswer] = useState(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    loadCourseData();
  }, [courseId]);

  const loadCourseData = async () => {
    try {
      const [courseRes, materialsRes] = await Promise.all([
        coursesAPI.get(courseId),
        materialsAPI.list(courseId),
      ]);

      setCourse(courseRes.data);
      setMaterials(materialsRes.data);

      // Load policy if exists
      try {
        const policyRes = await policiesAPI.get(courseId);
        setPolicy(policyRes.data);
        setPolicyForm({
          persona: policyRes.data.persona,
          allowed_topics: policyRes.data.allowed_topics || '',
          disallowed_actions: policyRes.data.disallowed_actions || '',
          custom_instructions: policyRes.data.custom_instructions || '',
        });
      } catch (e) {
        // Policy doesn't exist yet
      }

      // Load analytics
      try {
        const analyticsRes = await analyticsAPI.get(courseId);
        setAnalytics(analyticsRes.data);
      } catch (e) {
        console.error('Error loading analytics:', e);
      }
    } catch (error) {
      console.error('Error loading course data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
      alert('Please upload a PDF file');
      return;
    }

    const fileType = prompt(
      'Select material type:\n1. syllabus\n2. lecture\n3. assignment\n4. transcript',
      'lecture'
    );

    if (!['syllabus', 'lecture', 'assignment', 'transcript'].includes(fileType)) {
      alert('Invalid file type');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);

    setUploading(true);
    setUploadProgress('Uploading...');

    try {
      await materialsAPI.upload(courseId, formData);
      setUploadProgress('Processing PDF...');

      // Reload materials after a short delay to allow processing
      setTimeout(async () => {
        const materialsRes = await materialsAPI.list(courseId);
        setMaterials(materialsRes.data);
        setUploading(false);
        setUploadProgress('');
        e.target.value = ''; // Reset file input
      }, 2000);
    } catch (error) {
      console.error('Error uploading material:', error);
      alert('Failed to upload material');
      setUploading(false);
      setUploadProgress('');
    }
  };

  const handleDeleteMaterial = async (materialId) => {
    if (!window.confirm('Are you sure you want to delete this material?')) {
      return;
    }

    try {
      await materialsAPI.delete(materialId);
      const materialsRes = await materialsAPI.list(courseId);
      setMaterials(materialsRes.data);
    } catch (error) {
      console.error('Error deleting material:', error);
      alert('Failed to delete material');
    }
  };

  const handleSavePolicy = async (e) => {
    e.preventDefault();
    try {
      const response = await policiesAPI.update(courseId, policyForm);
      setPolicy(response.data);
      alert('Policy saved successfully!');
    } catch (error) {
      console.error('Error saving policy:', error);
      alert('Failed to save policy');
    }
  };

  const handleTestQuery = async (e) => {
    e.preventDefault();
    if (!testQuestion.trim()) return;

    setTesting(true);
    setTestAnswer(null);

    try {
      const response = await qaAPI.ask(courseId, testQuestion);
      setTestAnswer(response.data);
    } catch (error) {
      console.error('Error testing query:', error);
      alert('Failed to test query');
    } finally {
      setTesting(false);
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

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/instructor"
            className="text-blue-600 hover:text-blue-700 mb-4 inline-block"
          >
            ← Back to Courses
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">{course?.name}</h1>
          <p className="text-gray-600">{course?.term}</p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <div className="flex gap-8">
            {['materials', 'policies', 'simulator', 'analytics'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-3 px-1 font-medium capitalize border-b-2 transition-colors ${
                  activeTab === tab
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Materials Tab */}
        {activeTab === 'materials' && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Course Materials
              </h2>
              <label className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 cursor-pointer transition-colors">
                + Upload PDF
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  className="hidden"
                />
              </label>
            </div>

            {uploading && (
              <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <LoadingSpinner size="sm" text={uploadProgress} />
              </div>
            )}

            {materials.length === 0 ? (
              <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
                <div className="text-4xl mb-2">📄</div>
                <p className="text-gray-600">No materials uploaded yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {materials.map((material) => (
                  <div
                    key={material.id}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <span className="text-2xl">📄</span>
                      <div>
                        <div className="font-medium text-gray-900">
                          {material.filename}
                        </div>
                        <div className="text-sm text-gray-600">
                          Type: {material.file_type} • Chunks:{' '}
                          {material.chunk_count || 0} •{' '}
                          {material.processed ? (
                            <span className="text-green-600">Processed ✓</span>
                          ) : (
                            <span className="text-yellow-600">Processing...</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDeleteMaterial(material.id)}
                      className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg font-medium"
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Policies Tab */}
        {activeTab === 'policies' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">
              AI TA Configuration
            </h2>

            <form onSubmit={handleSavePolicy} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  AI Persona
                </label>
                <select
                  value={policyForm.persona}
                  onChange={(e) =>
                    setPolicyForm({ ...policyForm, persona: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="friendly">Friendly & Encouraging</option>
                  <option value="policy_first">Strict & Policy-Focused</option>
                  <option value="scaffolded">Socratic & Guiding</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Allowed Topics
                </label>
                <textarea
                  value={policyForm.allowed_topics}
                  onChange={(e) =>
                    setPolicyForm({
                      ...policyForm,
                      allowed_topics: e.target.value,
                    })
                  }
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Course concepts, assignment clarifications, exam preparation"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Disallowed Actions
                </label>
                <textarea
                  value={policyForm.disallowed_actions}
                  onChange={(e) =>
                    setPolicyForm({
                      ...policyForm,
                      disallowed_actions: e.target.value,
                    })
                  }
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Providing complete assignment solutions, sharing exam answers"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Custom Instructions (Optional)
                </label>
                <textarea
                  value={policyForm.custom_instructions}
                  onChange={(e) =>
                    setPolicyForm({
                      ...policyForm,
                      custom_instructions: e.target.value,
                    })
                  }
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Any additional instructions for the AI TA..."
                />
              </div>

              <button
                type="submit"
                className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
              >
                Save Policy
              </button>
            </form>
          </div>
        )}

        {/* Simulator Tab */}
        {activeTab === 'simulator' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">
              TA Simulator
            </h2>
            <p className="text-gray-600 mb-6">
              Test how the AI TA will respond to student questions
            </p>

            <form onSubmit={handleTestQuery} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Test Question
                </label>
                <textarea
                  value={testQuestion}
                  onChange={(e) => setTestQuestion(e.target.value)}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Ask a question..."
                  required
                />
              </div>

              <button
                type="submit"
                disabled={testing}
                className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {testing ? <LoadingSpinner size="sm" /> : 'Test Query'}
              </button>
            </form>

            {testAnswer && (
              <div className="mt-6 p-6 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-2xl">🤖</span>
                  <h3 className="font-bold text-gray-900">AI TA Response</h3>
                  {testAnswer.was_refused && (
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs font-medium rounded">
                      Refused
                    </span>
                  )}
                </div>

                <div className="prose max-w-none mb-4">
                  <p className="text-gray-900 whitespace-pre-wrap">
                    {testAnswer.answer}
                  </p>
                </div>

                {testAnswer.sources && testAnswer.sources.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-700 mb-2">
                      Sources:
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {testAnswer.sources.map((source, idx) => (
                        <CitationBadge key={idx} source={source} index={idx} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm font-medium text-gray-600 mb-1">
                  Total Questions
                </div>
                <div className="text-3xl font-bold text-gray-900">
                  {analytics?.total_questions || 0}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm font-medium text-gray-600 mb-1">
                  Refusals
                </div>
                <div className="text-3xl font-bold text-gray-900">
                  {analytics?.refusal_count || 0}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm font-medium text-gray-600 mb-1">
                  Refusal Rate
                </div>
                <div className="text-3xl font-bold text-gray-900">
                  {analytics?.refusal_rate || 0}%
                </div>
              </div>
            </div>

            {/* Recent Questions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Recent Questions
              </h3>

              {analytics?.recent_questions?.length === 0 ? (
                <p className="text-gray-600">No questions yet</p>
              ) : (
                <div className="space-y-4">
                  {analytics?.recent_questions?.map((log) => (
                    <div
                      key={log.id}
                      className="p-4 border border-gray-200 rounded-lg"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div className="font-medium text-gray-900">
                          Q: {log.question_text}
                        </div>
                        {log.was_refused && (
                          <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs font-medium rounded">
                            Refused
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-600">
                        A: {log.answer_text.substring(0, 150)}...
                      </div>
                      <div className="text-xs text-gray-500 mt-2">
                        {new Date(log.created_at).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CourseDetail;
