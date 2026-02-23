"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Plus, Minus, Maximize2, Layers, Eye, EyeOff, Box, Map, Satellite } from "lucide-react"
import { MapboxCanvas } from "@/components/mapbox-canvas"
import { DeckGLCanvas } from "@/components/deckgl-canvas"
import { ThreeJSViewer } from "@/components/threejs-viewer"
import { Card } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { IndustrialParkLayout } from "@/types/industrial-park"
import { useDesign } from "@/contexts/design-context"

interface MapCanvasProps {
  isAIMode: boolean
  currentLayout?: IndustrialParkLayout
}

export function MapCanvas({ isAIMode, currentLayout }: MapCanvasProps) {
  const [zoom, setZoom] = useState(14)
  const [showLayers, setShowLayers] = useState(false)
  const [is3DView, setIs3DView] = useState(false)
  const [showCompliance, setShowCompliance] = useState(false)
  const [useMapbox, setUseMapbox] = useState(true) // Use Mapbox by default
  const [mapStyle, setMapStyle] = useState<"satellite" | "streets" | "light" | "dark">("satellite")
  const [visibleLayers, setVisibleLayers] = useState({
    roads: true,
    buildings: true,
    greenSpace: true,
    parking: true,
    utilities: true,
    fireProtection: true,
  })

  // Get real variants from backend context
  const { variants, selectedVariant: contextSelectedVariant, siteInfo } = useDesign()
  const hasRealData = variants.length > 0

  // Use currentLayout from props (from backend) or undefined for empty map
  const activeLayout = currentLayout

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 1, 20))
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 1, 1))

  const toggleLayer = (layer: keyof typeof visibleLayers) => {
    setVisibleLayers((prev) => ({ ...prev, [layer]: !prev[layer] }))
  }


  return (
    <div className="flex-1 relative bg-muted/30">
      {is3DView ? (
        <ThreeJSViewer layout={activeLayout} visibleLayers={visibleLayers} />
      ) : useMapbox ? (
        <MapboxCanvas
          zoom={zoom}
          layout={activeLayout}
          visibleLayers={visibleLayers}
          mapStyle={mapStyle}
        />
      ) : (
        <DeckGLCanvas zoom={zoom} layout={activeLayout} visibleLayers={visibleLayers} />
      )}

      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10">
        <div className="flex items-center bg-card/95 backdrop-blur-sm border border-border rounded-lg shadow-lg overflow-hidden">
          <button
            onClick={() => { setIs3DView(false); setUseMapbox(true); }}
            className={`px-4 py-2 text-sm font-medium transition-all flex items-center gap-2 ${!is3DView && useMapbox
              ? "bg-primary text-primary-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
          >
            <Satellite className="w-4 h-4" />
            Mapbox
          </button>
          <div className="w-px h-8 bg-border" />
          <button
            onClick={() => { setIs3DView(false); setUseMapbox(false); }}
            className={`px-4 py-2 text-sm font-medium transition-all flex items-center gap-2 ${!is3DView && !useMapbox
              ? "bg-primary text-primary-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
          >
            <Layers className="w-4 h-4" />
            2D Canvas
          </button>
          <div className="w-px h-8 bg-border" />
          <button
            onClick={() => setIs3DView(true)}
            className={`px-4 py-2 text-sm font-medium transition-all flex items-center gap-2 ${is3DView
              ? "bg-primary text-primary-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
          >
            <Box className="w-4 h-4" />
            3D View
          </button>
        </div>
      </div>

      {/* Map style selector for Mapbox */}
      {!is3DView && useMapbox && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 z-10">
          <div className="flex items-center bg-card/90 backdrop-blur-sm border border-border rounded-md shadow-md overflow-hidden">
            {(["satellite", "streets", "light", "dark"] as const).map((style) => (
              <button
                key={style}
                onClick={() => setMapStyle(style)}
                className={`px-3 py-1.5 text-xs font-medium transition-all capitalize ${mapStyle === style
                  ? "bg-primary/20 text-primary"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                  }`}
              >
                {style}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Zoom controls - positioned to avoid sidebar overlap */}
      <div className="absolute top-20 left-4 flex flex-col gap-3 z-20">
        {/* Zoom controls group */}
        <div className="flex flex-col gap-2">
          <Button
            size="icon"
            variant="secondary"
            className="w-10 h-10 bg-card hover:bg-accent shadow-lg border border-border rounded-lg transition-smooth"
            onClick={handleZoomIn}
          >
            <Plus className="w-5 h-5 text-foreground" />
          </Button>
          <Button
            size="icon"
            variant="secondary"
            className="w-10 h-10 bg-card hover:bg-accent shadow-lg border border-border rounded-lg transition-smooth"
            onClick={handleZoomOut}
          >
            <Minus className="w-5 h-5 text-foreground" />
          </Button>
          <Button
            size="icon"
            variant="secondary"
            className="w-10 h-10 bg-card hover:bg-accent shadow-lg border border-border rounded-lg transition-smooth"
            onClick={() => setZoom(14)}
          >
            <Maximize2 className="w-4 h-4 text-foreground" />
          </Button>
        </div>

        <div className="h-px bg-border/50 my-1" />

        <Button
          size="icon"
          variant="secondary"
          className={`w-10 h-10 shadow-lg border border-border rounded-lg transition-smooth ${showLayers ? "bg-primary text-primary-foreground hover:bg-primary/90" : "bg-card hover:bg-accent"
            }`}
          onClick={() => setShowLayers(!showLayers)}
          title="Quản lý layers"
        >
          <Layers className="w-4 h-4" />
        </Button>
      </div>

      {showLayers && (
        <div className="absolute top-4 right-16 mr-2">
          <Card className="p-3 shadow-xl w-64 backdrop-blur-sm bg-card/98 border border-border">
            <h3 className="text-xs font-bold mb-3 text-foreground uppercase tracking-wide flex items-center gap-2">
              <Layers className="w-3.5 h-3.5" />
              Quản lý Layers
            </h3>
            <div className="space-y-1.5">
              <LayerToggle
                label="Đường giao thông"
                color="bg-[#2196F3]"
                checked={visibleLayers.roads}
                onChange={() => toggleLayer("roads")}
              />
              <LayerToggle
                label="Nhà máy & Nhà xưởng"
                color="bg-[#E53935]"
                checked={visibleLayers.buildings}
                onChange={() => toggleLayer("buildings")}
              />
              <LayerToggle
                label="Cây xanh & Không gian xanh"
                color="bg-[#4CAF50]"
                checked={visibleLayers.greenSpace}
                onChange={() => toggleLayer("greenSpace")}
              />
              <LayerToggle
                label="Bãi đậu xe"
                color="bg-[#9E9E9E]"
                checked={visibleLayers.parking}
                onChange={() => toggleLayer("parking")}
              />
              <LayerToggle
                label="PCCC"
                color="bg-[#D32F2F]"
                checked={visibleLayers.fireProtection}
                onChange={() => toggleLayer("fireProtection")}
              />
              <LayerToggle
                label="Tiện ích"
                color="bg-[#FF9800]"
                checked={visibleLayers.utilities}
                onChange={() => toggleLayer("utilities")}
              />
            </div>
          </Card>
        </div>
      )}

      {/* Compliance Panel - Only show when in AI mode, positioned below controls */}
      {isAIMode && (
        <div className="absolute top-20 left-4 w-64 z-20">
          <Card className="backdrop-blur-sm bg-card/98 border border-border shadow-xl overflow-hidden">
            {!hasRealData ? (
              // Empty state when no real data - compact
              <div className="p-3 text-center">
                <div className="flex items-center justify-center gap-2 mb-1">
                  <span className="text-base">📋</span>
                  <h3 className="text-xs font-bold text-foreground uppercase">Kiểm tra tuân thủ</h3>
                </div>
                <p className="text-xs text-muted-foreground">
                  Tạo thiết kế để xem báo cáo
                </p>
              </div>
            ) : !showCompliance ? (
              // Collapsed state with real data
              <button
                onClick={() => setShowCompliance(true)}
                className="w-full flex items-center justify-between p-3 hover:bg-accent/30 transition-fast group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-fast">
                    <span className="text-base">📋</span>
                  </div>
                  <div className="text-left">
                    <h3 className="text-xs font-bold text-foreground uppercase tracking-wide">Kiểm tra tuân thủ</h3>
                    <p className="text-xs text-muted-foreground">
                      {contextSelectedVariant?.compliance?.overall_score
                        ? `${Math.round(contextSelectedVariant.compliance.overall_score)}% đạt chuẩn`
                        : "Đang phân tích..."}
                    </p>
                  </div>
                </div>
              </button>
            ) : (
              // Expanded state with real data
              <>
                <div className="p-3 border-b border-border/50">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center">
                        <span className="text-sm">📋</span>
                      </div>
                      <h3 className="text-xs font-bold text-foreground uppercase tracking-wide">Kiểm tra tuân thủ</h3>
                    </div>
                    <button
                      onClick={() => setShowCompliance(false)}
                      className="text-muted-foreground hover:text-foreground transition-fast"
                    >
                      <Minus className="w-4 h-4" />
                    </button>
                  </div>

                  <div>
                    <label className="text-xs text-muted-foreground mb-1.5 block">Đang đánh giá:</label>
                    <p className="text-xs font-medium text-foreground">
                      {contextSelectedVariant?.name || "Chọn phương án"}
                    </p>
                  </div>
                </div>

                {/* Summary with progress */}
                <div className="px-3 py-2 bg-accent/20">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-medium text-foreground">Tổng quan</span>
                    <span className="text-sm font-bold text-success">
                      {contextSelectedVariant?.compliance?.overall_score
                        ? `${Math.round(contextSelectedVariant.compliance.overall_score)}%`
                        : "N/A"}
                    </span>
                  </div>
                  <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-success rounded-full"
                      style={{
                        width: `${contextSelectedVariant?.compliance?.overall_score || 0}%`
                      }}
                    />
                  </div>
                </div>

                <div className="px-3 pb-3 pt-2 space-y-1.5">
                  {contextSelectedVariant?.compliance?.details ? (
                    // Real compliance data from backend
                    Object.entries(contextSelectedVariant.compliance.details).map(([key, item]: [string, any]) => (
                      <ComplianceItemDetail
                        key={key}
                        icon={getComplianceIcon(key)}
                        label={item.label || key}
                        status={item.passed ? "pass" : "warning"}
                        value={item.passed ? "Đạt" : "Kiểm tra"}
                        detail={item.detail || ""}
                      />
                    ))
                  ) : (
                    // Fallback when no detailed compliance data
                    <p className="text-xs text-muted-foreground text-center py-2">
                      Không có dữ liệu chi tiết
                    </p>
                  )}
                </div>
              </>
            )}
          </Card>
        </div>
      )}

      <div className="absolute bottom-4 left-4 bg-card/95 backdrop-blur border border-border rounded-md px-3 py-2 text-xs text-muted-foreground font-mono shadow-md">
        📍 105.724010, 21.051602 | Zoom: {zoom}
      </div>
    </div>
  )
}

function getComplianceIcon(key: string): string {
  const icons: Record<string, string> = {
    roads: "🛣️",
    green_space: "🌳",
    fire_safety: "🚒",
    parking: "🚗",
    utilities: "⚡",
    spacing: "📐",
    boundary: "🔲",
  }
  return icons[key] || "📋"
}

function ComplianceIcon({ status }: { status: "pass" | "warning" | "error" }) {
  const statusColors = {
    pass: "bg-success",
    warning: "bg-warning",
    error: "bg-destructive",
  }

  return <div className={`w-2 h-2 rounded-full ${statusColors[status]}`} />
}

function ComplianceItemDetail({
  icon,
  label,
  status,
  value,
  detail,
}: {
  icon: string
  label: string
  status: "pass" | "warning" | "error"
  value: string
  detail: string
}) {
  const statusColors = {
    pass: "text-success",
    warning: "text-warning",
    error: "text-destructive",
  }

  const statusIcons = {
    pass: "✓",
    warning: "⚠",
    error: "✕",
  }

  return (
    <div className="group px-2.5 py-2 rounded-md hover:bg-accent/40 transition-fast cursor-pointer" title={detail}>
      <div className="flex items-center justify-between mb-0.5">
        <div className="flex items-center gap-2">
          <span className="text-sm">{icon}</span>
          <span className="text-xs font-medium text-foreground">{label}</span>
        </div>
        <span className={`font-bold text-xs ${statusColors[status]} flex items-center gap-1`}>
          <span className={status === "warning" ? "animate-pulse" : ""}>{statusIcons[status]}</span>
          {value}
        </span>
      </div>
      <p className="text-xs text-muted-foreground pl-6 opacity-0 group-hover:opacity-100 transition-fast">{detail}</p>
    </div>
  )
}

function LayerToggle({
  label,
  color,
  checked,
  onChange,
}: { label: string; color: string; checked: boolean; onChange: () => void }) {
  return (
    <button
      onClick={onChange}
      className="flex items-center gap-3 p-2 rounded-md hover:bg-accent/50 transition-fast cursor-pointer w-full"
    >
      {checked ? (
        <Eye className="w-4 h-4 text-primary flex-shrink-0" />
      ) : (
        <EyeOff className="w-4 h-4 text-muted-foreground flex-shrink-0" />
      )}
      <span className={`w-3 h-3 rounded-full ${color} ${!checked && "opacity-40"} flex-shrink-0`} />
      <span className={`text-sm flex-1 text-left ${checked ? "text-foreground font-medium" : "text-muted-foreground"}`}>
        {label}
      </span>
    </button>
  )
}
