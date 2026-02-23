import { NextRequest, NextResponse } from "next/server"

// Backend API URL
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8001"

export async function GET(
    req: NextRequest,
    { params }: { params: Promise<{ projectId: string }> }
) {
    try {
        const { projectId } = await params

        // Get variants from backend
        const res = await fetch(`${BACKEND_URL}/api/designs/${projectId}/variants`)

        if (!res.ok) {
            throw new Error("Failed to fetch variants")
        }

        const data = await res.json()

        return NextResponse.json(data)

    } catch (error: any) {
        console.error("Get variants error:", error)
        return NextResponse.json(
            { error: error.message },
            { status: 500 }
        )
    }
}

export async function POST(
    req: NextRequest,
    { params }: { params: Promise<{ projectId: string }> }
) {
    try {
        const { projectId } = await params
        const body = await req.json()

        // Trigger design generation
        const res = await fetch(`${BACKEND_URL}/api/designs/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                project_id: projectId,
                parameters: body.parameters,
                use_chat_params: body.use_chat_params ?? false
            })
        })

        if (!res.ok) {
            throw new Error("Failed to trigger generation")
        }

        const data = await res.json()

        return NextResponse.json(data)

    } catch (error: any) {
        console.error("Generate designs error:", error)
        return NextResponse.json(
            { error: error.message },
            { status: 500 }
        )
    }
}
