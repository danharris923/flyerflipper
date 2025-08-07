# React Hooks Overview

React Hooks allow developers to use React features directly in components. They can be built-in or custom-created.

## Key Hook Categories

### 1. State Hooks
- Enable components to "remember" information
- Primary hooks: `useState` and `useReducer`
- Example: `const [index, setIndex] = useState(0)`

### 2. Context Hooks
- Allow receiving information from distant parent components
- Primary hook: `useContext`
- Enables passing data like UI themes without prop drilling

### 3. Ref Hooks
- Store information not used for rendering
- Primary hooks: `useRef` and `useImperativeHandle`
- Useful for interacting with non-React systems

### 4. Effect Hooks
- Connect components to external systems
- Primary hook: `useEffect`
- Handles side effects like network connections
- Variations: `useLayoutEffect`, `useInsertionEffect`

### 5. Performance Hooks
- Optimize re-rendering and calculation
- Hooks: `useMemo`, `useCallback`, `useTransition`, `useDeferredValue`
- Help manage rendering priorities and cache calculations

### 6. Other Hooks
- Mostly for library authors
- Include `useDebugValue`, `useId`, `useSyncExternalStore`

## Best Practices
- Use hooks to extract and reuse component logic
- Avoid overusing effects for data flow
- Create custom hooks as modular, reusable functions