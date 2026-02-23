"use client"
import { Canvas } from "@react-three/fiber"
import { OrbitControls, PerspectiveCamera } from "@react-three/drei"
import type { Building, FireProtection, GreenSpace, ParkingLot, Road, Utility } from "@/types/industrial-park"

interface ThreeJSViewerProps {
  layout?: {
    roads: Road[]
    buildings: Building[]
    greenSpaces: GreenSpace[]
    parking: ParkingLot[]
    utilities: Utility[]
    fireProtection: FireProtection[]
  }
  visibleLayers: {
    roads: boolean
    buildings: boolean
    greenSpace: boolean
    parking: boolean
    utilities: boolean
    fireProtection: boolean
  }
}

function Tree({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      <mesh position={[0, 4, 0]} castShadow>
        <cylinderGeometry args={[0.5, 0.8, 8, 8]} />
        <meshStandardMaterial color="#5D4037" roughness={0.9} />
      </mesh>
      <mesh position={[0, 10, 0]} castShadow>
        <sphereGeometry args={[4, 16, 16]} />
        <meshStandardMaterial color="#2E7D32" roughness={0.8} />
      </mesh>
    </group>
  )
}

function Building3D({ building, selected }: { building: Building; selected: boolean }) {
  const [width, depth] = building.size
  const height = building.height || building.floors * 4

  const colors = {
    manufacturing: "#E53935",
    warehouse: "#FB8C00",
    office: "#8E24AA",
    utility: "#FBC02D",
    mixed: "#5E35B1",
  }

  const color = colors[building.type]

  return (
    <group position={[0, 0, 0]}>
      {/* Building shadow */}
      <mesh position={[width * 0.05, 0.1, depth * 0.05]} receiveShadow>
        <boxGeometry args={[width, 0.2, depth]} />
        <meshStandardMaterial color="#000000" transparent opacity={0.3} />
      </mesh>

      {/* Main building structure */}
      <mesh position={[0, height / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[width, height, depth]} />
        <meshStandardMaterial color={selected ? "#FF1744" : color} roughness={0.7} metalness={0.3} />
      </mesh>

      {/* Roof */}
      <mesh position={[0, height + 0.5, 0]} castShadow>
        <boxGeometry args={[width + 1, 1, depth + 1]} />
        <meshStandardMaterial color="#424242" roughness={0.6} metalness={0.4} />
      </mesh>

      {/* Windows - only at high detail */}
      {building.floors > 1 && (
        <>
          {Array.from({ length: building.floors }).map((_, floor) => (
            <group key={`floor-${floor}`} position={[0, 4 * floor + 2, 0]}>
              {/* Front windows */}
              {Array.from({ length: Math.floor(width / 5) }).map((_, i) => (
                <mesh key={`window-front-${i}`} position={[-width / 2 + 2.5 + i * 5, 0, depth / 2 + 0.1]}>
                  <boxGeometry args={[2, 2, 0.2]} />
                  <meshStandardMaterial color="#90CAF9" emissive="#1976D2" emissiveIntensity={0.2} />
                </mesh>
              ))}
              {/* Side windows */}
              {Array.from({ length: Math.floor(depth / 5) }).map((_, i) => (
                <mesh key={`window-side-${i}`} position={[width / 2 + 0.1, 0, -depth / 2 + 2.5 + i * 5]}>
                  <boxGeometry args={[0.2, 2, 2]} />
                  <meshStandardMaterial color="#90CAF9" emissive="#1976D2" emissiveIntensity={0.2} />
                </mesh>
              ))}
            </group>
          ))}
        </>
      )}

      {/* Loading dock for manufacturing/warehouse */}
      {(building.type === "manufacturing" || building.type === "warehouse") && (
        <mesh position={[0, 2, -depth / 2 - 1]} castShadow>
          <boxGeometry args={[width * 0.4, 4, 2]} />
          <meshStandardMaterial color="#FFAB91" roughness={0.8} />
        </mesh>
      )}
    </group>
  )
}

function SceneContent({ layout, visibleLayers }: ThreeJSViewerProps) {
  // Convert geo coordinates to 3D positions
  const geoTo3D = (lat: number, lon: number): [number, number, number] => {
    const baseScale = 10000
    const x = (lon - 105.725) * baseScale
    const z = (21.053 - lat) * baseScale
    return [x, 0, z]
  }

  const roads = layout?.roads || []
  const buildings = layout?.buildings || []
  const greenSpaces = layout?.greenSpaces || []
  const parking = layout?.parking || []
  const utilities = layout?.utilities || []
  const fireProtection = layout?.fireProtection || []

  return (
    <>
      {/* Enhanced lighting */}
      <ambientLight intensity={0.5} />
      <directionalLight
        position={[300, 500, 300]}
        intensity={1.2}
        castShadow
        shadow-camera-left={-500}
        shadow-camera-right={500}
        shadow-camera-top={500}
        shadow-camera-bottom={-500}
        shadow-mapSize-width={4096}
        shadow-mapSize-height={4096}
      />
      <hemisphereLight args={["#87CEEB", "#8B7355", 0.6]} />

      {/* Ground plane */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow position={[0, 0, 0]}>
        <planeGeometry args={[2000, 2000]} />
        <meshStandardMaterial color="#E0E0E0" roughness={0.9} />
      </mesh>

      {/* Grid helper */}
      <gridHelper args={[2000, 100, "#BDBDBD", "#E0E0E0"]} />

      {/* Roads */}
      {visibleLayers.roads &&
        roads.map((road) => {
          const points = road.coordinates.map((coord) => geoTo3D(coord.latitude, coord.longitude))

          return (
            <group key={road.id}>
              {points.slice(0, -1).map((point, i) => {
                const nextPoint = points[i + 1]
                const dx = nextPoint[0] - point[0]
                const dz = nextPoint[2] - point[2]
                const length = Math.sqrt(dx * dx + dz * dz)
                const angle = Math.atan2(dx, dz)

                const colors = {
                  primary: "#607D8B",
                  secondary: "#78909C",
                  industrial: "#90A4AE",
                  service: "#B0BEC5",
                  fire: "#EF5350",
                }

                return (
                  <mesh
                    key={`${road.id}-segment-${i}`}
                    position={[(point[0] + nextPoint[0]) / 2, 0.25, (point[2] + nextPoint[2]) / 2]}
                    rotation={[0, angle, 0]}
                    receiveShadow
                  >
                    <boxGeometry args={[road.width, 0.5, length]} />
                    <meshStandardMaterial color={colors[road.type]} roughness={0.8} />
                  </mesh>
                )
              })}
            </group>
          )
        })}

      {/* Green Spaces */}
      {visibleLayers.greenSpace &&
        greenSpaces.map((space) => {
          const center = space.coordinates.reduce(
            (acc, coord) => {
              const pos = geoTo3D(coord.latitude, coord.longitude)
              return [acc[0] + pos[0], acc[1], acc[2] + pos[2]]
            },
            [0, 0, 0],
          )
          center[0] /= space.coordinates.length
          center[2] /= space.coordinates.length

          const avgSize = Math.sqrt(space.area) * 0.1

          return (
            <group key={space.id}>
              <mesh position={[center[0], 0.5, center[2]]} receiveShadow>
                <boxGeometry args={[avgSize, 1, avgSize]} />
                <meshStandardMaterial color="#81C784" transparent opacity={0.7} roughness={0.9} />
              </mesh>
              {/* Trees */}
              {Array.from({ length: Math.min(space.trees, 20) }).map((_, i) => {
                const angle = (i / space.trees) * Math.PI * 2
                const radius = avgSize * 0.3
                return (
                  <Tree
                    key={`tree-${space.id}-${i}`}
                    position={[center[0] + Math.cos(angle) * radius, 0, center[2] + Math.sin(angle) * radius]}
                  />
                )
              })}
            </group>
          )
        })}

      {/* Buildings */}
      {visibleLayers.buildings &&
        buildings.map((building) => {
          const pos = geoTo3D(building.coordinates.latitude, building.coordinates.longitude)
          return (
            <group key={building.id} position={pos}>
              <Building3D building={building} selected={false} />
            </group>
          )
        })}

      {/* Parking Lots */}
      {visibleLayers.parking &&
        parking.map((parkingLot) => {
          const pos = geoTo3D(parkingLot.coordinates.latitude, parkingLot.coordinates.longitude)
          const size = parkingLot.type === "truck" ? 70 : 50

          return (
            <group key={parkingLot.id} position={pos}>
              <mesh position={[0, 0.25, 0]} receiveShadow>
                <boxGeometry args={[size, 0.5, size]} />
                <meshStandardMaterial color="#9E9E9E" roughness={0.9} />
              </mesh>
              {/* Parking space lines */}
              {Array.from({ length: parkingLot.rows }).map((_, row) =>
                Array.from({ length: parkingLot.cols }).map((_, col) => (
                  <mesh
                    key={`space-${row}-${col}`}
                    position={[
                      -size / 2 + (col + 0.5) * (size / parkingLot.cols),
                      0.3,
                      -size / 2 + (row + 0.5) * (size / parkingLot.rows),
                    ]}
                  >
                    <boxGeometry args={[size / parkingLot.cols - 0.5, 0.1, size / parkingLot.rows - 0.5]} />
                    <meshStandardMaterial color="#757575" />
                  </mesh>
                )),
              )}
            </group>
          )
        })}

      {/* Utilities */}
      {visibleLayers.utilities &&
        utilities.map((utility) => {
          const pos = geoTo3D(utility.coordinates.latitude, utility.coordinates.longitude)

          const colors = {
            powerSubstation: "#FF6F00",
            waterTreatment: "#1976D2",
            waterStorage: "#0288D1",
            wasteCollection: "#43A047",
            sewage: "#0277BD",
            gasPipeline: "#F57C00",
          }

          return (
            <mesh key={utility.id} position={[pos[0], 10, pos[2]]} castShadow>
              <cylinderGeometry args={[8, 8, 20, 16]} />
              <meshStandardMaterial color={colors[utility.type]} roughness={0.5} metalness={0.6} />
            </mesh>
          )
        })}

      {/* Fire Protection */}
      {visibleLayers.fireProtection &&
        fireProtection.map((fire) => {
          const pos = geoTo3D(fire.coordinates.latitude, fire.coordinates.longitude)

          if (fire.type === "station") {
            return (
              <group key={fire.id} position={pos}>
                <mesh position={[0, 15, 0]} castShadow receiveShadow>
                  <boxGeometry args={[30, 30, 25]} />
                  <meshStandardMaterial color="#D32F2F" roughness={0.7} />
                </mesh>
                <mesh position={[0, 31, 0]} castShadow>
                  <boxGeometry args={[32, 2, 27]} />
                  <meshStandardMaterial color="#424242" roughness={0.6} />
                </mesh>
              </group>
            )
          } else {
            return (
              <mesh key={fire.id} position={[pos[0], 7.5, pos[2]]} castShadow>
                <coneGeometry args={[6, 15, 8]} />
                <meshStandardMaterial color="#F44336" roughness={0.6} metalness={0.3} />
              </mesh>
            )
          }
        })}
    </>
  )
}

export function ThreeJSViewer({ layout, visibleLayers }: ThreeJSViewerProps) {
  return (
    <div className="absolute inset-0">
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[500, 500, 500]} fov={50} near={1} far={5000} />
        <fog attach="fog" args={["#E0E0E0", 1000, 3000]} />
        <color attach="background" args={["#E0E0E0"]} />

        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          maxPolarAngle={Math.PI / 2.1}
          minDistance={100}
          maxDistance={1500}
          target={[0, 0, 0]}
        />

        <SceneContent layout={layout} visibleLayers={visibleLayers} />
      </Canvas>
    </div>
  )
}
