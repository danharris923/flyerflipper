# useEffect Hook

## Key Characteristics
- A React Hook for synchronizing components with external systems
- Runs after component render
- Can perform side effects like data fetching, subscriptions, or manual DOM manipulations

## Basic Syntax
```javascript
useEffect(setup, dependencies?)
```

## Core Responsibilities
1. Connect to external systems
2. Manage side effects
3. Handle component lifecycle interactions

## Critical Best Practices
- Always specify dependencies
- Implement cleanup functions
- Avoid unnecessary re-renders
- Move non-reactive logic outside the effect

## Common Use Cases
- Fetching data
- Setting up subscriptions
- Controlling non-React widgets
- Synchronizing with browser APIs

## Important Patterns
- Use dependency array to control effect execution
- Return a cleanup function to prevent memory leaks
- Separate reactive from non-reactive code
- Minimize effect complexity

## Key Troubleshooting Tips
- Effects running twice in development is normal (Strict Mode)
- Prevent infinite re-render loops
- Use `useLayoutEffect` for visual changes before browser paint
- Consider custom hooks for complex effect logic

## Recommended Approach
"Effects are an 'escape hatch' when you need to step outside React" and should be used judiciously.