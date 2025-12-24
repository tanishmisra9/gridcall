'use client';

import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

// Validation check component - just colored text, no symbols
function ValidationCheck({ passed, label }: { passed: boolean; label: string }) {
  return (
    <div className={`text-sm ${passed ? 'text-green-600' : 'text-red-500'}`}>
      {label}
    </div>
  );
}

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [touched, setTouched] = useState({
    username: false,
    email: false,
    password: false,
    confirmPassword: false,
  });
  const { register, user, loading: authLoading } = useAuth();
  const router = useRouter();

  // Username validation
  const usernameValidation = useMemo(() => ({
    minLength: username.length >= 8,
  }), [username]);

  const isUsernameValid = usernameValidation.minLength;

  // Email validation
  const emailValidation = useMemo(() => ({
    isValid: /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
  }), [email]);

  const isEmailValid = emailValidation.isValid;

  // Password validation
  const passwordValidation = useMemo(() => ({
    minLength: password.length >= 8,
    hasNumber: /\d/.test(password),
    hasSpecial: /[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/`~;']/.test(password),
  }), [password]);

  const isPasswordValid = passwordValidation.minLength && 
                          passwordValidation.hasNumber && 
                          passwordValidation.hasSpecial;

  const passwordsMatch = password === confirmPassword && confirmPassword.length > 0;

  // Redirect to home if already logged in
  useEffect(() => {
    if (!authLoading && user) {
      router.push('/');
    }
  }, [user, authLoading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Mark all fields as touched to show validation
    setTouched({ username: true, email: true, password: true, confirmPassword: true });

    // Validate before submitting
    if (!isUsernameValid) {
      setError('Username must be at least 8 characters');
      return;
    }

    if (!isEmailValid) {
      setError('Please enter a valid email address');
      return;
    }

    if (!isPasswordValid) {
      setError('Password does not meet requirements');
      return;
    }

    if (!passwordsMatch) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await register(username, email, password);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to register');
    } finally {
      setLoading(false);
    }
  };

  // Show loading while checking auth status
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Don't show register form if already authenticated
  if (user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-600">Redirecting...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        {/* Back button */}
        <button
          onClick={() => router.back()}
          className="text-blue-600 hover:underline mb-4 inline-flex items-center"
        >
          ← Back
        </button>

        <h1 className="text-3xl font-bold mb-2 text-black text-center">Gridcall</h1>
        <p className="text-gray-600 text-center mb-8">&quot;Prove you know the grid.&quot;</p>
        
        <h2 className="text-2xl font-semibold mb-6 text-black">Create Account</h2>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Username field */}
          <div>
            <label className="block text-sm font-medium mb-1 text-black">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onFocus={() => setTouched(prev => ({ ...prev, username: true }))}
              className={`w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                touched.username 
                  ? isUsernameValid 
                    ? 'border-green-500' 
                    : 'border-red-500'
                  : ''
              }`}
              required
              autoComplete="username"
            />
            {touched.username && (
              <div className="mt-2 space-y-1">
                <ValidationCheck passed={usernameValidation.minLength} label="At least 8 characters" />
              </div>
            )}
          </div>

          {/* Email field */}
          <div>
            <label className="block text-sm font-medium mb-1 text-black">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onFocus={() => setTouched(prev => ({ ...prev, email: true }))}
              className={`w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                touched.email && email.length > 0
                  ? isEmailValid 
                    ? 'border-green-500' 
                    : 'border-red-500'
                  : ''
              }`}
              required
              autoComplete="email"
            />
            {touched.email && email.length > 0 && (
              <div className="mt-2">
                <ValidationCheck passed={isEmailValid} label={isEmailValid ? "Valid email" : "Enter a valid email address"} />
              </div>
            )}
          </div>

          {/* Password field */}
          <div>
            <label className="block text-sm font-medium mb-1 text-black">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onFocus={() => setTouched(prev => ({ ...prev, password: true }))}
                className={`w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500 pr-12 ${
                  touched.password 
                    ? isPasswordValid 
                      ? 'border-green-500' 
                      : 'border-red-500'
                    : ''
                }`}
                required
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
            {touched.password && (
              <div className="mt-2 space-y-1">
                <ValidationCheck passed={passwordValidation.minLength} label="At least 8 characters" />
                <ValidationCheck passed={passwordValidation.hasNumber} label="Contains a number" />
                <ValidationCheck passed={passwordValidation.hasSpecial} label="Contains a special character" />
              </div>
            )}
          </div>

          {/* Confirm Password field */}
          <div>
            <label className="block text-sm font-medium mb-1 text-black">Confirm Password</label>
            <div className="relative">
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                onFocus={() => setTouched(prev => ({ ...prev, confirmPassword: true }))}
                className={`w-full p-3 border rounded text-black focus:outline-none focus:ring-2 focus:ring-blue-500 pr-12 ${
                  touched.confirmPassword && confirmPassword.length > 0
                    ? passwordsMatch 
                      ? 'border-green-500' 
                      : 'border-red-500'
                    : ''
                }`}
                required
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
              >
                {showConfirmPassword ? 'Hide' : 'Show'}
              </button>
            </div>
            {touched.confirmPassword && confirmPassword.length > 0 && (
              <div className="mt-2">
                <ValidationCheck passed={passwordsMatch} label={passwordsMatch ? "Passwords match" : "Passwords do not match"} />
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            {loading ? 'Creating account...' : 'Register'}
          </button>
        </form>

        <p className="mt-6 text-center text-gray-600">
          Already have an account?{' '}
          <Link href="/login" className="text-blue-600 hover:underline">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}