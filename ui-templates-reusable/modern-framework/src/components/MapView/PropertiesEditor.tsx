import React, { useState, useEffect } from 'react';
import { useDesignStore } from '../../store/designStore';
import './PropertiesEditor.css';

const PropertiesEditor: React.FC = () => {
  const { selectedElement, updateElement } = useDesignStore();
  const [localProperties, setLocalProperties] = useState<any>({});

  useEffect(() => {
    if (selectedElement) {
      setLocalProperties(selectedElement.properties);
    }
  }, [selectedElement]);

  if (!selectedElement) {
    return (
      <div className="properties-editor empty">
        <div className="empty-state">
          <span className="empty-icon">👈</span>
          <p className="empty-text">
            Select an element on the map to edit its properties
          </p>
        </div>
      </div>
    );
  }

  const handlePropertyChange = (key: string, value: any) => {
    setLocalProperties((prev: any) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleApply = () => {
    if (selectedElement) {
      updateElement(selectedElement.id, {
        properties: localProperties,
      });
    }
  };

  const renderRoadProperties = () => (
    <>
      <div className="property-field">
        <label>Road Name:</label>
        <input
          type="text"
          className="input"
          value={localProperties.name || ''}
          onChange={(e) => handlePropertyChange('name', e.target.value)}
          placeholder="Primary Road 1"
        />
      </div>
      <div className="property-field">
        <label>Width (m):</label>
        <input
          type="number"
          className="input"
          value={localProperties.width || 25}
          onChange={(e) => handlePropertyChange('width', Number(e.target.value))}
          min="5"
          max="50"
        />
      </div>
      <div className="property-field">
        <label>Type:</label>
        <select
          className="input"
          value={localProperties.type || 'primary'}
          onChange={(e) => handlePropertyChange('type', e.target.value)}
        >
          <option value="primary">Primary</option>
          <option value="secondary">Secondary</option>
          <option value="service">Service</option>
        </select>
      </div>
      <div className="property-field">
        <label>Color:</label>
        <input
          type="color"
          value={localProperties.color || '#ffffff'}
          onChange={(e) => handlePropertyChange('color', e.target.value)}
        />
      </div>
      <div className="property-field">
        <label>Surface:</label>
        <select
          className="input"
          value={localProperties.surface || 'asphalt'}
          onChange={(e) => handlePropertyChange('surface', e.target.value)}
        >
          <option value="asphalt">Asphalt</option>
          <option value="concrete">Concrete</option>
          <option value="gravel">Gravel</option>
        </select>
      </div>
      <div className="property-field">
        <label>Speed Limit (km/h):</label>
        <select
          className="input"
          value={localProperties.speedLimit || 60}
          onChange={(e) => handlePropertyChange('speedLimit', Number(e.target.value))}
        >
          <option value={30}>30</option>
          <option value={40}>40</option>
          <option value={60}>60</option>
          <option value={80}>80</option>
        </select>
      </div>
    </>
  );

  const renderBuildingProperties = () => (
    <>
      <div className="property-field">
        <label>Building Name:</label>
        <input
          type="text"
          className="input"
          value={localProperties.name || ''}
          onChange={(e) => handlePropertyChange('name', e.target.value)}
          placeholder="Factory Building 1"
        />
      </div>
      <div className="property-field">
        <label>Type:</label>
        <select
          className="input"
          value={localProperties.buildingType || 'factory'}
          onChange={(e) => handlePropertyChange('buildingType', e.target.value)}
        >
          <option value="factory">🏭 Factory</option>
          <option value="warehouse">🏗️ Warehouse</option>
          <option value="administration">🏛️ Administration</option>
          <option value="parking">🅿️ Parking Lot</option>
          <option value="greenhouse">🌳 Green House</option>
          <option value="water_treatment">💧 Water Treatment</option>
          <option value="power_station">⚡ Power Station</option>
          <option value="loading_bay">🚚 Loading Bay</option>
        </select>
      </div>
      <div className="property-field">
        <label>Area (m²):</label>
        <input
          type="number"
          className="input"
          value={localProperties.area || 0}
          onChange={(e) => handlePropertyChange('area', Number(e.target.value))}
          min="0"
        />
      </div>
      <div className="property-field">
        <label>Height (m):</label>
        <input
          type="number"
          className="input"
          value={localProperties.height || 5}
          onChange={(e) => handlePropertyChange('height', Number(e.target.value))}
          min="1"
          max="50"
        />
      </div>
      <div className="property-field">
        <label>Rotation (°):</label>
        <input
          type="number"
          className="input"
          value={localProperties.rotation || 0}
          onChange={(e) => handlePropertyChange('rotation', Number(e.target.value))}
          min="0"
          max="360"
        />
      </div>
    </>
  );

  const renderPlotProperties = () => (
    <>
      <div className="property-field">
        <label>Plot Name:</label>
        <input
          type="text"
          className="input"
          value={localProperties.name || ''}
          onChange={(e) => handlePropertyChange('name', e.target.value)}
          placeholder="Plot A-01"
        />
      </div>
      <div className="property-field">
        <label>Area (m²):</label>
        <input
          type="number"
          className="input"
          value={localProperties.area || 0}
          readOnly
        />
      </div>
      <div className="property-field">
        <label>Status:</label>
        <select
          className="input"
          value={localProperties.status || 'available'}
          onChange={(e) => handlePropertyChange('status', e.target.value)}
        >
          <option value="available">Available</option>
          <option value="reserved">Reserved</option>
          <option value="sold">Sold</option>
          <option value="pending">Pending</option>
        </select>
      </div>
      <div className="property-field">
        <label>Price (VND/m²):</label>
        <input
          type="number"
          className="input"
          value={localProperties.pricePerSqm || 0}
          onChange={(e) => handlePropertyChange('pricePerSqm', Number(e.target.value))}
          min="0"
        />
      </div>
    </>
  );

  return (
    <div className="properties-editor">
      <h3 className="toolbar-title">
        {selectedElement.type === 'road' && '✏️ Road Properties'}
        {selectedElement.type === 'building' && '🏢 Building Properties'}
        {selectedElement.type === 'plot' && '🟩 Plot Properties'}
      </h3>

      <div className="property-form">
        {selectedElement.type === 'road' && renderRoadProperties()}
        {selectedElement.type === 'building' && renderBuildingProperties()}
        {selectedElement.type === 'plot' && renderPlotProperties()}

        <div className="ai-suggestion">
          <p className="suggestion-label">🤖 AI Suggestion:</p>
          <p className="suggestion-text">
            This {selectedElement.type} design looks good. Consider adjusting
            the spacing for better layout optimization.
          </p>
        </div>

        <div className="property-actions">
          <button className="btn btn-primary" onClick={handleApply}>
            Apply Changes
          </button>
          <button className="btn btn-secondary" onClick={() => window.alert('Get AI help...')}>
            Get AI Help
          </button>
        </div>
      </div>
    </div>
  );
};

export default PropertiesEditor;
