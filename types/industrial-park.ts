export interface Point2D {
  x: number
  y: number
}

export interface GeoCoordinate {
  latitude: number
  longitude: number
}

export interface Road {
  id: string
  coordinates: GeoCoordinate[]
  width: number
  type: "primary" | "secondary" | "industrial" | "service" | "fire"
  name: string
  lanes?: number
  surfaceType?: "asphalt" | "concrete" | "gravel"
  trafficFlow?: "bidirectional" | "oneway"
}

export interface BuildingZones {
  production?: number
  office?: number
  storage?: number
  loading?: number
  utilities?: number
}

export interface Building {
  id: string
  coordinates: GeoCoordinate
  size: [number, number] // width, height in meters
  type: "manufacturing" | "warehouse" | "office" | "utility" | "mixed"
  name: string
  floors: number
  zones: BuildingZones
  height?: number // in meters
  capacity?: {
    workers?: number
    productionArea?: number
    storageVolume?: number
  }
  status?: "available" | "reserved" | "sold" | "planning"
}

export interface GreenSpace {
  id: string
  coordinates: GeoCoordinate[]
  area: number // square meters
  trees: number
  type: "park" | "greenBelt" | "buffer" | "garden"
  features?: string[]
}

export interface ParkingLot {
  id: string
  coordinates: GeoCoordinate
  spaces: number
  type: "car" | "truck" | "mixed"
  rows: number
  cols: number
  surfaceType?: "paved" | "gravel" | "grass"
  covered?: boolean
}

export interface Utility {
  id: string
  coordinates: GeoCoordinate
  type: "powerSubstation" | "waterTreatment" | "waterStorage" | "wasteCollection" | "sewage" | "gasPipeline"
  label: string
  capacity: string
  status?: "operational" | "maintenance" | "planned"
}

export interface FireProtection {
  id: string
  coordinates: GeoCoordinate
  type: "hydrant" | "station" | "extinguisher" | "alarm"
  label: string
  coverage?: number // radius in meters
  pressure?: string
}

export interface IndustrialParkLayout {
  id: string
  name: string
  totalArea: number // square meters
  roads: Road[]
  buildings: Building[]
  greenSpaces: GreenSpace[]
  parking: ParkingLot[]
  utilities: Utility[]
  fireProtection: FireProtection[]
  metadata: {
    createdAt: Date
    updatedAt: Date
    version: string
    author?: string
  }
}

export interface ComplianceCheck {
  roadNetwork: {
    passed: boolean
    score: number
    details: string
  }
  greenSpace: {
    passed: boolean
    percentage: number
    required: number
    details: string
  }
  fireProtection: {
    passed: boolean
    coverage: number
    details: string
  }
  parking: {
    passed: boolean
    spaces: number
    required: number
    details: string
  }
  utilities: {
    passed: boolean
    details: string
  }
  overallScore: number
  overallPassed: boolean
}

export interface DesignVariant {
  id: string
  name: string
  layout: IndustrialParkLayout
  score: number
  metrics: {
    flow: "High" | "Med" | "Low"
    greenRatio: string
    safety: "Pass" | "Warning" | "Fail"
    efficiency: string
  }
  compliance: ComplianceCheck
  optimizationGoals: string[]
  generatedAt: Date
}

export interface DesignRequirements {
  totalArea: number
  numberOfBuildings: number
  buildingTypes: {
    manufacturing?: number
    warehouse?: number
    office?: number
  }
  priorities: ("logistics" | "safety" | "green_space" | "efficiency" | "community")[]
  constraints?: {
    minGreenSpace?: number
    maxBuildingHeight?: number
    requiredParkingSpaces?: number
    specialRequirements?: string
  }
}
