'use client';

export default function BackgroundGlow() {
  return (
    <>
      {/* Red glow top-center */}
      <div
        className="pointer-events-none fixed left-1/2 top-0 z-0 -translate-x-1/2"
        style={{
          width: '900px',
          height: '600px',
          background:
            'radial-gradient(ellipse at 50% 0%, rgba(255, 31, 45, 0.07) 0%, transparent 60%)',
        }}
        aria-hidden="true"
      />

      {/* Subtle blue glow bottom-left */}
      <div
        className="pointer-events-none fixed bottom-0 left-0 z-0"
        style={{
          width: '600px',
          height: '450px',
          background:
            'radial-gradient(ellipse at 30% 100%, rgba(59, 130, 246, 0.03) 0%, transparent 70%)',
        }}
        aria-hidden="true"
      />

      {/* Warm glow bottom-right */}
      <div
        className="pointer-events-none fixed bottom-0 right-0 z-0"
        style={{
          width: '500px',
          height: '400px',
          background:
            'radial-gradient(ellipse at 70% 100%, rgba(245, 158, 11, 0.025) 0%, transparent 70%)',
        }}
        aria-hidden="true"
      />

      {/* Vignette */}
      <div
        className="pointer-events-none fixed inset-0 z-0"
        style={{
          background:
            'radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.4) 100%)',
        }}
        aria-hidden="true"
      />
    </>
  );
}
