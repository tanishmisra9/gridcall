'use client';

import { useParams, useRouter } from 'next/navigation';
import PredictionForm from '@/components/PredictionForm';
import Link from 'next/link';

export default function PredictPage() {
  const params = useParams();
  const router = useRouter();
  const raceId = parseInt(params.raceId as string);
  
  // TODO: Get from auth - for now use test user ID
  const userId = 1;

  const handleSuccess = () => {
    alert('Predictions submitted successfully!');
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
          userId={userId}
          onSuccess={handleSuccess}
        />
      </div>
    </div>
  );
}