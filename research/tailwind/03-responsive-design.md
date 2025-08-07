# Tailwind CSS Responsive Design

## Key Responsive Design Concepts

### 1. Breakpoint System
- 5 default breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)
- Mobile-first approach: Unprefixed utilities apply universally, prefixed utilities apply at specific breakpoints and above

### 2. Responsive Utility Syntax
- Add breakpoint prefix before utility: `md:w-32` means width changes at medium breakpoint
- Example: `<img class="w-16 md:w-32 lg:w-48" src="..." />`

### 3. Responsive Strategies
- Target mobile layouts using unprefixed utilities
- Layer breakpoint-specific changes progressively
- Can target specific breakpoint ranges using `max-*` variants

### 4. Customization Options
- Modify breakpoints using CSS theme variables
- Remove default breakpoints
- Use arbitrary values for one-off responsive designs

### 5. Container Queries (Advanced Feature)
- Style elements based on parent container size
- Use `@container` class and variants like `@sm` and `@md`
- Support for named containers and custom container sizes

## Best Practice
Implement mobile layout first, then progressively enhance for larger screens.