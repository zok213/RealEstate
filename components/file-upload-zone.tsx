"use client"

import type React from "react"
import { useCallback, useState, useEffect, useRef } from "react"
import { Upload, File, X, CheckCircle2, AlertCircle, MapPin, Ruler, Square } from "lucide-react"
import { Button } from "@/components/ui/button"
import { parseFile, type SiteInfo } from "@/utils/file-parsers"
import { useDesign } from "@/contexts/design-context"

interface FileUploadZoneProps {
  selectedFile: File | null
  onFileSelect: (file: File | null) => void
}

export function FileUploadZone({ selectedFile, onFileSelect }: FileUploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<"idle" | "parsing" | "success" | "error">(
    selectedFile ? "success" : "idle"
  )
  const [parseError, setParseError] = useState<string | null>(null)
  const [localSiteInfo, setLocalSiteInfo] = useState<SiteInfo | null>(null)
  const pendingFileRef = useRef<File | null>(null)

  const { setSiteBoundary, setSiteInfo, siteInfo } = useDesign()

  // Use context siteInfo if available
  useEffect(() => {
    if (siteInfo && !localSiteInfo) {
      setLocalSiteInfo(siteInfo)
    }
  }, [siteInfo, localSiteInfo])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files[0]
    if (file && (
      file.name.endsWith(".dxf") ||
      file.name.endsWith(".dwg") || 
      file.name.endsWith(".dwg") ||
      file.name.endsWith(".geojson") || 
      file.name.endsWith(".json")
    )) {
      handleFileUpload(file)
    } else {
      setParseError("Chỉ hỗ trợ file DXF, DWG, hoặc GeoJSON")
      setUploadStatus("error")
    }
  }, [])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileUpload(file)
    }
  }, [])

  const handleFileUpload = async (file: File) => {
    setUploadStatus("parsing")
    setParseError(null)
    pendingFileRef.current = file
    onFileSelect(file)

    try {
      // Actually parse the file
      const result = await parseFile(file)

      if (result.success && result.boundary && result.info) {
        // Update context with parsed data
        setSiteBoundary(result.boundary)
        setSiteInfo(result.info)
        setLocalSiteInfo(result.info)
        setUploadStatus("success")
      } else {
        setParseError(result.error || "Failed to parse file")
        setUploadStatus("error")
      }
    } catch (err) {
      setParseError(err instanceof Error ? err.message : "Unknown error")
      setUploadStatus("error")
    }
  }

  const handleRemoveFile = () => {
    onFileSelect(null)
    setSiteBoundary(null)
    setSiteInfo(null)
    setLocalSiteInfo(null)
    setUploadStatus("idle")
    setParseError(null)
    pendingFileRef.current = null
  }

  // Success state with site info
  if (uploadStatus === "success" && selectedFile && localSiteInfo) {
    return (
      <div className="p-3 border-2 border-success/30 bg-success/5 rounded-lg space-y-3">
        <div className="flex items-start gap-2">
          <File className="w-4 h-4 text-success shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-foreground truncate">{selectedFile.name}</p>
            <div className="flex items-center gap-1.5 mt-1">
              <CheckCircle2 className="w-3 h-3 text-success" />
              <span className="text-xs text-success">ĐÃ PHÂN TÍCH</span>
            </div>
          </div>
          <Button variant="ghost" size="icon" className="w-6 h-6 shrink-0" onClick={handleRemoveFile}>
            <X className="w-3 h-3" />
          </Button>
        </div>

        {/* Site Info Display */}
        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-success/20">
          <div className="flex items-center gap-2 text-xs">
            <Square className="w-3 h-3 text-muted-foreground" />
            <span className="text-muted-foreground">Diện tích:</span>
            <span className="font-semibold text-foreground">{localSiteInfo.area_ha.toFixed(2)} ha</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <Ruler className="w-3 h-3 text-muted-foreground" />
            <span className="text-muted-foreground">Chu vi:</span>
            <span className="font-semibold text-foreground">{(localSiteInfo.perimeter_m / 1000).toFixed(2)} km</span>
          </div>
          <div className="flex items-center gap-2 text-xs col-span-2">
            <MapPin className="w-3 h-3 text-muted-foreground" />
            <span className="text-muted-foreground">Tọa độ:</span>
            <span className="font-mono text-foreground text-[10px]">
              {localSiteInfo.center.latitude.toFixed(5)}, {localSiteInfo.center.longitude.toFixed(5)}
            </span>
          </div>
          {localSiteInfo.layers && localSiteInfo.layers.length > 0 && (
            <div className="flex items-center gap-2 text-xs col-span-2">
              <span className="text-muted-foreground">Layers:</span>
              <span className="font-semibold text-foreground">{localSiteInfo.layers.length}</span>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Error state
  if (uploadStatus === "error") {
    return (
      <div className="p-3 border-2 border-destructive/30 bg-destructive/5 rounded-lg">
        <div className="flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-destructive shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-foreground truncate">{selectedFile?.name}</p>
            <p className="text-xs text-destructive mt-1 whitespace-pre-wrap">{parseError}</p>
          </div>
          <Button variant="ghost" size="icon" className="w-6 h-6 shrink-0" onClick={handleRemoveFile}>
            <X className="w-3 h-3" />
          </Button>
        </div>
      </div>
    )
  }

  // Parsing state
  if (uploadStatus === "parsing") {
    return (
      <div className="p-3 border-2 border-info/30 bg-info/5 rounded-lg">
        <div className="flex items-center gap-2 mb-2">
          <File className="w-4 h-4 text-info animate-pulse" />
          <span className="text-xs text-foreground flex-1 truncate">{selectedFile?.name}</span>
        </div>
        <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
          <div className="h-full bg-info animate-pulse" style={{ width: '60%' }} />
        </div>
        <p className="text-xs text-muted-foreground mt-1">Đang phân tích file...</p>
      </div>
    )
  }

  // Default upload zone
  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`
        relative border-2 border-dashed rounded-lg p-4 text-center cursor-pointer
        transition-all duration-200
        ${isDragging ? "border-success bg-success/5" : "border-border bg-background hover:border-info hover:bg-info/5"}
      `}
    >
      <input
        type="file"
        accept=".dxf,.geojson,.json,.kml,.kmz"
        onChange={handleFileInput}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />

      <Upload className={`w-6 h-6 mx-auto mb-2 ${isDragging ? "text-success" : "text-muted-foreground"}`} />
      <p className="text-xs text-foreground font-medium mb-1">
        {isDragging ? "Thả file vào đây để tải lên" : "Tải lên file DXF/GeoJSON"}
      </p>
      <p className="text-xs text-muted-foreground">Hỗ trợ DXF, GeoJSON</p>
    </div>
  )
}

