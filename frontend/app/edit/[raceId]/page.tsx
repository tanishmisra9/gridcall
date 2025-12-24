'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getUserPrediction, updatePrediction, Prediction, UserPrediction } from '@/lib/api';
import Link from 'next/link';

const DRIVERS = [
  'VER', 'PER', 'HAM', 'RUS', 'LEC', 'SAI', 'NOR', 'PIA',
  'ALO', 'STR', 'OCO', 'GAS', 'TSU', 'RIC', 'ALB', 'SAR',
  'MAG', 'HUL', 'BOT', 'ZHO'
];

const TEAMS = [
  'Red Bull Racing', 'Mercedes', 'Ferrari', 'McLaren',
  'Aston Martin', 'Alpine', 'Williams', 'Kick Sauber',
  'RB', 'Haas F1 Team'
];

export default function EditPredictionPage() {
  const params = useParams();
  const router = useRouter();
  const raceId = parseInt(params.raceId as string);
  const userId = 1; // TODO: Get from auth

  const [existingPrediction, setExistingPrediction] = useState<UserPrediction | null>(null);
  const [prediction, setPrediction] = useState<Partial<Prediction>>({
    race_id: raceId,
    breakout_type: 'driver',
    bust_type: 'driver',
  });
  const [fullSend, setFullSend] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadExistingPrediction();
  }, []);

  const loadExistingPrediction = async () => {
    try {
      const existing = await getUserPrediction(userId, raceId);
      setExistingPrediction(existing);
      
      // Pre-fill the form
      setPrediction({
        race_id: raceId,
        pole_driver: existing.pole_driver,
        podium_p1: existing.podium_p1,
        podium_p2: existing.podium_p2,
        podium_p3: existing.podium_p3,
        chaser_driver: existing.chaser_driver,
        breakout_type: existing.breakout_type,
        breakout_name: existing.breakout_name,
        bust_type: existing.bust_type,
        bust_name: existing.bust_name,
      });
      setFullSend(existing.full_send_category || '');
    } catch (err: any) {
      setError('Failed to load existing predictions');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      if (!prediction.pole_driver || !prediction.podium_p1 || 
          !prediction.podium_p2 || !prediction.podium_p3) {
        throw new Error('Please fill in all objective predictions');
      }

      if (!prediction.breakout_name || !prediction.bust_name) {
        throw new Error('Please fill in breakout and bust predictions');
      }

      const finalPrediction: Prediction = {
        ...prediction as Prediction,
        full_send_category: fullSend || undefined,
      };

      await updatePrediction(existingPrediction!.id, finalPrediction, userId);
      alert('Predictions updated successfully!');
      router.push(`/predictions/${raceId}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to update prediction');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading predictions...</div>
      </div>
    );
  }

  if (!existingPrediction) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-2xl mx-auto">
          <p className="text-gray-600 mb-4">No existing predictions found.</p>
          <Link href="/" className="text-blue-600 hover:underline">← Back to home</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
          ← Back to home
        </Link>
        <h1 className="text-3xl font-bold mb-6 text-black">Edit Your Predictions</h1>

        <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl mx-auto p-6 bg-white rounded-lg shadow">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Objective Predictions */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold text-black">Objective Predictions</h3>
            
            <div>
              <label className="block text-sm font-medium mb-1 text-black">Pole Position</label>
              <select
                className="w-full p-2 border rounded text-black"
                value={prediction.pole_driver || ''}
                onChange={(e) => setPrediction({ ...prediction, pole_driver: e.target.value })}
                required
              >
                <option value="">Select driver</option>
                {DRIVERS.map(driver => (
                  <option key={driver} value={driver}>{driver}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-black">Podium P1</label>
              <select
                className="w-full p-2 border rounded text-black"
                value={prediction.podium_p1 || ''}
                onChange={(e) => setPrediction({ ...prediction, podium_p1: e.target.value })}
                required
              >
                <option value="">Select driver</option>
                {DRIVERS.map(driver => (
                  <option key={driver} value={driver}>{driver}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-black">Podium P2</label>
              <select
                className="w-full p-2 border rounded text-black"
                value={prediction.podium_p2 || ''}
                onChange={(e) => setPrediction({ ...prediction, podium_p2: e.target.value })}
                required
              >
                <option value="">Select driver</option>
                {DRIVERS.map(driver => (
                  <option key={driver} value={driver}>{driver}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-black">Podium P3</label>
              <select
                className="w-full p-2 border rounded text-black"
                value={prediction.podium_p3 || ''}
                onChange={(e) => setPrediction({ ...prediction, podium_p3: e.target.value })}
                required
              >
                <option value="">Select driver</option>
                {DRIVERS.map(driver => (
                  <option key={driver} value={driver}>{driver}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-black">Chaser (Most Positions Gained)</label>
              <select
                className="w-full p-2 border rounded text-black"
                value={prediction.chaser_driver || ''}
                onChange={(e) => setPrediction({ ...prediction, chaser_driver: e.target.value })}
              >
                <option value="">Select driver (optional)</option>
                {DRIVERS.map(driver => (
                  <option key={driver} value={driver}>{driver}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Subjective Predictions */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold text-black">Subjective Predictions</h3>
            
            <div>
              <label className="block text-sm font-medium mb-1 text-black">Breakout</label>
              <div className="flex gap-4 mb-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="breakout_type"
                    value="driver"
                    checked={prediction.breakout_type === 'driver'}
                    onChange={(e) => setPrediction({ ...prediction, breakout_type: 'driver', breakout_name: '' })}
                  />
                  <span className="ml-2 text-black">Driver (1pt)</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="breakout_type"
                    value="team"
                    checked={prediction.breakout_type === 'team'}
                    onChange={(e) => setPrediction({ ...prediction, breakout_type: 'team', breakout_name: '' })}
                  />
                  <span className="ml-2 text-black">Team (2pt)</span>
                </label>
              </div>
              <select
                className="w-full p-2 border rounded text-black"
                value={prediction.breakout_name || ''}
                onChange={(e) => setPrediction({ ...prediction, breakout_name: e.target.value })}
                required
              >
                <option value="">Select {prediction.breakout_type}</option>
                {(prediction.breakout_type === 'driver' ? DRIVERS : TEAMS).map(item => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-black">Bust</label>
              <div className="flex gap-4 mb-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="bust_type"
                    value="driver"
                    checked={prediction.bust_type === 'driver'}
                    onChange={(e) => setPrediction({ ...prediction, bust_type: 'driver', bust_name: '' })}
                  />
                  <span className="ml-2 text-black">Driver (1pt)</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="bust_type"
                    value="team"
                    checked={prediction.bust_type === 'team'}
                    onChange={(e) => setPrediction({ ...prediction, bust_type: 'team', bust_name: '' })}
                  />
                  <span className="ml-2 text-black">Team (2pt)</span>
                </label>
              </div>
              <select
                className="w-full p-2 border rounded text-black"
                value={prediction.bust_name || ''}
                onChange={(e) => setPrediction({ ...prediction, bust_name: e.target.value })}
                required
              >
                <option value="">Select {prediction.bust_type}</option>
                {(prediction.bust_type === 'driver' ? DRIVERS : TEAMS).map(item => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Full Send */}
          <div>
            <label className="block text-sm font-medium mb-1 text-black">Full Send (Optional - Double Points)</label>
            <select
              className="w-full p-2 border rounded text-black"
              value={fullSend}
              onChange={(e) => setFullSend(e.target.value)}
            >
              <option value="">None</option>
              <option value="pole">Pole Position</option>
              <option value="podium">Podium</option>
              <option value="chaser">Chaser</option>
              <option value="breakout">Breakout</option>
              <option value="bust">Bust</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400"
          >
            {submitting ? 'Updating...' : 'Update Predictions'}
          </button>
        </form>
      </div>
    </div>
  );
}