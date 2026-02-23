"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MapPin, Ruler, Building2, TreePine, CheckCircle2 } from "lucide-react"

interface DXFAnalysis {
  site_info: {
    area_ha: number
    area_m2: number
    dimensions: {
      width_m: number
      height_m: number
      perimeter_m: number
    }
  }
  suggestions: {
    project_scale: string
    estimated_plots: number
    land_use_breakdown: {
      salable_area_ha: number
      green_area_ha: number
      utility_area_ha: number
    }
    building_recommendations: {
      description: string
      plot_size_range: string
      building_height: string
    }
  }
  questions: Array<{
    question: string
    options?: string[]
    why?: string
  }>
  sample_prompts: string[]
  ai_greeting?: string
}

interface DXFAnalysisCardProps {
  analysis: DXFAnalysis
  onPromptSelect: (prompt: string) => void
}

export function DXFAnalysisCard({ analysis, onPromptSelect }: DXFAnalysisCardProps) {
  const { site_info, suggestions, questions, sample_prompts } = analysis

  return (
    <div className="space-y-4 animate-in fade-in-50 duration-500">
      {/* Site Info Card */}
      <Card className="p-4 bg-gradient-to-br from-green-50 to-blue-50 border-green-200">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-green-100">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-green-900 mb-2">
              ✅ Phân tích DXF thành công!
            </h3>
            
            {/* Site metrics */}
            <div className="grid grid-cols-2 gap-3 mb-3">
              <div className="flex items-center gap-2 text-sm">
                <MapPin className="h-4 w-4 text-green-600" />
                <div>
                  <div className="text-gray-600">Diện tích</div>
                  <div className="font-semibold text-green-900">
                    {site_info.area_ha} ha
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2 text-sm">
                <Ruler className="h-4 w-4 text-blue-600" />
                <div>
                  <div className="text-gray-600">Kích thước</div>
                  <div className="font-semibold text-blue-900">
                    {Math.round(site_info.dimensions.width_m)}m × {Math.round(site_info.dimensions.height_m)}m
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2 text-sm">
                <Building2 className="h-4 w-4 text-orange-600" />
                <div>
                  <div className="text-gray-600">Quy mô</div>
                  <div className="font-semibold text-orange-900">
                    ~{suggestions.estimated_plots} plots
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2 text-sm">
                <TreePine className="h-4 w-4 text-emerald-600" />
                <div>
                  <div className="text-gray-600">Green area</div>
                  <div className="font-semibold text-emerald-900">
                    {suggestions.land_use_breakdown.green_area_ha.toFixed(1)} ha
                  </div>
                </div>
              </div>
            </div>

            {/* Project scale */}
            <div className="text-sm text-gray-700 mb-2">
              <span className="font-medium">Quy mô dự án:</span>{" "}
              <span className="text-blue-600 font-semibold">
                {suggestions.project_scale.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </span>
            </div>

            {/* Building recommendations */}
            <div className="text-sm text-gray-700 bg-white/50 rounded p-2">
              <div className="font-medium mb-1">💡 Gợi ý theo IEAT Thailand:</div>
              <div className="text-xs space-y-1">
                <div>• Salable: {suggestions.land_use_breakdown.salable_area_ha.toFixed(1)} ha (77%)</div>
                <div>• {suggestions.building_recommendations.description}</div>
                <div>• Plot size: {suggestions.building_recommendations.plot_size_range}</div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Quick Prompts */}
      <Card className="p-4">
        <h4 className="font-semibold mb-3 flex items-center gap-2">
          <span>📝</span> Prompt mẫu - Click để sử dụng ngay:
        </h4>
        <div className="space-y-2">
          {sample_prompts.map((prompt, idx) => (
            <Button
              key={idx}
              variant="outline"
              className="w-full text-left justify-start h-auto py-3 px-4 hover:bg-blue-50 hover:border-blue-300"
              onClick={() => onPromptSelect(prompt)}
            >
              <div className="text-sm">
                <div className="font-medium text-blue-600 mb-1">
                  {idx === 0 ? "🚀 Simple" : idx === 1 ? "📊 Detailed" : "🎯 Advanced"}
                </div>
                <div className="text-gray-700 line-clamp-2">{prompt}</div>
              </div>
            </Button>
          ))}
        </div>
      </Card>

      {/* Questions */}
      {questions && questions.length > 0 && (
        <Card className="p-4 bg-amber-50 border-amber-200">
          <h4 className="font-semibold mb-3 text-amber-900">
            ❓ Câu hỏi hỗ trợ (để AI hiểu rõ hơn):
          </h4>
          <div className="space-y-3">
            {questions.slice(0, 3).map((q, idx) => (
              <div key={idx} className="text-sm">
                <div className="font-medium text-amber-900 mb-1">{q.question}</div>
                {q.options && (
                  <div className="text-xs text-amber-700 ml-4">
                    Options: {q.options.slice(0, 3).join(', ')}
                    {q.options.length > 3 && '...'}
                  </div>
                )}
              </div>
            ))}
          </div>
          <div className="mt-3 text-xs text-amber-700">
            💬 Bạn có thể trả lời các câu hỏi này trong chat hoặc dùng prompt mẫu ở trên
          </div>
        </Card>
      )}
    </div>
  )
}
