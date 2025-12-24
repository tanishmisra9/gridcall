'use client';

import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import PredictionForm from '@/components/PredictionForm';

function PredictContent() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const raceId = parseInt(params.raceId as string);

  const handleSuccess = () => {
    router.push(`/predictions/${raceId}`);
  };

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
          ← Back to home
        </Link>
        <h1 className="text-3xl font-bold mb-6 text-black">Make Your Predictions</h1>
        <PredictionForm 
          raceId={raceId} 
          userId={user?.id || 0}
          onSuccess={handleSuccess}
        />
      </div>
    </div>
  );
}

export default function PredictPage() {
  return (
    <ProtectedRoute>
      <PredictContent />
    </ProtectedRoute>
  );
}
