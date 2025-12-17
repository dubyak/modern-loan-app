'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import BottomNav from '@/components/BottomNav';
import { ArrowLeft, Gift, Star, Trophy } from 'lucide-react';

export default function RewardsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-lg mx-auto px-4 py-4 flex items-center gap-4">
          <Link href="/customer" className="text-tala-500">
            <ArrowLeft size={24} />
          </Link>
          <h1 className="text-xl font-bold text-gray-900">Rewards</h1>
        </div>
      </header>

      <div className="max-w-lg mx-auto px-4 py-6 space-y-6">
        {/* Rewards Balance */}
        <div className="bg-gradient-to-br from-tala-500 to-tala-600 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm text-tala-100 mb-1">Your Points</p>
              <h2 className="text-4xl font-bold">0</h2>
            </div>
            <div className="text-5xl">🎁</div>
          </div>
          <p className="text-sm text-tala-50">
            Earn points by making on-time payments and referring friends!
          </p>
        </div>

        {/* How to Earn Points */}
        <div className="bg-white rounded-2xl p-6">
          <h3 className="font-semibold text-gray-900 mb-4">How to Earn Points</h3>

          <div className="space-y-4">
            <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-xl">
              <div className="bg-green-100 p-2 rounded-full">
                <Star className="text-green-600" size={20} />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900 mb-1">
                  On-time Payments
                </h4>
                <p className="text-sm text-gray-600">
                  Earn 50 points for every on-time loan payment
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-xl">
              <div className="bg-orange-100 p-2 rounded-full">
                <Gift className="text-orange-600" size={20} />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900 mb-1">Refer a Friend</h4>
                <p className="text-sm text-gray-600">
                  Get 100 points when a friend completes their first loan
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-xl">
              <div className="bg-tala-100 p-2 rounded-full">
                <Trophy className="text-tala-600" size={20} />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900 mb-1">
                  Complete Your Profile
                </h4>
                <p className="text-sm text-gray-600">
                  Earn 25 points by completing your business profile
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Available Rewards */}
        <div className="bg-white rounded-2xl p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Available Rewards</h3>

          <div className="text-center py-8">
            <div className="text-4xl mb-2">🎯</div>
            <p className="text-sm text-gray-600">Coming soon!</p>
            <p className="text-xs text-gray-500 mt-2">
              Start earning points now and redeem them when rewards are available
            </p>
          </div>
        </div>

        {/* Share & Earn */}
        <div className="card-highlight">
          <h3 className="font-semibold text-gray-900 mb-2">Share & Earn</h3>
          <p className="text-sm text-gray-600 mb-4">
            Invite your friends to join TALA and earn rewards for every successful
            referral!
          </p>
          <button className="btn btn-primary w-full">Share Your Link</button>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
