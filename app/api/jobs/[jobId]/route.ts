import { NextRequest, NextResponse } from "next/server"

// Backend API URL
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8001"

export async function GET(
    req: NextRequest,
    { params }: { params: Promise<{ jobId: string }> }
) {
    try {
        const { jobId } = await params

        // Get job status from backend
        const res = await fetch(`${BACKEND_URL}/api/designs/jobs/${jobId}`)

        if (!res.ok) {
            throw new Error("Failed to fetch job status")
        }

        const data = await res.json()

        return NextResponse.json(data)

    } catch (error: any) {
        console.error("Get job status error:", error)
        return NextResponse.json(
            { error: error.message },
            { status: 500 }
        )
    }
}
