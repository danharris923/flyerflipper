# Tailwind CSS Installation with Vite

## Installation Steps

### 1. Create a new Vite project
- Command: `npm create vite@latest my-project`
- Change into project directory: `cd my-project`

### 2. Install Tailwind CSS dependencies
- Command: `npm install tailwindcss @tailwindcss/vite`

### 3. Configure Vite plugin (in `vite.config.ts`)
```typescript
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [tailwindcss()],
})
```

### 4. Import Tailwind in CSS file
- Add: `@import "tailwindcss";`

### 5. Start development server
- Command: `npm run dev`

### 6. Use Tailwind classes in HTML
```html
<h1 class="text-3xl font-bold underline">Hello world!</h1>
```

## Key Highlights
- Zero-runtime CSS generation
- Scans HTML, JavaScript, and templates for class names
- Generates corresponding styles automatically
- Works with multiple frameworks (Laravel, SvelteKit, React Router, etc.)

**Recommendation**: Check framework-specific guides for more detailed setup instructions.