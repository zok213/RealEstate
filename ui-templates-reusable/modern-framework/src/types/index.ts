// Type definitions for AIOptimize MVP

export interface Coordinates {
  x: number;
  y: number;
}

export interface PlotData {
  x: number;
  y: number;
  width: number;
  height: number;
  area: number;
  coords: number[][];
}

export interface LayoutMetrics {
  total_plots: number;
  total_area: number;
  avg_size: number;
  fitness: number;
  compliance: string;
}

export interface LayoutOption {
  id: number;
  name: string;
  icon: string;
  description: string;
  plots: PlotData[];
  metrics: LayoutMetrics;
}

export interface SiteMetadata {
  area: number;
  perimeter: number;
  bounds: number[];
  centroid: number[];
}

export interface GeoJSONGeometry {
  type: string;
  coordinates: number[][][];
}

export interface GeoJSONFeature {
  type: string;
  geometry: GeoJSONGeometry;
  properties?: Record<string, unknown>;
}

// Design Mode Types (Version 2.0)
export interface Estate {
  id: string;
  name: string;
  location: string;
  province: string;
  area: number;
  totalPlots: number;
  status: 'active' | 'draft' | 'archived';
  boundary: GeoJSON.Feature<GeoJSON.Polygon>;
  boundaryCoords?: [number, number][];
  centerCoords?: [number, number];
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, any>;
}

export interface Road {
  id: string;
  estateId: string;
  name: string;
  type: 'primary' | 'secondary' | 'service';
  width: number;
  length: number;
  color: string;
  geometry: GeoJSON.Feature<GeoJSON.LineString>;
  properties?: {
    surface?: string;
    speedLimit?: number;
    lanes?: number;
  };
}

export interface Building {
  id: string;
  estateId: string;
  name: string;
  type: 'factory' | 'warehouse' | 'administration' | 'parking' | 'greenhouse' | 'water_treatment' | 'power_station' | 'loading_bay';
  area: number;
  height?: number;
  rotation?: number;
  geometry: GeoJSON.Feature<GeoJSON.Polygon>;
  properties?: Record<string, any>;
}

export interface DesignElement {
  id: string;
  type: 'road' | 'building' | 'plot' | 'utility' | 'green_area';
  geometry: GeoJSON.Geometry;
  properties: Record<string, any>;
  style?: {
    color?: string;
    fillColor?: string;
    weight?: number;
    opacity?: number;
  };
}

export interface DrawingTool {
  id: 'road' | 'building' | 'boundary' | 'delete' | 'split' | 'merge' | 'color' | 'measure';
  name: string;
  icon: string;
  active: boolean;
  mode?: 'freehand' | 'snap-to-grid' | 'snap-to-element';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  suggestions?: string[];
  actions?: ChatAction[];
}

export interface ChatAction {
  type: 'draw_road' | 'place_building' | 'edit_properties' | 'calculate' | 'export';
  label: string;
  parameters?: Record<string, any>;
}

export interface DesignState {
  currentTool: DrawingTool | null;
  selectedElement: DesignElement | null;
  elements: DesignElement[];
  layers: {
    plots: boolean;
    roads: boolean;
    buildings: boolean;
    utilities: boolean;
    greenAreas: boolean;
  };
  snapToGrid: boolean;
  gridSize: number;
  history: DesignElement[][];
  historyIndex: number;
}

export interface Session {
  id: string;
  boundary: any;
  boundary_coords?: [number, number][];
  metadata?: {
    estate_name?: string;
    location?: string;
    province?: string;
    center_coords?: [number, number];
  };
  layouts?: any[];
  chat_history?: any[];
  created_at: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  model?: string;
  timestamp?: string;
}

export interface UploadResponse {
  session_id: string;
  boundary: GeoJSONFeature;
  metadata: SiteMetadata;
}

export interface GenerateResponse {
  session_id: string;
  options: LayoutOption[];
  count: number;
}

export interface ChatResponse {
  message: string;
  model: 'gemini-2.0-flash' | 'fallback';
}

export interface AppState {
  sessionId: string | null;
  boundary: GeoJSONFeature | null;
  boundaryCoords: number[][] | null;
  metadata: SiteMetadata | null;
  options: LayoutOption[];
  selectedOption: number | null;
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
}
