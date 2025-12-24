'use client';

import { useEffect, useState } from 'react';
import { getUpcomingRaces, getMyPrediction, UpcomingRace } from '@/lib/api';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';

function HomeContent() {
  const { user, logout } = useAuth();
  const [races, setRaces] = useState<UpcomingRace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [hasPredictions, setHasPredictions] = useState<{ [key: number]: boolean }>({});

  useEffect(() => {
    loadRaces();
  }, []);

  const loadRaces = async () => {
    try {
      const data = await getUpcomingRaces();
      setRaces(data);
      
      // Check which races have predictions
      const predictions: { [key: number]: boolean } = {};
      for (const race of data) {
        try {
          await getMyPrediction(race.id);
          predictions[race.id] = true;
        } catch {
          predictions[race.id] = false;
        }
      }
      setHasPredictions(predictions);
    } catch (err: any) {
      setError('Failed to load races');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Loading races...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-xl text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        {/* Header with user info */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-5xl font-bold mb-2 text-black">Gridcall</h1>
            <p className="text-2xl text-gray-600">&quot;Prove you know the grid.&quot;</p>
          </div>
          <div className="text-right">
            <p className="text-gray-600 mb-2">
              Welcome,{' '}
              <Link 
                href="/account" 
                className="font-semibold text-blue-600 hover:underline"
              >
                {user?.username}
              </Link>
            </p>
            <button
              onClick={logout}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              Logout
            </button>
          </div>
        </div>

        <h2 className="text-3xl font-semibold mb-6 text-black">Upcoming Races</h2>

        {races.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600">No upcoming races at the moment.</p>
            <p className="text-gray-500 text-sm mt-2">Check back soon!</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {races.map((race) => (
              <div key={race.id} className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-semibold text-black mb-2">{race.location}</h3>
                <p className="text-gray-600 mb-1">Round {race.round_number}</p>
                <p className="text-gray-500 text-sm mb-4">
                  Race: {new Date(race.race_date).toLocaleDateString()}
                </p>
                
                {race.can_predict ? (
                  <div className="space-y-2">
                    {hasPredictions[race.id] ? (
                      <>
                        <Link
                          href={`/predictions/${race.id}`}
                          className="block w-full bg-green-100 text-green-700 py-2 px-4 rounded text-center hover:bg-green-200"
                        >
                          View Predictions
                        </Link>
                        <Link
                          href={`/edit/${race.id}`}
                          className="block w-full bg-gray-100 text-gray-700 py-2 px-4 rounded text-center hover:bg-gray-200"
                        >
                          Edit Predictions
                        </Link>
                      </>
                    ) : (
                      <Link
                        href={`/predict/${race.id}`}
                        className="block w-full bg-blue-600 text-white py-2 px-4 rounded text-center hover:bg-blue-700"
                      >
                        Make Predictions
                      </Link>
                    )}
                    <p className="text-xs text-gray-500 text-center">
                      Closes: {race.time_until_close}
                    </p>
                  </div>
                ) : (
                  <div className="text-center">
                    <span className="inline-block bg-gray-100 text-gray-500 py-2 px-4 rounded">
                      Predictions Closed
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Grids Section */}
        <div className="mt-12">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-3xl font-semibold text-black">Your Grids</h2>
            <Link
              href="/grids"
              className="text-blue-600 hover:underline"
            >
              Manage Grids
            </Link>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-center">
              Join or create a grid to compete with friends!
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

export default function Home() {
  return (
    <ProtectedRoute>
      <HomeContent />
    </ProtectedRoute>
  );
}