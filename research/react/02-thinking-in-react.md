# Thinking in React

## React Component Design Process

### 1. Break UI into Component Hierarchy
- Identify components based on design and data structure
- Create a component tree with parent-child relationships
- Follow single responsibility principle

### 2. Build Static Version
- Create components that render data without interactivity
- Use props to pass data between components
- Can build top-down or bottom-up

### 3. Identify Minimal State
- Determine what data actually needs to be dynamic
- Follow DRY (Don't Repeat Yourself) principle
- Only track state that changes and can't be computed

### 4. Determine State Location
- Find the closest common parent component for state
- "Often, you can put the state directly into their common parent"
- Ensure state is in a logical, accessible location

### 5. Add Inverse Data Flow
- Create event handlers to update state
- Pass state update functions down to child components
- Enable two-way interaction between components

## Key Principles
- One-way data flow from parent to child
- Minimal, computed state
- Components with clear, single responsibilities

The process emphasizes thoughtful component design and data management in React applications.