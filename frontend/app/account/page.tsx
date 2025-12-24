'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/ProtectedRoute';
import api from '@/lib/api';

function AccountContent() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState('');
  const [userDetails, setUserDetails] = useState<{ created_at: string } | null>(null);

  const DELETE_CONFIRMATION = "I would like to delete my account.";

  useEffect(() => {
    loadUserDetails();
  }, []);

  const loadUserDetails = async () => {
    try {
      const response = await api.get('/api/users/me/details');
      setUserDetails(response.data);
    } catch (err) {
      // If endpoint doesn't exist yet, that's okay
      console.log('Could not load user details');
    }
  };

  const formatMemberSince = (dateString: string | undefined) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== DELETE_CONFIRMATION) {
      setError('Please type the confirmation text exactly as shown.');
      return;
    }

    setDeleting(true);
    setError('');

    try {
      await api.delete('/api/users/me');
      logout();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete account');
      setDeleting(false);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-2xl mx-auto">
        <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
          ← Back to home
        </Link>

        <h1 className="text-3xl font-bold mb-6 text-black">Account Settings</h1>

        {/* User Info Card */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-black">Profile Information</h2>
          
          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Username</span>
              <span className="font-medium text-black">{user?.username}</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Email</span>
              <span className="font-medium text-black">{user?.email}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-gray-600">Member since</span>
              <span className="font-medium text-black">
                {formatMemberSince(userDetails?.created_at)}
              </span>
            </div>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="bg-white rounded-lg shadow p-6 border-2 border-red-200">
          <h2 className="text-xl font-semibold mb-4 text-red-600">Danger Zone</h2>
          
          {!showDeleteConfirm ? (
            <div>
              <p className="text-gray-600 mb-4">
                Once you delete your account, there is no going back. All your predictions and data will be permanently removed.
              </p>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
              >
                Delete Account
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-gray-600">
                To confirm deletion, please type the following exactly:
              </p>
              <p className="font-mono bg-gray-100 p-2 rounded text-black">
                {DELETE_CONFIRMATION}
              </p>
              
              <input
                type="text"
                value={deleteConfirmText}
                onChange={(e) => setDeleteConfirmText(e.target.value)}
                placeholder="Type the confirmation text..."
                className="w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-red-500"
              />

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                  {error}
                </div>
              )}

              <div className="flex gap-3">
                <button
                  onClick={handleDeleteAccount}
                  disabled={deleting || deleteConfirmText !== DELETE_CONFIRMATION}
                  className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 disabled:bg-gray-400 transition-colors"
                >
                  {deleting ? 'Deleting...' : 'Permanently Delete Account'}
                </button>
                <button
                  onClick={() => {
                    setShowDeleteConfirm(false);
                    setDeleteConfirmText('');
                    setError('');
                  }}
                  className="bg-gray-200 text-black px-4 py-2 rounded hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function AccountPage() {
  return (
    <ProtectedRoute>
      <AccountContent />
    </ProtectedRoute>
  );
}