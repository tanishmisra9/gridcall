'use client';

import { useState } from 'react';
import { submitPrediction, Prediction } from '@/lib/api';

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

interface PredictionFormProps {
  raceId: number;
  userId: number;
  onSuccess?: () => void;
}

export default function PredictionForm({ raceId, userId, onSuccess }: PredictionFormProps) {
  const [prediction, setPrediction] = useState<Partial<Prediction>>({
    race_id: raceId,
    breakout_type: 'driver',
    bust_type: 'driver',
  });
  
  const [fullSend, setFullSend] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validate prediction
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

      await submitPrediction(finalPrediction, userId);
      
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to submit prediction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl mx-auto p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4 text-black">Submit Your Predictions</h2>
      
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
            <option value="">Select driver (optional, editable until race start)</option>
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
        disabled={loading}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400"
      >
        {loading ? 'Submitting...' : 'Submit Predictions'}
      </button>
    </form>
  );
}