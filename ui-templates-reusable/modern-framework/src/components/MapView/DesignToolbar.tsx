import React from 'react';
import { useDesignStore } from '../../store/designStore';
import { DrawingTool } from '../../types';
import './DesignToolbar.css';

const tools: DrawingTool[] = [
  { id: 'road', name: 'Draw Road', icon: '✏️', active: false },
  { id: 'building', name: 'Add Building', icon: '🏢', active: false },
  { id: 'boundary', name: 'Edit Boundary', icon: '🟩', active: false },
  { id: 'delete', name: 'Delete', icon: '🗑️', active: false },
  { id: 'split', name: 'Split Plot', icon: '✂️', active: false },
  { id: 'merge', name: 'Merge Plots', icon: '➕', active: false },
  { id: 'color', name: 'Color Selector', icon: '🎨', active: false },
  { id: 'measure', name: 'Measure', icon: '📐', active: false },
];

const DesignToolbar: React.FC = () => {
  const {
    currentTool,
    setCurrentTool,
    snapToGrid,
    setSnapToGrid,
    gridSize,
    setGridSize,
    layers,
    toggleLayer,
    undo,
    redo,
    historyIndex,
    history,
  } = useDesignStore();

  const handleToolClick = (tool: DrawingTool) => {
    if (currentTool?.id === tool.id) {
      setCurrentTool(null);
    } else {
      setCurrentTool(tool);
    }
  };

  return (
    <div className="design-toolbar">
      {/* Drawing Tools */}
      <div className="toolbar-section">
        <h3 className="toolbar-title">Drawing Tools</h3>
        <div className="tool-grid">
          {tools.map((tool) => (
            <button
              key={tool.id}
              className={`tool-button ${currentTool?.id === tool.id ? 'active' : ''}`}
              onClick={() => handleToolClick(tool)}
              title={tool.name}
            >
              <span className="tool-icon">{tool.icon}</span>
              <span className="tool-name">{tool.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Snap to Grid */}
      <div className="toolbar-section">
        <h3 className="toolbar-title">Grid Settings</h3>
        <div className="setting-item">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={snapToGrid}
              onChange={(e) => setSnapToGrid(e.target.checked)}
            />
            <span>Snap to Grid</span>
          </label>
        </div>
        {snapToGrid && (
          <div className="setting-item">
            <label>Grid Size (m):</label>
            <select
              value={gridSize}
              onChange={(e) => setGridSize(Number(e.target.value))}
              className="input"
            >
              <option value={5}>5m</option>
              <option value={10}>10m</option>
              <option value={20}>20m</option>
              <option value={50}>50m</option>
            </select>
          </div>
        )}
      </div>

      {/* Layers */}
      <div className="toolbar-section">
        <h3 className="toolbar-title">Layers</h3>
        <div className="layer-list">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={layers.plots}
              onChange={() => toggleLayer('plots')}
            />
            <span>☑ Plots</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={layers.roads}
              onChange={() => toggleLayer('roads')}
            />
            <span>☑ Roads</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={layers.buildings}
              onChange={() => toggleLayer('buildings')}
            />
            <span>☑ Buildings</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={layers.utilities}
              onChange={() => toggleLayer('utilities')}
            />
            <span>☑ Utilities</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={layers.greenAreas}
              onChange={() => toggleLayer('greenAreas')}
            />
            <span>☑ Green Areas</span>
          </label>
        </div>
      </div>

      {/* History Controls */}
      <div className="toolbar-section">
        <h3 className="toolbar-title">History</h3>
        <div className="history-controls">
          <button
            className="btn btn-secondary"
            onClick={undo}
            disabled={historyIndex <= 0}
            title="Undo"
          >
            ↶ Undo
          </button>
          <button
            className="btn btn-secondary"
            onClick={redo}
            disabled={historyIndex >= history.length - 1}
            title="Redo"
          >
            ↷ Redo
          </button>
        </div>
      </div>
    </div>
  );
};

export default DesignToolbar;
