# useState Hook

## Key Characteristics
- Allows adding state variables to functional components
- Returns an array with two elements: current state and a setter function
- Can be used with various data types (numbers, strings, objects, arrays)

## Basic Usage
```javascript
const [state, setState] = useState(initialValue);
```

## Important Principles

### 1. State Updates
- State updates trigger re-renders
- State is immutable; always replace, never mutate
- Use functional updates for state dependent on previous state

### 2. Best Practices
- Name state variables using `[something, setSomething]` convention
- Use initializer functions to avoid recreating expensive initial states
- Prefer creating new objects/arrays instead of mutating existing ones

### 3. Common Patterns
- Updating based on previous state: `setState(prevState => newState)`
- Resetting state by changing component's `key`
- Storing information from previous renders

## Unique Behaviors
- In Strict Mode, initializer and updater functions may run twice
- State updates are batched for performance
- React skips re-rendering if new state is identical to current state

## Potential Pitfalls
- State updates don't immediately change values in current code execution
- Avoid setting state during rendering to prevent infinite loops
- Be cautious when storing functions as state