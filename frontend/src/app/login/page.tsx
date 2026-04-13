"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Zap, Eye, EyeOff, ArrowRight, Shield, BarChart3, Users } from "lucide-react";
import { motion } from "framer-motion";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("support@creative.co.ke");
  const [password, setPassword] = useState("1234");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Redirect if already authenticated
  if (isAuthenticated) {
    router.replace("/");
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    // Simulate brief loading
    await new Promise((r) => setTimeout(r, 600));

    const success = login(email, password);
    if (success) {
      router.push("/");
    } else {
      setError("Invalid email or password");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left panel — branding & features */}
      <div className="hidden lg:flex lg:w-[480px] xl:w-[540px] flex-col justify-between p-12 relative overflow-hidden border-r border-white/[0.04]">
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-accent-lime/10 via-transparent to-accent-purple/10" />

        <div className="relative z-10">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-16">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-accent-lime to-accent-lime/60 flex items-center justify-center shadow-[0_0_24px_rgba(204,243,129,0.3)]">
              <Zap className="w-5 h-5 text-[#050505]" strokeWidth={2.5} />
            </div>
            <span className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold tracking-tight">
              <span className="text-accent-lime">Craig</span> AI
            </span>
          </div>

          {/* Headline */}
          <h1 className="font-[family-name:var(--font-space-grotesk)] text-5xl font-bold leading-[1.1] tracking-tight mb-4">
            Social Media
            <br />
            <span className="text-accent-lime">Compliance</span>
            <br />
            Intelligence
          </h1>
          <p className="text-text-secondary text-lg leading-relaxed max-w-sm">
            AI-powered contract compliance tracking across Facebook, Instagram &amp; TikTok.
          </p>
        </div>

        {/* Feature cards */}
        <div className="relative z-10 space-y-3">
          {[
            { icon: Shield, label: "AI Compliance Scoring", desc: "Automated analysis of every post" },
            { icon: BarChart3, label: "Real-time Analytics", desc: "Track deliverables across platforms" },
            { icon: Users, label: "Multi-client Dashboard", desc: "Manage all accounts in one place" },
          ].map((f, i) => (
            <motion.div
              key={f.label}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + i * 0.1 }}
              className="flex items-center gap-4 bg-white/[0.04] border border-white/[0.06] rounded-2xl p-4"
            >
              <div className="w-10 h-10 rounded-xl bg-accent-lime/10 flex items-center justify-center flex-shrink-0">
                <f.icon className="w-5 h-5 text-accent-lime" />
              </div>
              <div>
                <div className="text-sm font-bold text-text-primary">{f.label}</div>
                <div className="text-xs text-text-tertiary">{f.desc}</div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom text */}
        <div className="relative z-10 pt-8">
          <p className="text-xs text-text-tertiary">
            &copy; 2026 Craig AI &bull; A Creativedge tool
          </p>
        </div>
      </div>

      {/* Right panel — login form, perfectly centered */}
      <div className="flex-1 flex items-center justify-center min-h-screen p-6 sm:p-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-[400px]"
        >
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center justify-center gap-3 mb-10">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-accent-lime to-accent-lime/60 flex items-center justify-center">
              <Zap className="w-5 h-5 text-[#050505]" strokeWidth={2.5} />
            </div>
            <span className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
              <span className="text-accent-lime">Craig</span> AI
            </span>
          </div>

          <h2 className="font-[family-name:var(--font-space-grotesk)] text-3xl font-bold tracking-tight mb-2">
            Welcome back
          </h2>
          <p className="text-text-secondary mb-8">
            Sign in to your compliance dashboard
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-text-tertiary mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-white/[0.04] border border-white/[0.06] text-text-primary rounded-2xl px-4 py-3.5 text-sm font-medium outline-none focus:border-accent-lime/40 focus:bg-white/[0.06] transition-all placeholder:text-text-tertiary"
                placeholder="you@company.com"
                required
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-text-tertiary mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-white/[0.04] border border-white/[0.06] text-text-primary rounded-2xl px-4 py-3.5 pr-12 text-sm font-medium outline-none focus:border-accent-lime/40 focus:bg-white/[0.06] transition-all placeholder:text-text-tertiary"
                  placeholder="Enter password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text-secondary transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Remember + Forgot */}
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  defaultChecked
                  className="w-4 h-4 rounded border-white/[0.1] bg-white/[0.04] text-accent-lime focus:ring-accent-lime/20 accent-[#ccf381]"
                />
                <span className="text-sm text-text-secondary">Remember me</span>
              </label>
              <button type="button" className="text-sm text-accent-lime hover:underline font-medium">
                Forgot password?
              </button>
            </div>

            {/* Error */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-danger/10 border border-danger/20 rounded-2xl px-4 py-3 text-sm text-danger font-medium"
              >
                {error}
              </motion.div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-accent-lime text-[#050505] py-4 rounded-2xl font-bold text-sm uppercase tracking-wide hover:brightness-110 active:scale-[0.98] disabled:opacity-60 transition-all shadow-[0_0_30px_rgba(204,243,129,0.2)]"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-[#050505]/30 border-t-[#050505] rounded-full animate-spin" />
              ) : (
                <>
                  Sign In
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Bottom text */}
          <p className="text-center text-xs text-text-tertiary mt-8">
            Need access?{" "}
            <button type="button" className="text-accent-lime hover:underline font-medium">
              Contact support
            </button>
          </p>

          <p className="text-center text-[11px] text-text-tertiary/50 mt-3 lg:hidden">
            &copy; 2026 Craig AI &bull; A Creativedge tool
          </p>
        </motion.div>
      </div>
    </div>
  );
}
