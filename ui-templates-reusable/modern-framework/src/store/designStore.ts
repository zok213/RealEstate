import { create } from 'zustand';
import { DesignState, DesignElement, DrawingTool } from '../types';

interface DesignStore extends DesignState {
  // Actions
  setCurrentTool: (tool: DrawingTool | null) => void;
  selectElement: (element: DesignElement | null) => void;
  addElement: (element: DesignElement) => void;
  updateElement: (id: string, updates: Partial<DesignElement>) => void;
  deleteElement: (id: string) => void;
  toggleLayer: (layer: keyof DesignState['layers']) => void;
  setSnapToGrid: (enabled: boolean) => void;
  setGridSize: (size: number) => void;
  undo: () => void;
  redo: () => void;
  saveHistory: () => void;
  clearHistory: () => void;
}

export const useDesignStore = create<DesignStore>((set, get) => ({
  // Initial state
  currentTool: null,
  selectedElement: null,
  elements: [],
  layers: {
    plots: true,
    roads: true,
    buildings: true,
    utilities: true,
    greenAreas: true,
  },
  snapToGrid: false,
  gridSize: 20,
  history: [[]],
  historyIndex: 0,

  // Actions
  setCurrentTool: (tool) => {
    set({ currentTool: tool, selectedElement: null });
  },

  selectElement: (element) => {
    set({ selectedElement: element });
  },

  addElement: (element) => {
    set((state) => ({
      elements: [...state.elements, element],
    }));
    get().saveHistory();
  },

  updateElement: (id, updates) => {
    set((state) => ({
      elements: state.elements.map((el) =>
        el.id === id ? { ...el, ...updates } : el
      ),
    }));
    get().saveHistory();
  },

  deleteElement: (id) => {
    set((state) => ({
      elements: state.elements.filter((el) => el.id !== id),
      selectedElement: state.selectedElement?.id === id ? null : state.selectedElement,
    }));
    get().saveHistory();
  },

  toggleLayer: (layer) => {
    set((state) => ({
      layers: {
        ...state.layers,
        [layer]: !state.layers[layer],
      },
    }));
  },

  setSnapToGrid: (enabled) => {
    set({ snapToGrid: enabled });
  },

  setGridSize: (size) => {
    set({ gridSize: size });
  },

  saveHistory: () => {
    const state = get();
    const newHistory = state.history.slice(0, state.historyIndex + 1);
    newHistory.push([...state.elements]);
    set({
      history: newHistory,
      historyIndex: newHistory.length - 1,
    });
  },

  undo: () => {
    const state = get();
    if (state.historyIndex > 0) {
      const newIndex = state.historyIndex - 1;
      set({
        elements: [...state.history[newIndex]],
        historyIndex: newIndex,
      });
    }
  },

  redo: () => {
    const state = get();
    if (state.historyIndex < state.history.length - 1) {
      const newIndex = state.historyIndex + 1;
      set({
        elements: [...state.history[newIndex]],
        historyIndex: newIndex,
      });
    }
  },

  clearHistory: () => {
    set({
      history: [[]],
      historyIndex: 0,
      elements: [],
    });
  },
}));
