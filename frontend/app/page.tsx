'use client';

import { useEffect, useState } from 'react';
import { getUpcomingRaces, getMyPrediction, UpcomingRace } from '@/lib/api';
import Link from 'next/link';

export default function Home() {
  const [races, setRaces] = useState<UpcomingRace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [hasPredictions, setHasPredictions] = useState<{ [key: number]: boolean }>({});
  
  const userId = 1; // TODO: Get from auth

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
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading races...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-5xl font-bold mb-2 text-black">Gridcall</h1>
        <p className="text-2xl text-gray-600 mb-8">&quot;Prove you know the grid.&quot;</p>

        <h2 className="text-3xl font-semibold mb-6 text-black">Upcoming Races</h2>

        {races.length === 0 ? (
          <div className="bg-white rounded-lg p-8 text-center shadow">
            <p className="text-gray-600">No upcoming races at the moment.</p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {races.map((race) => (
              <div
                key={race.id}
                className="bg-white rounded-lg shadow-md p-6 border-2 border-gray-200 hover:border-blue-500 transition"
              >
                <h3 className="text-2xl font-bold mb-3 text-black">{race.location}</h3>
                <div className="space-y-2 text-gray-700 mb-4">
                  <p>
                    <span className="font-medium">Round:</span> {race.round_number}
                  </p>
                  <p>
                    <span className="font-medium">Race Date:</span>{' '}
                    {new Date(race.race_date).toLocaleDateString()}
                  </p>
                  <p>
                    <span className="font-medium">Predictions close in:</span>{' '}
                    {race.time_until_close}
                  </p>
                </div>

                <div className="mt-4 space-y-2">
                  {race.can_predict ? (
                    <>
                      {hasPredictions[race.id] ? (
                        <>
                          <Link
                            href={`/edit/${race.id}`}
                            className="block w-full text-center bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
                          >
                            Edit Predictions
                          </Link>
                          <Link
                            href={`/predictions/${race.id}`}
                            className="block w-full text-center bg-gray-200 text-gray-700 py-2 rounded-lg text-sm hover:bg-gray-300 transition"
                          >
                            View My Predictions
                          </Link>
                        </>
                      ) : (
                        <Link
                          href={`/predict/${race.id}`}
                          className="block w-full text-center bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
                        >
                          Make Predictions
                        </Link>
                      )}
                    </>
                  ) : (
                    <div className="text-center text-gray-500 py-3">
                      Predictions Closed
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-12 bg-blue-50 rounded-lg p-8">
          <h3 className="text-2xl font-semibold mb-4">How to Play</h3>
          <ol className="list-decimal list-inside space-y-3 text-gray-700">
            <li>Submit predictions before each race weekend</li>
            <li>Predict pole position, podium finishers, and more</li>
            <li>Choose one prediction to &quot;Full Send&quot; for double points</li>
            <li>Compete with friends in your Grid to score the most points</li>
          </ol>
        </div>
      </div>
    </main>
  );
}