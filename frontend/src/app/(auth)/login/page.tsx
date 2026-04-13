export default function LoginPage() {
  return (
    <div className="fixed inset-0 bg-bg-primary flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-accent to-neon-green bg-clip-text text-transparent">
            Social Tracker
          </h1>
          <p className="text-sm text-text-secondary mt-2">
            Sign in to your dashboard
          </p>
        </div>

        {/* Form */}
        <form className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5">
              Email
            </label>
            <input
              type="email"
              placeholder="you@company.com"
              className="w-full bg-bg-card border border-border rounded-lg px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-all"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5">
              Password
            </label>
            <input
              type="password"
              placeholder="••••••••"
              className="w-full bg-bg-card border border-border rounded-lg px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-all"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-accent text-bg-primary font-bold py-3 rounded-lg text-sm uppercase tracking-wider hover:brightness-110 transition-all active:scale-[0.98]"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
