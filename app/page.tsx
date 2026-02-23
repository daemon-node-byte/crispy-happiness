'use client'

import { useRouter } from 'next/navigation'

import { AuthForm } from '@/app/components/AuthForm'
import { AuthSuccessData } from '@/app/lib/types'

export default function Home() {
  const router = useRouter()

  function onAuthenticated(data: AuthSuccessData) {
    if (!data.session?.sessionId) {
      return
    }
    router.push('/dashboard')
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl items-center justify-center p-6">
      <AuthForm onAuthenticated={onAuthenticated} />
    </main>
  )
}
