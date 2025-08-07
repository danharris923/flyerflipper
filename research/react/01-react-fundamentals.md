# React Fundamentals

## Key React Concepts

### 1. Components
- React applications are built using components
- Components are JavaScript functions that return markup
- Component names must start with a capital letter
- Components can be nested within each other

### 2. JSX
- Markup syntax that allows embedding JavaScript in HTML-like structures
- Requires closed tags (e.g., `<br />`)
- Uses curly braces `{}` to embed JavaScript expressions
- Supports conditional rendering and list rendering

### 3. State Management
- Uses `useState` hook to create state variables
- State allows components to "remember" and update information
- State can be "lifted up" to parent components to share data between child components
- Each component can have its own independent state

### 4. Event Handling
- Components can define event handler functions
- Events are attached using camelCase (e.g., `onClick`)
- Event handlers are passed as references, not called directly

### 5. Styling
- Uses `className` instead of `class` for CSS classes
- Supports inline styles using JavaScript objects
- Flexible approach to adding CSS to components

## Core Principles
- Components are reusable UI building blocks
- State drives UI updates
- Data flows from parent to child components via props
- Hooks provide powerful state and lifecycle management

## Recommended Learning Path
- Start with basic component creation
- Learn state management
- Practice event handling
- Explore more advanced component patterns