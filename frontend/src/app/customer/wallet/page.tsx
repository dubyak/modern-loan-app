'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import { loansAPI, transactionsAPI } from '@/lib/api';
import BottomNav from '@/components/BottomNav';
import { ArrowLeft, ArrowDown, ArrowUp, Clock } from 'lucide-react';

export default function WalletPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  const [loans, setLoans] = useState<any[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [totalBorrowed, setTotalBorrowed] = useState(0);
  const [totalRepaid, setTotalRepaid] = useState(0);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    loadData();
  }, [isAuthenticated, router]);

  const loadData = async () => {
    try {
      const [loansRes, transactionsRes] = await Promise.all([
        loansAPI.getLoans(),
        transactionsAPI.getTransactions(),
      ]);

      setLoans(loansRes.data);
      setTransactions(transactionsRes.data);

      // Calculate totals
      const borrowed = loansRes.data.reduce(
        (sum: number, loan: any) => sum + (loan.amount || 0),
        0
      );
      const repaid = transactionsRes.data
        .filter((t: any) => t.type === 'repayment')
        .reduce((sum: number, t: any) => sum + (t.amount || 0), 0);

      setTotalBorrowed(borrowed);
      setTotalRepaid(repaid);
    } catch (error) {
      console.error('Error loading wallet data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'disbursement':
        return <ArrowDown className="text-green-500" size={20} />;
      case 'repayment':
        return <ArrowUp className="text-orange-500" size={20} />;
      default:
        return <Clock className="text-gray-400" size={20} />;
    }
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
        <div className="max-w-lg mx-auto px-4 py-4 flex items-center gap-4">
          <Link href="/customer" className="text-tala-500">
            <ArrowLeft size={24} />
          </Link>
          <h1 className="text-xl font-bold text-gray-900">Wallet</h1>
        </div>
      </header>

      <div className="max-w-lg mx-auto px-4 py-6 space-y-6">
        {/* Balance Cards */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gradient-to-br from-tala-500 to-tala-600 rounded-2xl p-4 text-white">
            <p className="text-sm text-tala-100 mb-1">Total Borrowed</p>
            <h3 className="text-2xl font-bold">${totalBorrowed.toLocaleString()}</h3>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-4 text-white">
            <p className="text-sm text-orange-100 mb-1">Total Repaid</p>
            <h3 className="text-2xl font-bold">${totalRepaid.toLocaleString()}</h3>
          </div>
        </div>

        {/* Outstanding Balance */}
        {totalBorrowed > totalRepaid && (
          <div className="card-highlight">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Outstanding Balance</p>
                <h3 className="text-2xl font-bold text-gray-900">
                  ${(totalBorrowed - totalRepaid).toLocaleString()}
                </h3>
              </div>
              <div className="text-4xl">💰</div>
            </div>
          </div>
        )}

        {/* Loans List */}
        <div className="bg-white rounded-2xl p-6">
          <h4 className="font-semibold text-gray-900 mb-4">Your Loans</h4>

          {loans.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-4xl mb-2">🌱</div>
              <p className="text-sm text-gray-600">No loans yet</p>
              <Link
                href="/customer/chat"
                className="btn btn-primary inline-block mt-4"
              >
                Apply for a loan
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {loans.map((loan) => (
                <div
                  key={loan.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-xl"
                >
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-semibold text-gray-900">
                        ${loan.amount.toLocaleString()}
                      </p>
                      <span
                        className={`text-xs px-2 py-1 rounded-full font-medium ${
                          loan.status === 'completed'
                            ? 'bg-green-100 text-green-700'
                            : loan.status === 'active'
                            ? 'bg-orange-100 text-orange-700'
                            : loan.status === 'approved'
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {loan.status}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">
                      {new Date(loan.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })}
                    </p>
                    {loan.due_date && (
                      <p className="text-xs text-gray-500">
                        Due:{' '}
                        {new Date(loan.due_date).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                        })}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Transactions */}
        <div className="bg-white rounded-2xl p-6">
          <h4 className="font-semibold text-gray-900 mb-4">Transaction History</h4>

          {transactions.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-4xl mb-2">📋</div>
              <p className="text-sm text-gray-600">No transactions yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {transactions.map((transaction) => (
                <div
                  key={transaction.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-xl"
                >
                  <div className="flex items-center gap-3 flex-1">
                    {getTransactionIcon(transaction.type)}
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 capitalize">
                        {transaction.type.replace('_', ' ')}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(transaction.created_at).toLocaleDateString(
                          'en-US',
                          {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          }
                        )}
                      </p>
                    </div>
                    <p
                      className={`font-semibold ${
                        transaction.type === 'disbursement'
                          ? 'text-green-600'
                          : 'text-orange-600'
                      }`}
                    >
                      {transaction.type === 'disbursement' ? '+' : '-'}$
                      {transaction.amount.toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
