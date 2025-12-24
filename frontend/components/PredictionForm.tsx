'use client';

import { useState } from 'react';
import { submitPrediction, Prediction } from '@/lib/api';

// F1 2025 drivers list
const DRIVERS = [
  'VER', 'PER', 'HAM', 'RUS', 'LEC', 'SAI', 'NOR', 'PIA',
  'ALO', 'STR', 'OCO', 'GAS', 'TSU', 'LAW', 'ALB', 'SAR',
  'BOT', 'ZHO', 'MAG', 'HUL', 'BEA', 'HAD', 'ANT', 'DOO'
];

// F1 2025 teams list
const TEAMS = [
  'Red Bull', 'Mercedes', 'Ferrari', 'McLaren', 'Aston Martin',
  'Alpine', 'RB', 'Williams', 'Sauber', 'Haas'
];

const FULL_SEND_CATEGORIES = [
  'pole_driver',
  'podium_p1',
  'podium_p2',
  'podium_p3',
  'breakout',
  'bust'
];

interface PredictionFormProps {
  raceId: number;
  userId: number;
  onSuccess?: () => void;
  initialData?: Partial<Prediction>;
}

export default function PredictionForm({ 
  raceId, 
  userId, 
  onSuccess,
  initialData 
}: PredictionFormProps) {
  const [formData, setFormData] = useState<Prediction>({
    race_id: raceId,
    pole_driver: initialData?.pole_driver || '',
    podium_p1: initialData?.podium_p1 || '',
    podium_p2: initialData?.podium_p2 || '',
    podium_p3: initialData?.podium_p3 || '',
    chaser_driver: initialData?.chaser_driver || '',
    breakout_type: initialData?.breakout_type || 'driver',
    breakout_name: initialData?.breakout_name || '',
    bust_type: initialData?.bust_type || 'driver',
    bust_name: initialData?.bust_name || '',
    full_send_category: initialData?.full_send_category || '',
  });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      await submitPrediction(formData);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit prediction');
    } finally {
      setSubmitting(false);
    }
  };

  const updateField = (field: keyof Prediction, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
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
            value={formData.pole_driver}
            onChange={(e) => updateField('pole_driver', e.target.value)}
            className="w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Select driver</option>
            {DRIVERS.map(d => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1 text-black">Podium P1</label>
            <select
              value={formData.podium_p1}
              onChange={(e) => updateField('podium_p1', e.target.value)}
              className="w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select</option>
              {DRIVERS.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-black">Podium P2</label>
            <select
              value={formData.podium_p2}
              onChange={(e) => updateField('podium_p2', e.target.value)}
              className="w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select</option>
              {DRIVERS.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-black">Podium P3</label>
            <select
              value={formData.podium_p3}
              onChange={(e) => updateField('podium_p3', e.target.value)}
              className="w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select</option>
              {DRIVERS.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1 text-black">Chaser (Fastest Lap)</label>
          <select
            value={formData.chaser_driver}
            onChange={(e) => updateField('chaser_driver', e.target.value)}
            className="w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select driver (optional)</option>
            {DRIVERS.map(d => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
          <p className="text-xs text-gray-500 mt-1">Can be edited until race start</p>
        </div>
      </div>

      {/* Subjective Predictions */}
      <div className="space-y-4 pt-4 border-t">
        <h3 className="text-xl font-semibold text-black">Subjective Predictions</h3>

        <div>
          <label className="block text-sm font-medium mb-1 text-black">Breakout Pick</label>
          <div className="flex gap-2 mb-2">
            <button
              type="button"
              onClick={() => {
                updateField('breakout_type', 'driver');
                updateField('breakout_name', '');
              }}
              className={`px-4 py-2 rounded ${
                formData.breakout_type === 'driver' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-black'
              }`}
            >
              Driver
            </button>
            <button
              type="button"
              onClick={() => {
                updateField('breakout_type', 'team');
                updateField('breakout_name', '');
              }}
              className={`px-4 py-2 rounded ${
                formData.breakout_type === 'team' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-black'
              }`}
            >
              Team
            </button>
          </div>
          <select
            value={formData.breakout_name}
            onChange={(e) => updateField('breakout_name', e.target.value)}
            className="w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Select {formData.breakout_type}</option>
            {(formData.breakout_type === 'driver' ? DRIVERS : TEAMS).map(item => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1 text-black">Bust Pick</label>
          <div className="flex gap-2 mb-2">
            <button
              type="button"
              onClick={() => {
                updateField('bust_type', 'driver');
                updateField('bust_name', '');
              }}
              className={`px-4 py-2 rounded ${
                formData.bust_type === 'driver' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-black'
              }`}
            >
              Driver
            </button>
            <button
              type="button"
              onClick={() => {
                updateField('bust_type', 'team');
                updateField('bust_name', '');
              }}
              className={`px-4 py-2 rounded ${
                formData.bust_type === 'team' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-black'
              }`}
            >
              Team
            </button>
          </div>
          <select
            value={formData.bust_name}
            onChange={(e) => updateField('bust_name', e.target.value)}
            className="w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Select {formData.bust_type}</option>
            {(formData.bust_type === 'driver' ? DRIVERS : TEAMS).map(item => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Full Send */}
      <div className="space-y-4 pt-4 border-t">
        <h3 className="text-xl font-semibold text-black">Full Send (Double Points)</h3>
        <p className="text-sm text-gray-600">Pick one category to double your points (or lose them all!)</p>
        <select
          value={formData.full_send_category}
          onChange={(e) => updateField('full_send_category', e.target.value)}
          className="w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">None (optional)</option>
          {FULL_SEND_CATEGORIES.map(cat => (
            <option key={cat} value={cat}>
              {cat.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </option>
          ))}
        </select>
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
      >
        {submitting ? 'Submitting...' : 'Submit Predictions'}
      </button>
    </form>
  );
}
