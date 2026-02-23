import React, { useState } from 'react';
import MapView from './components/MapView/MapView';
import './styles/design-system.css';

// Test data
const testBoundary: [number, number][] = [
  [21.0254, 105.8430],
  [21.0254, 105.8530],
  [21.0354, 105.8530],
  [21.0354, 105.8430],
  [21.0254, 105.8430],
];

function TestMapView() {
  const [designMode, setDesignMode] = useState(false);

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <MapView
        estateId="test-estate-1"
        boundary={testBoundary}
        centerCoords={[21.0304, 105.8480]}
        designMode={designMode}
        onToggleDesignMode={() => setDesignMode(!designMode)}
      />
    </div>
  );
}

export default TestMapView;
