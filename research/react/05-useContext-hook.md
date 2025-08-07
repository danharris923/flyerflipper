# useContext Hook

## Key Characteristics
- A React Hook for reading and subscribing to context
- Allows passing data deeply through component trees without prop drilling
- Automatically re-renders components when context values change

## Basic Usage
```javascript
const value = useContext(SomeContext)
```

## Core Principles

### 1. Context Providers
- Wrap components to distribute shared values
- Can be nested and overridden
- Pass values using the `value` prop

### 2. Context Consumption
- Components can access context values using `useContext()`
- Searches upward in component tree for nearest provider
- Uses default value if no provider found

## Best Practices
- Use `useState` to make context values dynamic
- Optimize re-renders with `useMemo` and `useCallback`
- Specify meaningful default values
- Ensure context objects are exactly the same between provider and consumer

## Common Pitfalls
- Providers must be above components consuming context
- Forgetting to specify `value` prop
- Build tool issues causing context object mismatches

## Performance Optimization Example
```javascript
const contextValue = useMemo(() => ({
  currentUser,
  login
}), [currentUser, login]);
```

This approach prevents unnecessary re-renders by memoizing context values.