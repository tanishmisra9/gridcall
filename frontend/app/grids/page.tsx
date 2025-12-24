'use client';

import { useState, useEffect } from 'react';
import { createGrid, joinGrid, getMyGrids, Grid } from '@/lib/api';
import Link from 'next/link';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';

function GridsContent() {
  const { user } = useAuth();
  const [grids, setGrids] = useState<Grid[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Create grid form
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newGridName, setNewGridName] = useState('');
  const [creating, setCreating] = useState(false);
  
  // Join grid form
  const [showJoinForm, setShowJoinForm] = useState(false);
  const [inviteCode, setInviteCode] = useState('');
  const [joining, setJoining] = useState(false);

  useEffect(() => {
    loadGrids();
  }, []);

  const loadGrids = async () => {
    try {
      const data = await getMyGrids();
      setGrids(data);
    } catch (err: any) {
      // No grids yet is okay
      setGrids([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGrid = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setError('');
    setSuccess('');

    try {
      const grid = await createGrid(newGridName);
      setGrids([...grids, grid]);
      setNewGridName('');
      setShowCreateForm(false);
      setSuccess(`Grid "${grid.name}" created! Share code: ${grid.invite_code}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create grid');
    } finally {
      setCreating(false);
    }
  };

  const handleJoinGrid = async (e: React.FormEvent) => {
    e.preventDefault();
    setJoining(true);
    setError('');
    setSuccess('');

    try {
      const grid = await joinGrid(inviteCode);
      setGrids([...grids, grid]);
      setInviteCode('');
      setShowJoinForm(false);
      setSuccess(`Successfully joined "${grid.name}"!`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to join grid');
    } finally {
      setJoining(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
          ← Back to home
        </Link>
        
        <h1 className="text-3xl font-bold mb-6 text-black">Your Grids</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => { setShowCreateForm(!showCreateForm); setShowJoinForm(false); }}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
          >
            Create Grid
          </button>
          <button
            onClick={() => { setShowJoinForm(!showJoinForm); setShowCreateForm(false); }}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
          >
            Join Grid
          </button>
        </div>

        {/* Create grid form */}
        {showCreateForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-black">Create a New Grid</h2>
            <form onSubmit={handleCreateGrid} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-black">Grid Name</label>
                <input
                  type="text"
                  value={newGridName}
                  onChange={(e) => setNewGridName(e.target.value)}
                  placeholder="e.g., Office F1 League"
                  className="w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={creating}
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {creating ? 'Creating...' : 'Create'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="bg-gray-200 text-black px-4 py-2 rounded hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Join grid form */}
        {showJoinForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-black">Join a Grid</h2>
            <form onSubmit={handleJoinGrid} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-black">Invite Code</label>
                <input
                  type="text"
                  value={inviteCode}
                  onChange={(e) => setInviteCode(e.target.value)}
                  placeholder="Enter invite code"
                  className="w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={joining}
                  className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:bg-gray-400"
                >
                  {joining ? 'Joining...' : 'Join'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowJoinForm(false)}
                  className="bg-gray-200 text-black px-4 py-2 rounded hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Grids list */}
        {grids.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600 mb-2">You haven&apos;t joined any grids yet.</p>
            <p className="text-gray-500 text-sm">Create a new grid or join one with an invite code!</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {grids.map((grid) => (
              <div key={grid.id} className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-semibold text-black mb-2">{grid.name}</h3>
                <p className="text-gray-600 mb-2">{grid.member_count} member{grid.member_count !== 1 ? 's' : ''}</p>
                <div className="bg-gray-100 p-2 rounded">
                  <p className="text-xs text-gray-500">Invite Code:</p>
                  <p className="font-mono text-sm text-black select-all">{grid.invite_code}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function GridsPage() {
  return (
    <ProtectedRoute>
      <GridsContent />
    </ProtectedRoute>
  );
}
