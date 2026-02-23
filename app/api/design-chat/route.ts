import { NextRequest, NextResponse } from "next/server"

export const maxDuration = 60

// Backend API URL
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8001"

// In-memory project ID (should be stored in session in production)
let currentProjectId: string | null = null

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json()

    // Get the last user message
    const lastMessage = messages[messages.length - 1]
    const userText = lastMessage?.parts?.find((p: any) => p.type === "text")?.text ||
      lastMessage?.content || ""

    // Create project if not exists
    if (!currentProjectId) {
      const createRes = await fetch(`${BACKEND_URL}/api/projects/new`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: "Chat Design Project",
          site_area_ha: 50
        })
      })

      if (!createRes.ok) {
        throw new Error("Failed to create project")
      }

      const projectData = await createRes.json()
      currentProjectId = projectData.project_id
    }

    // Send message to backend chat API
    const chatRes = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_id: currentProjectId,
        message: userText
      })
    })

    if (!chatRes.ok) {
      const errorText = await chatRes.text()
      throw new Error(`Chat API failed: ${errorText}`)
    }

    const chatData = await chatRes.json()

    // Format response for Vercel AI SDK UIMessage format
    const response = {
      id: `msg-${Date.now()}`,
      role: "assistant",
      parts: [
        {
          type: "text",
          text: chatData.response
        }
      ]
    }

    // If ready for design generation, trigger it
    if (chatData.ready_for_design) {
      // Trigger design generation in background
      fetch(`${BACKEND_URL}/api/designs/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: currentProjectId,
          use_chat_params: true
        })
      }).catch(console.error)

      // Add a tool result to the response
      response.parts.push({
        type: "tool-generateLayoutVariants",
        state: "input-available",
        input: {
          totalArea: chatData.extracted_params?.parameters?.totalArea_ha * 10000 || 500000,
          numberOfBuildings: chatData.extracted_params?.parameters?.industryFocus?.reduce(
            (sum: number, f: any) => sum + (f.count || 0), 0
          ) || 10,
          priorities: ["logistics", "safety"]
        }
      } as any)
    }

    return NextResponse.json(response)

  } catch (error: any) {
    console.error("Design chat error:", error)

    // Return a fallback response
    return NextResponse.json({
      id: `msg-${Date.now()}`,
      role: "assistant",
      parts: [
        {
          type: "text",
          text: `Xin chào! Tôi là AI trợ lý thiết kế khu công nghiệp.\n\nVui lòng cho tôi biết:\n1. **Diện tích** khu công nghiệp (hecta)\n2. **Ngành nghề** chính (sản xuất, logistics, kho bãi)\n3. **Số công nhân** dự kiến\n\n_Lưu ý: ${error.message}_`
        }
      ]
    })
  }
}

// GET endpoint to check status
export async function GET() {
  return NextResponse.json({
    status: "ready",
    backend_url: BACKEND_URL,
    project_id: currentProjectId
  })
}
