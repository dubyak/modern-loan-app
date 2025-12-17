'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import { loansAPI } from '@/lib/api';
import BottomNav from '@/components/BottomNav';
import { ArrowRight, Clock, CheckCircle } from 'lucide-react';

export default function CustomerDashboard() {
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();

  const [loans, setLoans] = useState<any[]>([]);
  const [activeLoan, setActiveLoan] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    loadLoans();
  }, [isAuthenticated, router]);

  const loadLoans = async () => {
    try {
      const response = await loansAPI.getLoans();
      setLoans(response.data);

      // Find active or approved loan
      const active = response.data.find(
        (loan: any) => loan.status === 'active' || loan.status === 'approved'
      );
      setActiveLoan(active);
    } catch (error) {
      console.error('Error loading loans:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tala-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-lg mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-tala-600">TALA</h1>
          </div>
          <button
            onClick={handleLogout}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            Logout
          </button>
        </div>
      </header>

      <div className="max-w-lg mx-auto px-4 py-6 space-y-6">
        {/* Loan Disbursement Card */}
        {activeLoan && activeLoan.status === 'approved' && !activeLoan.disbursed_at && (
          <div className="card-highlight">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Your money is on the way!</p>
                <h2 className="text-3xl font-bold text-gray-900">
                  ${activeLoan.amount.toLocaleString()}
                </h2>
              </div>
              <div className="text-6xl">🌱</div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Start off strong! Your growth is in your hands. That's why payment matters
              so much here.{' '}
              <span className="text-tala-600 font-medium">Guide with Tala</span>
            </p>
            <button className="btn btn-secondary w-full">
              Make payment
            </button>
          </div>
        )}

        {/* Payment Due Card */}
        {activeLoan && activeLoan.status === 'active' && (
          <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-500 mb-1">Due {activeLoan.due_date ? new Date(activeLoan.due_date).toLocaleDateString('en-US', { day: 'numeric', month: 'short' }) : '1 Feb'}</p>
                <h3 className="text-2xl font-bold text-gray-900">
                  ${activeLoan.total_repayment.toLocaleString()}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="text-orange-500" size={20} />
                <span className="text-sm font-medium text-orange-500">Payment Due</span>
              </div>
            </div>
            <button className="btn btn-secondary w-full">
              Make payment
            </button>
          </div>
        )}

        {/* No Active Loan */}
        {!activeLoan && (
          <div className="card-highlight text-center">
            <div className="text-6xl mb-4">🌱</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Ready to grow your business?
            </h3>
            <p className="text-gray-600 mb-6">
              Chat with Lucy to get started with your loan application
            </p>
            <Link href="/customer/chat" className="btn btn-primary inline-block">
              Start application
            </Link>
          </div>
        )}

        {/* Chat Assistant Card */}
        <div className="bg-tala-500 rounded-2xl p-6 text-white">
          <div className="flex items-start gap-4 mb-4">
            <div className="text-3xl">💬</div>
            <div className="flex-1">
              <h4 className="font-bold text-lg mb-1">Lucy</h4>
              <p className="text-sm text-tala-50">
                Hi! How can I help you today? 💚
              </p>
            </div>
          </div>
          <div className="bg-white/10 rounded-xl p-4 backdrop-blur-sm">
            <p className="text-sm mb-2">
              I can help you answer questions about your loan, and you can tell me anything!
            </p>
          </div>
          <Link href="/customer/chat" className="btn btn-outline mt-4 w-full bg-white text-tala-600 hover:bg-gray-50">
            Chat with Lucy
          </Link>
        </div>

        {/* Add to Payment Streak */}
        <div className="bg-white rounded-2xl p-6 flex items-start gap-4">
          <div className="text-4xl">🌿</div>
          <div className="flex-1">
            <h5 className="font-semibold text-gray-900 mb-1">Add to your payment streak!</h5>
            <p className="text-sm text-gray-600">
              You can always pay your loan before the due date. This can improve your score.
            </p>
          </div>
        </div>

        {/* Grow Your Money */}
        <div className="bg-white rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="text-3xl">🌱</div>
            <div>
              <h5 className="font-semibold text-gray-900">Pump your cash!</h5>
              <p className="text-sm text-gray-600">
                Paying on time helps you grow faster
              </p>
            </div>
          </div>
          <div className="bg-gradient-to-r from-tala-50 to-green-50 rounded-xl p-4">
            <p className="text-sm text-gray-700">
              <span className="font-semibold">Tip:</span> We'll guide you through easy steps to
              make payments on time and save more.
            </p>
          </div>
        </div>

        {/* Loan History */}
        {loans.length > 0 && (
          <div className="bg-white rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold text-gray-900">Your loans</h4>
              <Link href="/customer/wallet" className="text-sm text-tala-500 font-medium">
                See all
              </Link>
            </div>
            <div className="space-y-3">
              {loans.slice(0, 3).map((loan) => (
                <div
                  key={loan.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-xl"
                >
                  <div className="flex items-center gap-3">
                    {loan.status === 'completed' ? (
                      <CheckCircle className="text-green-500" size={20} />
                    ) : (
                      <Clock className="text-orange-500" size={20} />
                    )}
                    <div>
                      <p className="font-medium text-gray-900">
                        ${loan.amount.toLocaleString()}
                      </p>
                      <p className="text-xs text-gray-500 capitalize">{loan.status}</p>
                    </div>
                  </div>
                  <ArrowRight className="text-gray-400" size={16} />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
