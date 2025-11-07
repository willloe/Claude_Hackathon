/**
 * Main App component with routing
 */
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import InstructorDashboard from './pages/InstructorDashboard';
import CourseDetail from './pages/CourseDetail';
import StudentCourses from './pages/StudentCourses';
import ChatInterface from './pages/ChatInterface';

const AppRoutes = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-6xl mb-4">🎓</div>
          <div className="text-xl font-semibold text-gray-900">
            Loading...
          </div>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={user ? <Navigate to={user.role === 'instructor' ? '/instructor' : '/student'} replace /> : <Login />}
      />
      <Route
        path="/register"
        element={user ? <Navigate to={user.role === 'instructor' ? '/instructor' : '/student'} replace /> : <Register />}
      />

      {/* Instructor Routes */}
      <Route
        path="/instructor"
        element={
          <ProtectedRoute requireInstructor>
            <InstructorDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/instructor/course/:courseId"
        element={
          <ProtectedRoute requireInstructor>
            <CourseDetail />
          </ProtectedRoute>
        }
      />

      {/* Student Routes */}
      <Route
        path="/student"
        element={
          <ProtectedRoute>
            <StudentCourses />
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/chat/:courseId"
        element={
          <ProtectedRoute>
            <ChatInterface />
          </ProtectedRoute>
        }
      />

      {/* Default Route */}
      <Route
        path="/"
        element={
          user ? (
            <Navigate to={user.role === 'instructor' ? '/instructor' : '/student'} replace />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      {/* 404 */}
      <Route
        path="*"
        element={
          <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
              <div className="text-6xl mb-4">404</div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Page Not Found
              </h1>
              <a href="/" className="text-blue-600 hover:text-blue-700">
                Go Home
              </a>
            </div>
          </div>
        }
      />
    </Routes>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
