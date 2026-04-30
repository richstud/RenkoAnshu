import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from 'react';
import { supabase } from '../services/supabase';
export default function AuthPage() {
    const [mode, setMode] = useState('login');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);
        try {
            if (mode === 'login') {
                const { error } = await supabase.auth.signInWithPassword({ email, password });
                if (error)
                    throw error;
            }
            else if (mode === 'signup') {
                const { error } = await supabase.auth.signUp({ email, password });
                if (error)
                    throw error;
                setMessage({ type: 'success', text: 'Account created! Check your email to confirm.' });
            }
            else if (mode === 'reset') {
                const { error } = await supabase.auth.resetPasswordForEmail(email, {
                    redirectTo: `${window.location.origin}/reset-password`,
                });
                if (error)
                    throw error;
                setMessage({ type: 'success', text: 'Password reset email sent! Check your inbox.' });
            }
        }
        catch (err) {
            setMessage({ type: 'error', text: err.message || 'An error occurred' });
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsx("div", { className: "min-h-screen bg-slate-900 flex items-center justify-center p-4", children: _jsxs("div", { className: "bg-slate-800 rounded-xl shadow-2xl p-8 w-full max-w-md border border-slate-700", children: [_jsxs("div", { className: "text-center mb-8", children: [_jsx("div", { className: "text-4xl mb-3", children: "\uD83D\uDCCA" }), _jsx("h1", { className: "text-2xl font-bold text-white", children: "Renko Gold Bot" }), _jsx("p", { className: "text-slate-400 text-sm mt-1", children: mode === 'login' ? 'Sign in to your account' :
                                mode === 'signup' ? 'Create a new account' :
                                    'Reset your password' })] }), message && (_jsx("div", { className: `mb-4 p-3 rounded-lg text-sm ${message.type === 'success'
                        ? 'bg-green-900/50 border border-green-700 text-green-300'
                        : 'bg-red-900/50 border border-red-700 text-red-300'}`, children: message.text })), _jsxs("form", { onSubmit: handleSubmit, className: "space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-1", children: "Email" }), _jsx("input", { type: "email", value: email, onChange: e => setEmail(e.target.value), required: true, placeholder: "you@example.com", className: "w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" })] }), mode !== 'reset' && (_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-1", children: "Password" }), _jsx("input", { type: "password", value: password, onChange: e => setPassword(e.target.value), required: true, placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022", minLength: 6, className: "w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" })] })), _jsx("button", { type: "submit", disabled: loading, className: "w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-semibold py-2.5 rounded-lg transition-colors", children: loading ? '⏳ Please wait...' :
                                mode === 'login' ? '🔐 Sign In' :
                                    mode === 'signup' ? '✅ Create Account' :
                                        '📧 Send Reset Email' })] }), _jsxs("div", { className: "mt-6 space-y-2 text-center text-sm", children: [mode === 'login' && (_jsxs(_Fragment, { children: [_jsx("button", { onClick: () => { setMode('reset'); setMessage(null); }, className: "text-slate-400 hover:text-blue-400 transition-colors block w-full", children: "Forgot password?" }), _jsxs("button", { onClick: () => { setMode('signup'); setMessage(null); }, className: "text-slate-400 hover:text-white transition-colors", children: ["Don't have an account? ", _jsx("span", { className: "text-blue-400", children: "Sign up" })] })] })), mode === 'signup' && (_jsxs("button", { onClick: () => { setMode('login'); setMessage(null); }, className: "text-slate-400 hover:text-white transition-colors", children: ["Already have an account? ", _jsx("span", { className: "text-blue-400", children: "Sign in" })] })), mode === 'reset' && (_jsx("button", { onClick: () => { setMode('login'); setMessage(null); }, className: "text-slate-400 hover:text-white transition-colors", children: "\u2190 Back to sign in" }))] })] }) }));
}
