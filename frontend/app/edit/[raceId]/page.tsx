'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getMyPrediction, updatePrediction, UserPrediction, Prediction } from '@/lib/api';
import Link from 'next/link';
import ProtectedRoute from '@/components/ProtectedRoute';

// F1 2025 drivers list
const DRIVERS = [
  'VER', 'PER', 'HAM', 'RUS', 'LEC', 'SAI', 'NOR', 'PIA',
  'ALO', 'STR', 'OCO', 'GAS', 'TSU', 'LAW', 'ALB', 'SAR',
  'BOT', 'ZHO', 'MAG', 'HUL', 'BEA', 'HAD', 'ANT', 'DOO'
];

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

function EditContent() {
  const params = useParams();
  const router = useRouter();
  const raceId = parseInt(params.raceId as string);
  
  const [existingPrediction, setExistingPrediction] = useState<UserPrediction | null>(null);
  const [formData, setFormData] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPrediction();
  }, [raceId]);

  const loadPrediction = async () => {
    try {
      const prediction = await getMyPrediction(raceId);
      setExistingPrediction(prediction);
      setFormData({
        race_id: raceId,
        pole_driver: prediction.pole_driver,
        podium_p1: prediction.podium_p1,
        podium_p2: prediction.podium_p2,
        podium_p3: prediction.podium_p3,
        chaser_driver: prediction.chaser_driver || '',
        breakout_type: prediction.breakout_type,
        breakout_name: prediction.breakout_name,
        bust_type: prediction.bust_type,
        bust_name: prediction.bust_name,
        full_send_category: prediction.full_send_category || '',
      });
    } catch (err: any) {
      setError('No existing predictions found');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!existingPrediction || !formData) return;

    setSubmitting(true);
    setError('');

    try {
      await updatePrediction(existingPrediction.id, formData);
      router.push(`/predictions/${raceId}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to update prediction');
    } finally {
      setSubmitting(false);
    }
  };

  const updateField = (field: keyof Prediction, value: string) => {
    if (!formData) return;
    setFormData(prev => prev ? { ...prev, [field]: value } : null);
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

  if (!existingPrediction || !formData) {
    return (
      <div className="min-h-screen p-8 bg-gray-50">
        <div className="max-w-2xl mx-auto">
          <p className="text-gray-600 mb-4">{error || 'No existing predictions found.'}</p>
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
                <label className="block text-sm font-medium mb-1 text-black">P1</label>
                <select
                  value={formData.podium_p1}
                  onChange={(e) => updateField('podium_p1', e.target.value)}
                  className="w-full p-3 border rounded text-black"
                  required
                >
                  <option value="">Select</option>
                  {DRIVERS.map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-black">P2</label>
                <select
                  value={formData.podium_p2}
                  onChange={(e) => updateField('podium_p2', e.target.value)}
                  className="w-full p-3 border rounded text-black"
                  required
                >
                  <option value="">Select</option>
                  {DRIVERS.map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-black">P3</label>
                <select
                  value={formData.podium_p3}
                  onChange={(e) => updateField('podium_p3', e.target.value)}
                  className="w-full p-3 border rounded text-black"
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
                className="w-full p-3 border rounded text-black"
              >
                <option value="">Select driver (optional)</option>
                {DRIVERS.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
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
                className="w-full p-3 border rounded text-black"
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
                className="w-full p-3 border rounded text-black"
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
            <select
              value={formData.full_send_category}
              onChange={(e) => updateField('full_send_category', e.target.value)}
              className="w-full p-3 border rounded text-black"
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
            {submitting ? 'Updating...' : 'Update Predictions'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function EditPage() {
  return (
    <ProtectedRoute>
      <EditContent />
    </ProtectedRoute>
  );
}
