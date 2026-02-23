"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Droplet, 
  Building2, 
  Road, 
  Trees,
  Info
} from 'lucide-react';

interface Feature {
  id: string;
  type: 'water' | 'building' | 'road' | 'vegetation' | 'obstacle';
  area?: number; // m²
  length?: number; // m (for roads)
  isRectangular?: boolean; // for buildings
  significant?: boolean; // for vegetation
  properties: Record<string, any>;
}

interface ReusabilityClassification {
  keep_as_is: string[];
  reuse_modified: string[];
  demolish: string[];
  constraints: any[];
}

interface ReusableFeatureManagerProps {
  fileId: string;
  features: {
    water_bodies: any[];
    buildings: any[];
    roads: any[];
    vegetation: any[];
    obstacles: any[];
  };
  reusability: ReusabilityClassification;
  onUpdate?: (overrides: Record<string, string>) => void;
  onFeatureHover?: (featureId: string | null) => void;
}

export default function ReusableFeaturesManager({
  fileId,
  features,
  reusability,
  onUpdate,
  onFeatureHover
}: ReusableFeatureManagerProps) {
  const [localClassification, setLocalClassification] = useState<Record<string, string>>({});
  const [hasChanges, setHasChanges] = useState(false);

  // Initialize local classification from backend
  useEffect(() => {
    const initial: Record<string, string> = {};
    
    reusability.keep_as_is.forEach(id => {
      initial[id] = 'keep';
    });
    
    reusability.reuse_modified.forEach(id => {
      initial[id] = 'reuse';
    });
    
    reusability.demolish.forEach(id => {
      initial[id] = 'demolish';
    });
    
    setLocalClassification(initial);
    setHasChanges(false);
  }, [reusability]);

  // Convert all features to unified format
  const allFeatures: Feature[] = [
    ...features.water_bodies.map(wb => ({
      id: wb.id,
      type: 'water' as const,
      area: wb.area_m2,
      properties: wb
    })),
    ...features.buildings.map(b => ({
      id: b.id,
      type: 'building' as const,
      area: b.area_m2,
      isRectangular: b.is_rectangular,
      properties: b
    })),
    ...features.roads.map(r => ({
      id: r.id,
      type: 'road' as const,
      length: r.length_m,
      properties: r
    })),
    ...features.vegetation.map(v => ({
      id: v.id,
      type: 'vegetation' as const,
      area: v.polygon ? Math.PI * Math.pow(v.radius_m, 2) : 0,
      significant: v.significant,
      properties: v
    }))
  ];

  // Update classification
  const updateClassification = (featureId: string, classification: string) => {
    setLocalClassification(prev => ({
      ...prev,
      [featureId]: classification
    }));
    setHasChanges(true);
  };

  // Save changes to backend
  const saveChanges = async () => {
    try {
      const response = await fetch('/api/dxf/reusability-override', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_id: fileId,
          overrides: localClassification
        })
      });

      if (response.ok) {
        setHasChanges(false);
        if (onUpdate) {
          onUpdate(localClassification);
        }
      }
    } catch (error) {
      console.error('Failed to save changes:', error);
      alert('Failed to save changes');
    }
  };

  // Reset to backend classification
  const resetChanges = () => {
    const initial: Record<string, string> = {};
    
    reusability.keep_as_is.forEach(id => {
      initial[id] = 'keep';
    });
    
    reusability.reuse_modified.forEach(id => {
      initial[id] = 'reuse';
    });
    
    reusability.demolish.forEach(id => {
      initial[id] = 'demolish';
    });
    
    setLocalClassification(initial);
    setHasChanges(false);
  };

  // Get feature icon
  const getFeatureIcon = (type: string) => {
    switch (type) {
      case 'water':
        return <Droplet className="h-4 w-4 text-blue-500" />;
      case 'building':
        return <Building2 className="h-4 w-4 text-gray-500" />;
      case 'road':
        return <Road className="h-4 w-4 text-yellow-500" />;
      case 'vegetation':
        return <Trees className="h-4 w-4 text-green-500" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  // Get classification icon
  const getClassificationIcon = (classification: string) => {
    switch (classification) {
      case 'keep':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'reuse':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      case 'demolish':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  // Estimate cost
  const estimateCost = (feature: Feature, classification: string): number => {
    // Cost estimates in THB
    const costs = {
      water: {
        keep: 0,
        reuse: 50000, // Minor modifications
        demolish: (feature.area || 0) * 100 // 100 THB/m² to fill
      },
      building: {
        keep: 0,
        reuse: (feature.area || 0) * 3000, // 3,000 THB/m² renovation
        demolish: (feature.area || 0) * 1500 // 1,500 THB/m² demolition
      },
      road: {
        keep: 0,
        reuse: (feature.length || 0) * 2000, // 2,000 THB/m upgrade
        demolish: (feature.length || 0) * 1000 // 1,000 THB/m removal + new
      },
      vegetation: {
        keep: 0,
        reuse: 50000, // Transplanting
        demolish: feature.significant ? 100000 : 10000 // Protected trees expensive
      }
    };

    return costs[feature.type]?.[classification as keyof typeof costs[typeof feature.type]] || 0;
  };

  // Format currency
  const formatCurrency = (amount: number): string => {
    if (amount === 0) return '฿0';
    if (amount >= 1000000) return `฿${(amount / 1000000).toFixed(1)}M`;
    if (amount >= 1000) return `฿${(amount / 1000).toFixed(0)}K`;
    return `฿${amount.toFixed(0)}`;
  };

  // Calculate total cost
  const totalCost = allFeatures.reduce((sum, feature) => {
    const classification = localClassification[feature.id] || 'demolish';
    return sum + estimateCost(feature, classification);
  }, 0);

  // Group features by type
  const groupedFeatures = {
    water: allFeatures.filter(f => f.type === 'water'),
    building: allFeatures.filter(f => f.type === 'building'),
    road: allFeatures.filter(f => f.type === 'road'),
    vegetation: allFeatures.filter(f => f.type === 'vegetation')
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Reusable Features Manager</span>
          <div className="flex items-center gap-2">
            {hasChanges && (
              <>
                <Button variant="outline" size="sm" onClick={resetChanges}>
                  Reset
                </Button>
                <Button size="sm" onClick={saveChanges}>
                  Save Changes
                </Button>
              </>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Summary */}
        <div className="mb-4 p-4 bg-muted rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium">Estimated Total Cost:</span>
            <Badge variant="default" className="text-base">
              {formatCurrency(totalCost)}
            </Badge>
          </div>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="flex items-center gap-1">
              <CheckCircle2 className="h-3 w-3 text-green-500" />
              <span>Keep: {Object.values(localClassification).filter(c => c === 'keep').length}</span>
            </div>
            <div className="flex items-center gap-1">
              <AlertTriangle className="h-3 w-3 text-orange-500" />
              <span>Reuse: {Object.values(localClassification).filter(c => c === 'reuse').length}</span>
            </div>
            <div className="flex items-center gap-1">
              <XCircle className="h-3 w-3 text-red-500" />
              <span>Demolish: {Object.values(localClassification).filter(c => c === 'demolish').length}</span>
            </div>
          </div>
        </div>

        {/* Feature Lists */}
        <ScrollArea className="h-[500px]">
          {Object.entries(groupedFeatures).map(([type, typeFeatures]) => {
            if (typeFeatures.length === 0) return null;

            return (
              <div key={type} className="mb-6">
                <h3 className="font-medium mb-3 capitalize flex items-center gap-2">
                  {getFeatureIcon(type)}
                  {type}s ({typeFeatures.length})
                </h3>
                <div className="space-y-2">
                  {typeFeatures.map(feature => {
                    const classification = localClassification[feature.id] || 'demolish';
                    const cost = estimateCost(feature, classification);

                    return (
                      <div
                        key={feature.id}
                        className="p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                        onMouseEnter={() => onFeatureHover && onFeatureHover(feature.id)}
                        onMouseLeave={() => onFeatureHover && onFeatureHover(null)}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              {getFeatureIcon(type)}
                              <span className="text-sm font-medium">
                                {feature.id.substring(0, 8)}...
                              </span>
                            </div>
                            <div className="text-xs text-muted-foreground space-y-1">
                              {feature.area && (
                                <div>Area: {(feature.area / 1600).toFixed(2)} rai ({feature.area.toFixed(0)} m²)</div>
                              )}
                              {feature.length && (
                                <div>Length: {feature.length.toFixed(0)} m</div>
                              )}
                              {feature.type === 'building' && (
                                <div>Shape: {feature.isRectangular ? 'Rectangular' : 'Irregular'}</div>
                              )}
                              {feature.type === 'vegetation' && feature.significant && (
                                <Badge variant="outline" className="text-xs">Significant Tree</Badge>
                              )}
                            </div>
                          </div>
                          <Badge variant={cost === 0 ? 'default' : 'outline'}>
                            {formatCurrency(cost)}
                          </Badge>
                        </div>

                        {/* Classification Options */}
                        <div className="flex gap-2">
                          <Button
                            variant={classification === 'keep' ? 'default' : 'outline'}
                            size="sm"
                            className="flex-1"
                            onClick={() => updateClassification(feature.id, 'keep')}
                          >
                            <CheckCircle2 className="h-3 w-3 mr-1" />
                            Keep
                          </Button>
                          <Button
                            variant={classification === 'reuse' ? 'default' : 'outline'}
                            size="sm"
                            className="flex-1"
                            onClick={() => updateClassification(feature.id, 'reuse')}
                          >
                            <AlertTriangle className="h-3 w-3 mr-1" />
                            Reuse
                          </Button>
                          <Button
                            variant={classification === 'demolish' ? 'default' : 'outline'}
                            size="sm"
                            className="flex-1"
                            onClick={() => updateClassification(feature.id, 'demolish')}
                          >
                            <XCircle className="h-3 w-3 mr-1" />
                            Demolish
                          </Button>
                        </div>

                        {/* Cost Breakdown */}
                        <div className="mt-2 text-xs text-muted-foreground">
                          {classification === 'keep' && '✓ No cost - preserving existing'}
                          {classification === 'reuse' && `⚠️ Modification cost: ${formatCurrency(cost)}`}
                          {classification === 'demolish' && `✗ Removal + rebuild: ${formatCurrency(cost)}`}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
