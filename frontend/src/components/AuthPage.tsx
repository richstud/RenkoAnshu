import { useState } from 'react';
import { supabase } from '../services/supabase';

type Mode = 'login' | 'signup' | 'reset';

export default function AuthPage() {
  const [mode, setMode] = useState<Mode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      if (mode === 'login') {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      } else if (mode === 'signup') {
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        setMessage({ type: 'success', text: 'Account created! Check your email to confirm.' });
      } else if (mode === 'reset') {
        const { error } = await supabase.auth.resetPasswordForEmail(email, {
          redirectTo: `${window.location.origin}/reset-password`,
        });
        if (error) throw error;
        setMessage({ type: 'success', text: 'Password reset email sent! Check your inbox.' });
      }
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'An error occurred' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-xl shadow-2xl p-8 w-full max-w-md border border-slate-700">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-4xl mb-3">📊</div>
          <h1 className="text-2xl font-bold text-white">Renko Gold Bot</h1>
          <p className="text-slate-400 text-sm mt-1">
            {mode === 'login' ? 'Sign in to your account' :
             mode === 'signup' ? 'Create a new account' :
             'Reset your password'}
          </p>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-4 p-3 rounded-lg text-sm ${
            message.type === 'success'
              ? 'bg-green-900/50 border border-green-700 text-green-300'
              : 'bg-red-900/50 border border-red-700 text-red-300'
          }`}>
            {message.text}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {mode !== 'reset' && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                minLength={6}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-semibold py-2.5 rounded-lg transition-colors"
          >
            {loading ? '⏳ Please wait...' :
             mode === 'login' ? '🔐 Sign In' :
             mode === 'signup' ? '✅ Create Account' :
             '📧 Send Reset Email'}
          </button>
        </form>

        {/* Footer links */}
        <div className="mt-6 space-y-2 text-center text-sm">
          {mode === 'login' && (
            <>
              <button
                onClick={() => { setMode('reset'); setMessage(null); }}
                className="text-slate-400 hover:text-blue-400 transition-colors block w-full"
              >
                Forgot password?
              </button>
              <button
                onClick={() => { setMode('signup'); setMessage(null); }}
                className="text-slate-400 hover:text-white transition-colors"
              >
                Don't have an account? <span className="text-blue-400">Sign up</span>
              </button>
            </>
          )}
          {mode === 'signup' && (
            <button
              onClick={() => { setMode('login'); setMessage(null); }}
              className="text-slate-400 hover:text-white transition-colors"
            >
              Already have an account? <span className="text-blue-400">Sign in</span>
            </button>
          )}
          {mode === 'reset' && (
            <button
              onClick={() => { setMode('login'); setMessage(null); }}
              className="text-slate-400 hover:text-white transition-colors"
            >
              ← Back to sign in
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
