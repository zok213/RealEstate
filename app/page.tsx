"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function Page() {
  const router = useRouter()
  
  useEffect(() => {
    // Redirect to dashboard with new UI
    router.push("/dashboard")
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a140e]">
      <div className="text-center">
        <div className="size-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-white font-medium">Loading EstateParser...</p>
      </div>
    </div>
  )
}
