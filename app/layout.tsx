import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Astarot',
  description: 'Tarot + Astrology web app MVP',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen bg-zinc-950 text-zinc-100`}>
        {children}
      </body>
    </html>
  )
}
