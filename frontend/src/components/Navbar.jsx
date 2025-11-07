/**
 * Navigation bar component
 */
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout, isInstructor } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  return (
    <nav className="bg-white shadow-md border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Title */}
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-2">
              <span className="text-2xl">🎓</span>
              <span className="text-xl font-bold text-gray-900">
                AI TA Platform
              </span>
            </Link>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center gap-6">
            {isInstructor ? (
              <Link
                to="/instructor"
                className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
              >
                My Courses
              </Link>
            ) : (
              <Link
                to="/student"
                className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
              >
                Browse Courses
              </Link>
            )}

            {/* User Info and Logout */}
            <div className="flex items-center gap-4 border-l pl-4">
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">
                  {user.name}
                </div>
                <div className="text-xs text-gray-500 capitalize">
                  {user.role}
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
