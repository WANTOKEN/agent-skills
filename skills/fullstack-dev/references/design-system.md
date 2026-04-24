# UI/UX Design System

## Design Principles

### 1. Visual Hierarchy
- Use size, color, and spacing to guide attention
- Primary actions should be visually prominent
- Secondary actions should be subtle but accessible
- Create clear focal points on each screen

### 2. Consistency
- Reuse components across the application
- Maintain consistent spacing and sizing
- Use the same interaction patterns
- Follow established conventions

### 3. Feedback
- Immediate visual feedback for interactions
- Clear loading states
- Meaningful error messages
- Success confirmations

### 4. Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- Sufficient color contrast

---

## Color System

### Semantic Colors

```css
:root {
  /* Base colors */
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  
  /* Primary - for main actions */
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  
  /* Secondary - for less prominent elements */
  --secondary: 210 40% 96.1%;
  --secondary-foreground: 222.2 47.4% 11.2%;
  
  /* Accent - for highlights */
  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;
  
  /* Destructive - for dangerous actions */
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;
  
  /* Semantic states */
  --success: 142 76% 36%;
  --warning: 38 92% 50%;
  --error: 0 84% 60%;
  --info: 199 89% 48%;
  
  /* Borders and inputs */
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;
}
```

### Dark Mode

```css
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --primary: 210 40% 98%;
  --primary-foreground: 222.2 47.4% 11.2%;
  /* ... invert other colors */
}
```

### Color Usage Guidelines

| Color | Usage |
|-------|-------|
| Primary | Main CTAs, active states, key information |
| Secondary | Supporting elements, cards, backgrounds |
| Accent | Highlights, hover states, emphasis |
| Destructive | Delete actions, errors, warnings |
| Success | Confirmations, positive states |
| Warning | Caution states, important notices |

---

## Typography

### Font Stack

```css
/* System font stack for performance */
--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
  "Helvetica Neue", Arial, sans-serif;

/* Monospace for code */
--font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas,
  "Liberation Mono", monospace;
```

### Type Scale

```css
/* Using Tailwind's default scale */
.text-xs    { font-size: 0.75rem; line-height: 1rem; }    /* 12px */
.text-sm    { font-size: 0.875rem; line-height: 1.25rem; } /* 14px */
.text-base  { font-size: 1rem; line-height: 1.5rem; }     /* 16px */
.text-lg    { font-size: 1.125rem; line-height: 1.75rem; } /* 18px */
.text-xl    { font-size: 1.25rem; line-height: 1.75rem; }  /* 20px */
.text-2xl   { font-size: 1.5rem; line-height: 2rem; }      /* 24px */
.text-3xl   { font-size: 1.875rem; line-height: 2.25rem; } /* 30px */
.text-4xl   { font-size: 2.25rem; line-height: 2.5rem; }   /* 36px */
```

### Typography Guidelines

- **Headings**: Bold weight, tight line-height
- **Body**: Regular weight, comfortable line-height (1.5-1.7)
- **Small text**: Use sparingly, ensure sufficient contrast
- **Links**: Underline on hover, consistent color

---

## Spacing System

### Base Unit: 4px

```css
/* Tailwind spacing scale */
space-0: 0;      /* 0px */
space-1: 0.25rem; /* 4px */
space-2: 0.5rem;  /* 8px */
space-3: 0.75rem; /* 12px */
space-4: 1rem;    /* 16px */
space-5: 1.25rem; /* 20px */
space-6: 1.5rem;  /* 24px */
space-8: 2rem;    /* 32px */
space-10: 2.5rem; /* 40px */
space-12: 3rem;   /* 48px */
space-16: 4rem;   /* 64px */
```

### Spacing Guidelines

- Use consistent padding inside components
- Use consistent gaps between elements
- Increase spacing for visual separation
- Reduce spacing for related items

---

## Component Patterns

### Buttons

```tsx
// Variants
<Button variant="default">Primary Action</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="destructive">Delete</Button>
<Button variant="link">Link Style</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>
<Button size="icon"><Icon /></Button>

// States
<Button disabled>Disabled</Button>
<Button loading>Loading...</Button>
```

### Inputs

```tsx
// Text input
<Input 
  type="text"
  placeholder="Enter value"
  error="This field is required"
/>

// With label
<Label htmlFor="email">Email</Label>
<Input id="email" type="email" />

// Select
<Select>
  <SelectTrigger>
    <SelectValue placeholder="Select option" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="1">Option 1</SelectItem>
    <SelectItem value="2">Option 2</SelectItem>
  </SelectContent>
</Select>
```

### Cards

```tsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description text</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

### Modals/Dialogs

```tsx
<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Confirm Action</DialogTitle>
      <DialogDescription>
        Are you sure you want to proceed?
      </DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <Button variant="outline">Cancel</Button>
      <Button>Confirm</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Tables

```tsx
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
      <TableHead>Status</TableHead>
      <TableHead className="text-right">Actions</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {items.map((item) => (
      <TableRow key={item.id}>
        <TableCell>{item.name}</TableCell>
        <TableCell><Badge>{item.status}</Badge></TableCell>
        <TableCell className="text-right">
          <Button size="icon" variant="ghost">
            <MoreHorizontal />
          </Button>
        </TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

---

## Animation Guidelines

### Timing

```css
/* Fast - micro-interactions */
--duration-fast: 150ms;

/* Normal - most transitions */
--duration-normal: 200ms;

/* Slow - complex animations */
--duration-slow: 300ms;

/* Easing */
--ease-default: cubic-bezier(0.4, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Common Animations

```tsx
// Fade in
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.2 }}
/>

// Slide in
<motion.div
  initial={{ opacity: 0, y: 10 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.2 }}
/>

// Scale on hover
<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
/>
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile first approach */
sm: 640px   /* Small devices */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large screens */
```

### Responsive Patterns

```tsx
// Responsive grid
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>

// Responsive spacing
<div className="p-4 md:p-6 lg:p-8">
  {/* Content */}
</div>

// Hide/show based on breakpoint
<div className="hidden md:block">Desktop only</div>
<div className="md:hidden">Mobile only</div>
```

---

## Loading States

### Skeleton

```tsx
<div className="space-y-4">
  <Skeleton className="h-12 w-12 rounded-full" />
  <Skeleton className="h-4 w-[250px]" />
  <Skeleton className="h-4 w-[200px]" />
</div>
```

### Spinner

```tsx
<Spinner className="h-6 w-6" />
```

### Progress

```tsx
<Progress value={progress} max={100} />
```

---

## Error States

### Inline Error

```tsx
<Input error="This field is required" />
```

### Alert

```tsx
<Alert variant="destructive">
  <AlertCircle className="h-4 w-4" />
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>
    Your session has expired. Please log in again.
  </AlertDescription>
</Alert>
```

### Toast

```tsx
toast({
  title: "Error",
  description: "Something went wrong.",
  variant: "destructive",
});
```

---

## Icons

### Lucide Icons Usage

```tsx
import { 
  Home, 
  Settings, 
  User, 
  Search,
  Plus,
  Trash,
  Edit,
  MoreHorizontal,
  ChevronRight,
  Check,
  X,
  AlertCircle,
  Info
} from 'lucide-react';

// Usage
<Home className="h-4 w-4" />
```

### Icon Guidelines

- Use consistent sizes (16px, 20px, 24px)
- Match icon weight with text weight
- Use semantic icons (check for success, x for close)
- Provide aria-labels for icon-only buttons
