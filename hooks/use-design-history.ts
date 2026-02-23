import { useState, useCallback } from 'react';

/**
 * useDesignHistory Hook
 * 
 * Quản lý lịch sử thiết kế cho undo/redo functionality
 * Hỗ trợ branching history và time-travel debugging
 */

export interface HistoryAction {
  type: 'add' | 'update' | 'delete' | 'batch';
  timestamp: number;
  data: any;
  elementId?: string;
  description?: string;
}

export interface DesignHistoryState {
  history: HistoryAction[];
  currentIndex: number;
  maxHistory: number;
}

export function useDesignHistory(maxHistory: number = 50) {
  const [history, setHistory] = useState<HistoryAction[]>([]);
  const [currentIndex, setCurrentIndex] = useState(-1);

  /**
   * Thêm action mới vào history
   * Xóa tất cả redo history khi thêm action mới
   */
  const addToHistory = useCallback((action: Omit<HistoryAction, 'timestamp'>) => {
    setHistory(prev => {
      // Xóa các action sau currentIndex (redo stack)
      const newHistory = prev.slice(0, currentIndex + 1);
      
      // Thêm action mới
      const newAction: HistoryAction = {
        ...action,
        timestamp: Date.now()
      };
      
      newHistory.push(newAction);
      
      // Giới hạn số lượng history
      if (newHistory.length > maxHistory) {
        return newHistory.slice(newHistory.length - maxHistory);
      }
      
      return newHistory;
    });
    
    setCurrentIndex(prev => {
      const newIndex = prev + 1;
      return newIndex >= maxHistory ? maxHistory - 1 : newIndex;
    });
  }, [currentIndex, maxHistory]);

  /**
   * Undo action
   * Returns action data để apply vào state
   */
  const undo = useCallback((): HistoryAction | null => {
    if (currentIndex < 0) return null;
    
    const action = history[currentIndex];
    setCurrentIndex(prev => prev - 1);
    
    return action;
  }, [currentIndex, history]);

  /**
   * Redo action
   * Returns action data để apply vào state
   */
  const redo = useCallback((): HistoryAction | null => {
    if (currentIndex >= history.length - 1) return null;
    
    const action = history[currentIndex + 1];
    setCurrentIndex(prev => prev + 1);
    
    return action;
  }, [currentIndex, history]);

  /**
   * Check if can undo
   */
  const canUndo = currentIndex >= 0;

  /**
   * Check if can redo
   */
  const canRedo = currentIndex < history.length - 1;

  /**
   * Clear toàn bộ history
   */
  const clearHistory = useCallback(() => {
    setHistory([]);
    setCurrentIndex(-1);
  }, []);

  /**
   * Get current state description
   */
  const getCurrentDescription = useCallback((): string => {
    if (currentIndex < 0) return 'Initial state';
    return history[currentIndex].description || `Action ${currentIndex + 1}`;
  }, [currentIndex, history]);

  /**
   * Get history info for debugging
   */
  const getHistoryInfo = useCallback(() => {
    return {
      total: history.length,
      current: currentIndex,
      canUndo,
      canRedo,
      actions: history.map((action, idx) => ({
        index: idx,
        type: action.type,
        description: action.description,
        isCurrent: idx === currentIndex
      }))
    };
  }, [history, currentIndex, canUndo, canRedo]);

  return {
    addToHistory,
    undo,
    redo,
    canUndo,
    canRedo,
    clearHistory,
    getCurrentDescription,
    getHistoryInfo,
    historyLength: history.length,
    currentIndex
  };
}
