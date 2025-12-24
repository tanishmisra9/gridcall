'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getMyPrediction, UserPrediction, getRace, Race } from '@/lib/api';
import Link from 'next/link';

export default function ViewPredictionsPage() {
  const params = useParams();
  const raceId = parseInt(params.raceId as string);
  const userId = 1; // TODO: Get from auth
  
  const [prediction, setPrediction] = useState<UserPrediction | null>(null);
  const [race, setRace] = useState<Race | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [predData, raceData] = await Promise.all([
        getMyPrediction(raceId),
        getRace(raceId)
      ]);
      setPrediction(predData);
      setRace(raceData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load predictions');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading predictions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
          <Link href="/" className="text-blue-600 hover:underline">
            ← Back to home
          </Link>
        </div>
      </div>
    );
  }

  if (!prediction || !race) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-2xl mx-auto text-center">
          <p className="text-gray-600 mb-4">No predictions found for this race.</p>
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

        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          {/* Objective Predictions */}
          <div>
            <h2 className="text-xl font-semibold mb-3 text-black">Objective Predictions</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Pole Position:</span>
                <span className="font-semibold text-black">{prediction.pole_driver}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Podium P1:</span>
                <span className="font-semibold text-black">{prediction.podium_p1}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Podium P2:</span>
                <span className="font-semibold text-black">{prediction.podium_p2}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Podium P3:</span>
                <span className="font-semibold text-black">{prediction.podium_p3}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Chaser:</span>
                <span className="font-semibold text-black">
                  {prediction.chaser_driver || 'Not selected'}
                </span>
              </div>
            </div>
          </div>

          {/* Subjective Predictions */}
          <div>
            <h2 className="text-xl font-semibold mb-3 text-black">Subjective Predictions</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Breakout:</span>
                <span className="font-semibold text-black">
                  {prediction.breakout_name} ({prediction.breakout_type})
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Bust:</span>
                <span className="font-semibold text-black">
                  {prediction.bust_name} ({prediction.bust_type})
                </span>
              </div>
            </div>
          </div>

          {/* Full Send */}
          {prediction.full_send_category && (
            <div className="bg-blue-50 p-4 rounded">
              <h2 className="text-xl font-semibold mb-2 text-black">Full Send!</h2>
              <p className="text-gray-700">
                Double points on: <span className="font-semibold text-black">{prediction.full_send_category}</span>
              </p>
            </div>
          )}

          {/* Scoring Status */}
          <div className="border-t pt-4">
            {prediction.scored ? (
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600 mb-1">
                  {prediction.points_earned} points
                </p>
                <p className="text-gray-600">Race scored!</p>
              </div>
            ) : (
              <div className="text-center text-gray-500">
                <p>Race not yet completed</p>
                <p className="text-sm">Points will be calculated after the race</p>
              </div>
            )}
          </div>

          {/* Submission Info */}
          <div className="text-sm text-gray-500 text-center border-t pt-4">
            Submitted: {new Date(prediction.submitted_at).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
}