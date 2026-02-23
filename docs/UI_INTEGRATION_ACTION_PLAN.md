# Kế hoạch tích hợp UI Templates - Action Plan

**Dự án**: Industrial Estate Planning System  
**Timeline**: 4 tuần  
**Mục tiêu**: Tích hợp các UI patterns có giá trị từ templates vào dự án Next.js

---

## 🎯 Phase 1: CSS & Design System (Tuần 1)

### Mục tiêu
Thiết lập design tokens và visual language nhất quán

### Tasks

#### Task 1.1: Thêm Color Palette ⏱️ 1 hour
**File**: `tailwind.config.ts`

```typescript
// Thêm vào theme.extend.colors
const config = {
  theme: {
    extend: {
      colors: {
        // Industrial Estate brand colors
        estate: {
          green: {
            DEFAULT: '#36e27b',
            dark: '#2ab863',
            light: '#4eff8f',
            50: '#f0fdf6',
            100: '#dcfce9',
            500: '#36e27b',
            600: '#2ab863',
            700: '#219653',
          },
          surface: {
            dark: '#1b3224',
            darker: '#112117',
            border: '#254632',
            hover: '#2a4a38',
          }
        },
        // Semantic colors for estate planning
        plot: {
          available: '#10b981',
          reserved: '#f59e0b',
          sold: '#ef4444',
        },
        infrastructure: {
          road: '#6b7280',
          water: '#3b82f6',
          electric: '#f59e0b',
          green: '#22c55e',
        }
      }
    }
  }
}
```

**Testing**: Check colors in Storybook/component preview

---

#### Task 1.2: Add Custom Animations ⏱️ 1 hour
**File**: `app/globals.css`

```css
/* Thêm vào file */

/* Slide in animations */
@keyframes slideInLeft {
  0% {
    transform: translateX(-100%);
    opacity: 0;
  }
  100% {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideInRight {
  0% {
    transform: translateX(100%);
    opacity: 0;
  }
  100% {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideInUp {
  0% {
    transform: translateY(20px);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Fade animations */
@keyframes fadeIn {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

@keyframes fadeInScale {
  0% {
    opacity: 0;
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* Pulse animations */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes pulseScale {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

/* Shimmer loading */
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

/* Utility classes */
.animate-slide-in-left {
  animation: slideInLeft 0.3s ease-out;
}

.animate-slide-in-right {
  animation: slideInRight 0.3s ease-out;
}

.animate-slide-in-up {
  animation: slideInUp 0.3s ease-out;
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-in;
}

.animate-fade-in-scale {
  animation: fadeInScale 0.3s ease-out;
}

.animate-pulse-slow {
  animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.animate-pulse-scale {
  animation: pulseScale 2s ease-in-out infinite;
}

/* Loading shimmer effect */
.loading-shimmer {
  background: linear-gradient(
    90deg,
    #f0f0f0 0%,
    #e0e0e0 50%,
    #f0f0f0 100%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s infinite linear;
}

.dark .loading-shimmer {
  background: linear-gradient(
    90deg,
    #1f2937 0%,
    #374151 50%,
    #1f2937 100%
  );
}
```

**Testing**: Add animations to buttons, panels

---

#### Task 1.3: Create Design Tokens Library ⏱️ 1 hour
**File**: `lib/design-tokens.ts`

```typescript
/**
 * Design Tokens for Industrial Estate Planning System
 * Centralized design constants for consistency
 */

export const COLORS = {
  // Brand colors
  brand: {
    primary: '#36e27b',
    primaryDark: '#2ab863',
    primaryLight: '#4eff8f',
  },
  
  // Surface colors
  surface: {
    dark: '#1b3224',
    darker: '#112117',
    border: '#254632',
    hover: '#2a4a38',
  },
  
  // Status colors
  status: {
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
  },
  
  // Plot status
  plot: {
    available: '#10b981',
    reserved: '#f59e0b',
    sold: '#ef4444',
    pending: '#8b5cf6',
  },
  
  // Infrastructure
  infrastructure: {
    road: '#6b7280',
    water: '#3b82f6',
    electric: '#f59e0b',
    sewer: '#7c3aed',
    green: '#22c55e',
  },
} as const;

export const SPACING = {
  xs: '0.25rem',  // 4px
  sm: '0.5rem',   // 8px
  md: '1rem',     // 16px
  lg: '1.5rem',   // 24px
  xl: '2rem',     // 32px
  '2xl': '3rem',  // 48px
  '3xl': '4rem',  // 64px
} as const;

export const RADIUS = {
  sm: '0.375rem',  // 6px
  md: '0.5rem',    // 8px
  lg: '0.75rem',   // 12px
  xl: '1rem',      // 16px
  full: '9999px',
} as const;

export const SHADOWS = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
  glow: '0 0 20px rgba(54, 226, 123, 0.3)',
  glowStrong: '0 0 30px rgba(54, 226, 123, 0.5)',
} as const;

export const TRANSITIONS = {
  fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
  normal: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
  slow: '500ms cubic-bezier(0.4, 0, 0.2, 1)',
} as const;

export const TYPOGRAPHY = {
  fontFamily: {
    sans: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    mono: '"Fira Code", "Courier New", monospace',
  },
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem',// 30px
    '4xl': '2.25rem', // 36px
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
} as const;

export const BREAKPOINTS = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// Helper functions
export const getPlotColor = (status: 'available' | 'reserved' | 'sold' | 'pending') => {
  return COLORS.plot[status];
};

export const getInfrastructureColor = (type: keyof typeof COLORS.infrastructure) => {
  return COLORS.infrastructure[type];
};

export const getStatusColor = (status: 'success' | 'warning' | 'error' | 'info') => {
  return COLORS.status[status];
};
```

**Testing**: Import in components, verify types work

---

#### Task 1.4: Update Tailwind Config ⏱️ 30 mins
**File**: `tailwind.config.ts`

```typescript
import type { Config } from "tailwindcss"

const config = {
  // ... existing config
  theme: {
    extend: {
      // Add custom animations
      animation: {
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'slide-in-up': 'slideInUp 0.3s ease-out',
        'fade-in': 'fadeIn 0.5s ease-in',
        'fade-in-scale': 'fadeInScale 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-scale': 'pulseScale 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s infinite linear',
      },
      
      // Add custom keyframes
      keyframes: {
        slideInLeft: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInScale: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        pulseScale: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
      },
      
      // Add custom box shadows
      boxShadow: {
        'glow': '0 0 20px rgba(54, 226, 123, 0.3)',
        'glow-strong': '0 0 30px rgba(54, 226, 123, 0.5)',
      },
    },
  },
} satisfies Config

export default config
```

---

## 🎯 Phase 2: Chat Interface Enhancements (Tuần 2)

### Task 2.1: Add Typing Indicator ⏱️ 2 hours
**File**: `components/chat-interface.tsx`

```tsx
// Thêm component mới
const TypingIndicator = () => (
  <div className="flex items-center gap-2 p-3 bg-muted rounded-lg max-w-[80px]">
    <div className="flex gap-1">
      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" 
           style={{ animationDelay: '0ms' }} />
      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" 
           style={{ animationDelay: '150ms' }} />
      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" 
           style={{ animationDelay: '300ms' }} />
    </div>
  </div>
);

// Thêm vào ChatInterface component
export function ChatInterface() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/design-chat',
  });
  
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {/* Add typing indicator */}
        {isLoading && <TypingIndicator />}
      </div>
      
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <Input
          value={input}
          onChange={handleInputChange}
          placeholder="Ask about the design..."
          disabled={isLoading}
        />
      </form>
    </div>
  );
}
```

---

### Task 2.2: Add Message Actions ⏱️ 2 hours
**File**: `components/chat-message-actions.tsx`

```tsx
import { Copy, RotateCw, ThumbsUp, ThumbsDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from '@/components/ui/use-toast';

interface MessageActionsProps {
  content: string;
  onRegenerate?: () => void;
  onFeedback?: (type: 'positive' | 'negative') => void;
}

export function MessageActions({ content, onRegenerate, onFeedback }: MessageActionsProps) {
  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(content);
    toast({
      title: "Copied to clipboard",
      description: "Message content has been copied.",
    });
  };
  
  return (
    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8"
        onClick={copyToClipboard}
      >
        <Copy className="h-4 w-4" />
      </Button>
      
      {onRegenerate && (
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          onClick={onRegenerate}
        >
          <RotateCw className="h-4 w-4" />
        </Button>
      )}
      
      {onFeedback && (
        <>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => onFeedback('positive')}
          >
            <ThumbsUp className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => onFeedback('negative')}
          >
            <ThumbsDown className="h-4 w-4" />
          </Button>
        </>
      )}
    </div>
  );
}

// Update MessageBubble component
const MessageBubble = ({ message }) => (
  <div className={cn(
    "group flex gap-3 p-3 rounded-lg animate-slide-in-up",
    message.role === 'user' ? 'bg-primary/10' : 'bg-muted'
  )}>
    <Avatar>
      {message.role === 'user' ? <User /> : <Bot />}
    </Avatar>
    <div className="flex-1">
      <div className="prose prose-sm dark:prose-invert">
        {message.content}
      </div>
      <div className="mt-2">
        <MessageActions
          content={message.content}
          onRegenerate={message.role === 'assistant' ? handleRegenerate : undefined}
          onFeedback={handleFeedback}
        />
      </div>
    </div>
  </div>
);
```

---

### Task 2.3: Add Code Block Syntax Highlighting ⏱️ 2 hours

**Install**: `npm install react-syntax-highlighter @types/react-syntax-highlighter`

**File**: `components/code-block.tsx`

```tsx
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check } from 'lucide-react';
import { useState } from 'react';

export function CodeBlock({ code, language = 'typescript' }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false);
  
  const copyCode = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  return (
    <div className="relative group">
      <button
        onClick={copyCode}
        className="absolute right-2 top-2 p-2 rounded-md bg-muted hover:bg-muted/80 opacity-0 group-hover:opacity-100 transition-opacity"
      >
        {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
      </button>
      <SyntaxHighlighter
        language={language}
        style={oneDark}
        customStyle={{
          borderRadius: '0.5rem',
          padding: '1rem',
        }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}
```

---

## 🎯 Phase 3: File Upload Improvements (Tuần 3)

### Task 3.1: Add Upload Progress Bar ⏱️ 3 hours
**File**: `components/file-upload-zone.tsx`

```tsx
import { useState, useCallback } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

export function FileUploadZone() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isDragOver, setIsDragOver] = useState(false);
  
  const uploadFile = async (file: File) => {
    setUploading(true);
    setProgress(0);
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Simulate progress (in production, use XMLHttpRequest for real progress)
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percentComplete = (e.loaded / e.total) * 100;
        setProgress(percentComplete);
      }
    });
    
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        toast({
          title: "Upload successful",
          description: `${file.name} has been uploaded.`,
        });
      }
    });
    
    xhr.open('POST', '/api/dxf/upload');
    xhr.send(formData);
  };
  
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.name.endsWith('.dxf') || droppedFile.name.endsWith('.dwg'))) {
      setFile(droppedFile);
      uploadFile(droppedFile);
    }
  }, []);
  
  return (
    <div
      className={cn(
        "border-2 border-dashed rounded-lg p-8 transition-all",
        isDragOver && "border-primary bg-primary/5 scale-105",
        !isDragOver && "border-border"
      )}
      onDrop={handleDrop}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragOver(true);
      }}
      onDragLeave={() => setIsDragOver(false)}
    >
      {file ? (
        <div className="space-y-4 animate-fade-in-scale">
          <div className="flex items-center gap-3">
            <FileText className="h-10 w-10 text-primary" />
            <div className="flex-1">
              <p className="font-medium">{file.name}</p>
              <p className="text-sm text-muted-foreground">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => {
                setFile(null);
                setProgress(0);
              }}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          {uploading && (
            <div className="space-y-2">
              <Progress value={progress} className="h-2" />
              <p className="text-sm text-muted-foreground text-center">
                Uploading... {Math.round(progress)}%
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center animate-fade-in">
          <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
          <p className="text-lg font-medium mb-2">
            Drop your DXF/DWG file here
          </p>
          <p className="text-sm text-muted-foreground mb-4">
            or click to browse files
          </p>
          <Button onClick={() => document.getElementById('file-input')?.click()}>
            Select File
          </Button>
          <input
            id="file-input"
            type="file"
            accept=".dxf,.dwg"
            className="hidden"
            onChange={(e) => {
              const selectedFile = e.target.files?.[0];
              if (selectedFile) {
                setFile(selectedFile);
                uploadFile(selectedFile);
              }
            }}
          />
        </div>
      )}
    </div>
  );
}
```

---

## 🎯 Phase 4: Export Panel (Tuần 3-4)

### Task 4.1: Create Export Panel Component ⏱️ 4 hours
**File**: `components/export-panel.tsx`

```tsx
import { useState } from 'react';
import { Download, FileText, Image, Map } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';

type ExportFormat = 'dxf' | 'pdf' | 'png' | 'geojson';
type PaperSize = 'A0' | 'A1' | 'A2' | 'A3' | 'A4';

export function ExportPanel() {
  const [format, setFormat] = useState<ExportFormat>('dxf');
  const [paperSize, setPaperSize] = useState<PaperSize>('A0');
  const [includeMetadata, setIncludeMetadata] = useState(true);
  const [includeLegend, setIncludeLegend] = useState(true);
  const [scale, setScale] = useState('1:1000');
  const [exporting, setExporting] = useState(false);
  
  const handleExport = async () => {
    setExporting(true);
    
    try {
      const response = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          format,
          options: {
            paperSize: format === 'pdf' ? paperSize : undefined,
            scale,
            includeMetadata,
            includeLegend,
          },
        }),
      });
      
      if (!response.ok) throw new Error('Export failed');
      
      // Download file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `industrial-estate.${format}`;
      a.click();
      
      toast({
        title: "Export successful",
        description: `Design exported as ${format.toUpperCase()}`,
      });
    } catch (error) {
      toast({
        title: "Export failed",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setExporting(false);
    }
  };
  
  return (
    <div className="p-6 space-y-6 animate-slide-in-right">
      <div>
        <h3 className="text-lg font-semibold mb-2">Export Design</h3>
        <p className="text-sm text-muted-foreground">
          Export your industrial park design in various formats
        </p>
      </div>
      
      {/* Format Selection */}
      <div className="space-y-2">
        <Label>Export Format</Label>
        <Select value={format} onValueChange={(v) => setFormat(v as ExportFormat)}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="dxf">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                <span>DXF (AutoCAD)</span>
              </div>
            </SelectItem>
            <SelectItem value="pdf">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                <span>PDF (Print)</span>
              </div>
            </SelectItem>
            <SelectItem value="png">
              <div className="flex items-center gap-2">
                <Image className="h-4 w-4" />
                <span>PNG (Image)</span>
              </div>
            </SelectItem>
            <SelectItem value="geojson">
              <div className="flex items-center gap-2">
                <Map className="h-4 w-4" />
                <span>GeoJSON (GIS)</span>
              </div>
            </SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      {/* PDF Options */}
      {format === 'pdf' && (
        <div className="space-y-4 animate-fade-in-scale">
          <div className="space-y-2">
            <Label>Paper Size</Label>
            <Select value={paperSize} onValueChange={(v) => setPaperSize(v as PaperSize)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="A0">A0 (841 × 1189 mm)</SelectItem>
                <SelectItem value="A1">A1 (594 × 841 mm)</SelectItem>
                <SelectItem value="A2">A2 (420 × 594 mm)</SelectItem>
                <SelectItem value="A3">A3 (297 × 420 mm)</SelectItem>
                <SelectItem value="A4">A4 (210 × 297 mm)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label>Scale</Label>
            <Select value={scale} onValueChange={setScale}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1:500">1:500</SelectItem>
                <SelectItem value="1:1000">1:1000</SelectItem>
                <SelectItem value="1:2000">1:2000</SelectItem>
                <SelectItem value="1:5000">1:5000</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      )}
      
      {/* Options */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label htmlFor="metadata">Include Metadata</Label>
          <Switch
            id="metadata"
            checked={includeMetadata}
            onCheckedChange={setIncludeMetadata}
          />
        </div>
        <div className="flex items-center justify-between">
          <Label htmlFor="legend">Include Legend</Label>
          <Switch
            id="legend"
            checked={includeLegend}
            onCheckedChange={setIncludeLegend}
          />
        </div>
      </div>
      
      {/* Export Button */}
      <Button
        onClick={handleExport}
        disabled={exporting}
        className="w-full"
        size="lg"
      >
        {exporting ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Exporting...
          </>
        ) : (
          <>
            <Download className="mr-2 h-4 w-4" />
            Export {format.toUpperCase()}
          </>
        )}
      </Button>
    </div>
  );
}
```

---

## 📝 Testing Checklist

### Phase 1 Tests
- [ ] Color palette renders correctly in dark/light mode
- [ ] Animations play smoothly on component mount
- [ ] Design tokens import without TypeScript errors
- [ ] Tailwind classes generate correctly

### Phase 2 Tests
- [ ] Typing indicator appears during AI response
- [ ] Message actions (copy, regenerate) work correctly
- [ ] Code blocks highlight syntax properly
- [ ] Message bubbles animate on scroll

### Phase 3 Tests
- [ ] File drag-drop works
- [ ] Upload progress bar updates in real-time
- [ ] File preview shows correct metadata
- [ ] Cancel upload works mid-transfer

### Phase 4 Tests
- [ ] DXF export generates valid file
- [ ] PDF export respects paper size and scale
- [ ] PNG export captures current view
- [ ] GeoJSON export includes all geometry

---

## 🎯 Success Metrics

### Phase 1
- [ ] All colors accessible via Tailwind classes
- [ ] 0 compilation errors
- [ ] Visual consistency across components

### Phase 2
- [ ] Chat feels more responsive
- [ ] Users can easily copy AI responses
- [ ] Code examples readable

### Phase 3
- [ ] Upload completion rate >95%
- [ ] Users confident during upload process
- [ ] Clear error messages on failure

### Phase 4
- [ ] Exports succeed >99% of time
- [ ] Generated files valid in target software
- [ ] Export time <10 seconds

---

## 🚀 Deployment Steps

1. **Merge Phase 1** → Test in staging → Deploy to production
2. **Merge Phase 2** → Test chat functionality → Deploy
3. **Merge Phase 3** → Test upload with large files → Deploy
4. **Merge Phase 4** → Test all export formats → Deploy

**Estimated Timeline**: 4 weeks  
**Total Effort**: 25-30 hours  
**Risk Level**: Low (incremental changes)  
**ROI**: High (better UX, professional polish)
