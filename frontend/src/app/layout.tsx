import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CineMind',
  description: 'Grounded AI-powered movie recommendations',
  icons: {
    icon: '/icon.svg',
    apple: '/apple-touch-icon.png',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col bg-[#0B0B0E] text-white">
        {children}
      </body>
    </html>
  );
}
