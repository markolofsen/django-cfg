# Knowledge Chat Widget

RAG-powered chat widget with beautiful animations powered by `tailwindcss-animate`.

## Features

- 🎨 **Beautiful Animations**: Smooth transitions and micro-interactions
- 💬 **Real-time Chat**: RAG-powered responses with sources
- 📱 **Responsive**: Works on desktop and mobile
- 🗂️ **Session Management**: Create and manage chat sessions
- 🎯 **Context-aware**: Uses SWR hooks for data management

## Animations

### Widget Animations
- **Entry**: Fade in + slide from bottom with scale
- **Exit**: Fade out + slide to bottom with scale reduction
- **FAB Button**: Fade in + slide from bottom, hover scale, active scale

### Message Animations
- **Message Entry**: Staggered fade in + slide from bottom (50ms delay between messages)
- **Message Bubble**: Hover shadow effect with smooth transition
- **Loading State**: Pulsing avatar with bouncing bot icon

### Sources Animations
- **Container**: Fade in + slide from left with 100ms delay
- **Individual Badges**: Staggered zoom in (100ms per badge)
- **Badge Hover**: Scale up + active scale down

### Session List Animations
- **Session Items**: Staggered fade in + slide from left (50ms delay)
- **Hover State**: Border color + shadow transition
- **Action Buttons**: 
  - Slide in from right on hover
  - Scale up on hover, scale down on active

### Input Animations
- **Textarea**: Focus ring animation
- **Send Button**: Scale up on hover, scale down on active
- **Send Icon**: Smooth transitions

## Usage

```tsx
import { KnowledgeChat } from '@djangocfg/layouts/snippets';

// Simple usage
<KnowledgeChat />

// With props
<KnowledgeChat
  autoOpen={false}
  persistent={true}
  onToggle={(isOpen) => console.log('Chat toggled:', isOpen)}
  onMessage={(message) => console.log('Message sent:', message)}
/>
```

## Components

### KnowledgeChat
Main component with all providers integrated.

### ChatWidget
Core chat interface (use with providers manually if needed).

### ChatUIProvider
Manages UI state (open/closed, expanded, sources visibility).

### MessageList
Displays chat messages with sources and animations.

### MessageInput
Input field with auto-resize and keyboard shortcuts.

### SessionList
Drawer with chat sessions list.

## Animation Timing

- **Fast**: 200ms (buttons, badges)
- **Normal**: 300ms (widget, messages, drawer)
- **Stagger Delay**: 50-100ms (lists)

## Tailwind Classes Used

### tailwindcss-animate
- `animate-in`
- `fade-in`
- `slide-in-from-bottom-{n}`
- `slide-in-from-left-{n}`
- `zoom-in-95`
- `duration-{n}`
- `delay-{n}`

### Tailwind Core
- `transition-all`
- `transition-transform`
- `transition-colors`
- `duration-{n}`
- `ease-out`
- `animate-spin`
- `animate-pulse`
- `animate-bounce`
- `hover:scale-{n}`
- `active:scale-{n}`

## Performance

All animations use CSS transforms and opacity for optimal performance:
- Hardware-accelerated transforms (translate, scale)
- Efficient opacity transitions
- No layout thrashing
- Minimal reflows

## Accessibility

- Respects `prefers-reduced-motion`
- Keyboard navigation support
- ARIA labels
- Screen reader friendly

