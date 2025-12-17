'use client';

import Link from 'next/link';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    // Redirect authenticated users to their dashboard
    if (isAuthenticated && user) {
      if (user.role === 'admin') {
        router.push('/admin');
      } else if (user.role === 'agent') {
        router.push('/agent');
      } else {
        router.push('/customer');
      }
    }
  }, [isAuthenticated, user, router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      <div className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Modern Loan App
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-2xl mx-auto">
            AI-powered microfinance platform helping entrepreneurs access loans quickly and easily
          </p>

          <div className="flex gap-4 justify-center">
            <Link
              href="/login"
              className="btn btn-primary text-lg px-8 py-3"
            >
              Login
            </Link>
            <Link
              href="/register"
              className="btn btn-secondary text-lg px-8 py-3"
            >
              Get Started
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <div className="card">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-bold mb-2">AI Loan Officer</h3>
            <p className="text-gray-600">
              Chat with Lucy, our AI loan officer, who will assess your business and help you get a loan
            </p>
          </div>

          <div className="card">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-bold mb-2">Fast Approval</h3>
            <p className="text-gray-600">
              Get loan decisions in minutes, not days. Our AI evaluates your business instantly
            </p>
          </div>

          <div className="card">
            <div className="text-4xl mb-4">💰</div>
            <h3 className="text-xl font-bold mb-2">Fair Terms</h3>
            <p className="text-gray-600">
              Transparent pricing with no hidden fees. Know exactly what you'll pay
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="mt-16 max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-8">How It Works</h2>

          <div className="space-y-6">
            <div className="flex gap-4 items-start">
              <div className="bg-primary-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                1
              </div>
              <div>
                <h4 className="font-bold mb-1">Register & Verify</h4>
                <p className="text-gray-600">
                  Create your account with your phone number and verify with OTP
                </p>
              </div>
            </div>

            <div className="flex gap-4 items-start">
              <div className="bg-primary-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                2
              </div>
              <div>
                <h4 className="font-bold mb-1">Chat with Lucy</h4>
                <p className="text-gray-600">
                  Our AI loan officer will ask about your business and assess eligibility
                </p>
              </div>
            </div>

            <div className="flex gap-4 items-start">
              <div className="bg-primary-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                3
              </div>
              <div>
                <h4 className="font-bold mb-1">Get Your Offer</h4>
                <p className="text-gray-600">
                  Receive a personalized loan offer based on your business information
                </p>
              </div>
            </div>

            <div className="flex gap-4 items-start">
              <div className="bg-primary-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                4
              </div>
              <div>
                <h4 className="font-bold mb-1">Accept & Receive Funds</h4>
                <p className="text-gray-600">
                  Accept the loan terms and receive funds directly
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
