# Tailwind CSS Dark Mode

## Key Dark Mode Features
- Supports automatic dark mode via system preferences
- Provides a `dark` variant for styling elements differently in dark mode
- Allows manual toggling of dark mode through CSS classes or data attributes

## Implementation Methods

### 1. Default System Preference Mode
- Uses CSS `prefers-color-scheme` media feature
- Automatically applies dark styles based on user's system settings

### 2. Manual Toggling Options
- Add `dark` class to HTML element
- Use data attribute like `data-theme="dark"`
- Implement custom JavaScript for theme switching

## Example Configuration
```css
@custom-variant dark (&:where(.dark, .dark *));
```

## Example HTML
```html
<html class="dark">
  <div class="bg-white dark:bg-gray-800">
    <!-- Content with light/dark variants -->
  </div>
</html>
```

## Theme Switching Strategy
- Store preference in `localStorage`
- Support light, dark, and system theme modes
- Use `window.matchMedia()` to detect system preference

## Best Practices
- Provide user control over theme selection
- Ensure smooth transition between themes
- Consider performance and user experience