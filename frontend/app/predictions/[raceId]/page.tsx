'use client';

import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getRace, getMyPrediction, Race, UserPrediction } from '@/lib/api';
import Link from 'next/link';
import ProtectedRoute from '@/components/ProtectedRoute';

function PredictionsContent() {
  const params = useParams();
  const raceId = parseInt(params.raceId as string);
  const [race, setRace] = useState<Race | null>(null);
  const [prediction, setPrediction] = useState<UserPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, [raceId]);

  const loadData = async () => {
    try {
      const [raceData, predictionData] = await Promise.all([
        getRace(raceId),
        getMyPrediction(raceId)
      ]);
      setRace(raceData);
      setPrediction(predictionData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load predictions');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Loading predictions...</p>
        </div>
      </div>
    );
  }

  if (error || !prediction || !race) {
    return (
      <div className="min-h-screen p-8 bg-gray-50">
        <div className="max-w-2xl mx-auto text-center">
          <p className="text-gray-600 mb-4">{error || 'No predictions found for this race.'}</p>
          <Link href="/" className="text-blue-600 hover:underline">
            ← Back to home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-2xl mx-auto">
        <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
          ← Back to home
        </Link>
        
        <h1 className="text-3xl font-bold mb-2 text-black">{race.location}</h1>
        <p className="text-gray-600 mb-6">Round {race.round_number} • Your Predictions</p>

        {prediction.scored && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <p className="text-green-800 font-semibold">
              Points Earned: {prediction.points_earned}
            </p>
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          {/* Objective Predictions */}
          <div>
            <h2 className="text-xl font-semibold mb-3 text-black">Objective Predictions</h2>
            <div className="space-y-2">
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Pole Position:</span>
                <span className="font-semibold text-black">{prediction.pole_driver}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Podium P1:</span>
                <span className="font-semibold text-black">{prediction.podium_p1}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Podium P2:</span>
                <span className="font-semibold text-black">{prediction.podium_p2}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Podium P3:</span>
                <span className="font-semibold text-black">{prediction.podium_p3}</span>
              </div>
              {prediction.chaser_driver && (
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Chaser (Fastest Lap):</span>
                  <span className="font-semibold text-black">{prediction.chaser_driver}</span>
                </div>
              )}
            </div>
          </div>

          {/* Subjective Predictions */}
          <div>
            <h2 className="text-xl font-semibold mb-3 text-black">Subjective Predictions</h2>
            <div className="space-y-2">
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Breakout ({prediction.breakout_type}):</span>
                <span className="font-semibold text-black">{prediction.breakout_name}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Bust ({prediction.bust_type}):</span>
                <span className="font-semibold text-black">{prediction.bust_name}</span>
              </div>
            </div>
          </div>

          {/* Full Send */}
          {prediction.full_send_category && (
            <div>
              <h2 className="text-xl font-semibold mb-3 text-black">Full Send</h2>
              <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                <span className="text-yellow-800 font-semibold">
                  {prediction.full_send_category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </span>
                <span className="text-yellow-600 text-sm ml-2">(Double or nothing!)</span>
              </div>
            </div>
          )}

          {/* Submitted timestamp */}
          <div className="text-sm text-gray-500 pt-4 border-t">
            Submitted: {new Date(prediction.submitted_at).toLocaleString()}
          </div>

          {/* Edit button if predictions not yet closed */}
          {!race.completed && (
            <Link
              href={`/edit/${raceId}`}
              className="block w-full bg-gray-100 text-gray-700 py-3 rounded-lg font-semibold text-center hover:bg-gray-200 transition-colors"
            >
              Edit Predictions
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}

export default function PredictionsPage() {
  return (
    <ProtectedRoute>
      <PredictionsContent />
    </ProtectedRoute>
  );
}
