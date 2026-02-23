import { renderHook, act } from '@testing-library/react';
import { useDesignHistory } from '@/hooks/use-design-history';

/**
 * Integration Tests for Enhanced UI Components
 */

describe('useDesignHistory Hook', () => {
  it('should initialize with empty history', () => {
    const { result } = renderHook(() => useDesignHistory());
    
    expect(result.current.canUndo).toBe(false);
    expect(result.current.canRedo).toBe(false);
    expect(result.current.historyLength).toBe(0);
    expect(result.current.currentIndex).toBe(-1);
  });

  it('should add actions to history', () => {
    const { result } = renderHook(() => useDesignHistory());
    
    act(() => {
      result.current.addToHistory({
        type: 'add',
        data: { id: '1', type: 'road' },
        description: 'Add road'
      });
    });
    
    expect(result.current.historyLength).toBe(1);
    expect(result.current.canUndo).toBe(true);
    expect(result.current.canRedo).toBe(false);
  });

  it('should undo action', () => {
    const { result } = renderHook(() => useDesignHistory());
    
    act(() => {
      result.current.addToHistory({
        type: 'add',
        data: { id: '1', type: 'road' },
        description: 'Add road'
      });
    });
    
    let undoneAction;
    act(() => {
      undoneAction = result.current.undo();
    });
    
    expect(undoneAction).toBeTruthy();
    expect(result.current.canUndo).toBe(false);
    expect(result.current.canRedo).toBe(true);
  });

  it('should redo action', () => {
    const { result } = renderHook(() => useDesignHistory());
    
    act(() => {
      result.current.addToHistory({
        type: 'add',
        data: { id: '1', type: 'road' },
        description: 'Add road'
      });
      result.current.undo();
    });
    
    let redoneAction;
    act(() => {
      redoneAction = result.current.redo();
    });
    
    expect(redoneAction).toBeTruthy();
    expect(result.current.canUndo).toBe(true);
    expect(result.current.canRedo).toBe(false);
  });

  it('should clear redo history when adding new action', () => {
    const { result } = renderHook(() => useDesignHistory());
    
    act(() => {
      result.current.addToHistory({
        type: 'add',
        data: { id: '1', type: 'road' },
        description: 'Add road'
      });
      result.current.addToHistory({
        type: 'add',
        data: { id: '2', type: 'building' },
        description: 'Add building'
      });
      result.current.undo(); // Undo building
    });
    
    expect(result.current.canRedo).toBe(true);
    
    act(() => {
      result.current.addToHistory({
        type: 'add',
        data: { id: '3', type: 'parking' },
        description: 'Add parking'
      });
    });
    
    expect(result.current.canRedo).toBe(false);
    expect(result.current.historyLength).toBe(3);
  });

  it('should respect maxHistory limit', () => {
    const { result } = renderHook(() => useDesignHistory(3));
    
    act(() => {
      result.current.addToHistory({ type: 'add', data: { id: '1' } });
      result.current.addToHistory({ type: 'add', data: { id: '2' } });
      result.current.addToHistory({ type: 'add', data: { id: '3' } });
      result.current.addToHistory({ type: 'add', data: { id: '4' } });
    });
    
    expect(result.current.historyLength).toBe(3);
  });

  it('should provide history info', () => {
    const { result } = renderHook(() => useDesignHistory());
    
    act(() => {
      result.current.addToHistory({
        type: 'add',
        data: { id: '1' },
        description: 'First action'
      });
      result.current.addToHistory({
        type: 'update',
        data: { id: '1' },
        description: 'Second action'
      });
    });
    
    const info = result.current.getHistoryInfo();
    
    expect(info.total).toBe(2);
    expect(info.current).toBe(1);
    expect(info.canUndo).toBe(true);
    expect(info.canRedo).toBe(false);
    expect(info.actions).toHaveLength(2);
    expect(info.actions[1].isCurrent).toBe(true);
  });

  it('should clear history', () => {
    const { result } = renderHook(() => useDesignHistory());
    
    act(() => {
      result.current.addToHistory({ type: 'add', data: { id: '1' } });
      result.current.addToHistory({ type: 'add', data: { id: '2' } });
    });
    
    expect(result.current.historyLength).toBe(2);
    
    act(() => {
      result.current.clearHistory();
    });
    
    expect(result.current.historyLength).toBe(0);
    expect(result.current.canUndo).toBe(false);
    expect(result.current.canRedo).toBe(false);
  });

  it('should get current description', () => {
    const { result } = renderHook(() => useDesignHistory());
    
    expect(result.current.getCurrentDescription()).toBe('Initial state');
    
    act(() => {
      result.current.addToHistory({
        type: 'add',
        data: { id: '1' },
        description: 'Custom description'
      });
    });
    
    expect(result.current.getCurrentDescription()).toBe('Custom description');
  });
});

describe('Enhanced UI Component Integration', () => {
  it('should handle complete workflow', () => {
    const { result } = renderHook(() => useDesignHistory());
    
    // Simulate adding multiple elements
    act(() => {
      result.current.addToHistory({
        type: 'add',
        elementId: 'road-1',
        data: { type: 'road', width: 25 },
        description: 'Add main road'
      });
      
      result.current.addToHistory({
        type: 'add',
        elementId: 'building-1',
        data: { type: 'building', area: 1000 },
        description: 'Add building'
      });
      
      result.current.addToHistory({
        type: 'update',
        elementId: 'road-1',
        data: { old: { width: 25 }, new: { width: 30 } },
        description: 'Update road width'
      });
    });
    
    expect(result.current.historyLength).toBe(3);
    expect(result.current.canUndo).toBe(true);
    
    // Undo last action
    let action;
    act(() => {
      action = result.current.undo();
    });
    
    expect(action?.type).toBe('update');
    expect(result.current.canRedo).toBe(true);
    
    // Redo
    act(() => {
      action = result.current.redo();
    });
    
    expect(action?.type).toBe('update');
    
    // Get complete history info
    const info = result.current.getHistoryInfo();
    expect(info.actions).toHaveLength(3);
    expect(info.actions.map(a => a.type)).toEqual(['add', 'add', 'update']);
  });
});
