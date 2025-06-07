# CogniCare Development Guide

## Design System Implementation

This guide outlines the comprehensive design system implemented across the CogniCare platform to maintain consistency and reduce code duplication.

## CSS Architecture

### 1. Base Template System
- **File**: `templates/layouts/base.html`
- Contains all common CSS variables, dashboard components, and universal styling
- Used by ALL templates via `{% extends 'layouts/base.html' %}`

### 2. Design System CSS
- **File**: `static/css/design-system.css`
- Contains reusable components for forms, buttons, tasks, and utilities
- Included automatically in base template

## Component Library

### Role-Based Theming
The system uses CSS custom properties for consistent role-based theming:

```css
:root {
    --patient-primary: #9333ea;
    --patient-secondary: #7c3aed;
    --caregiver-primary: #059669;
    --caregiver-secondary: #047857;
    --provider-primary: #1e3a8a;
    --provider-secondary: #1e40af;
    --admin-primary: #1a202c;
    --admin-secondary: #2d3748;
}
```

### Form Components

#### Login/Authentication Pages
Instead of writing custom CSS, use these classes:

```html
<div class="form-page patient">
    <div class="form-container patient">
        <div class="form-header">
            <div class="form-icon">🧠</div>
            <h1>Patient Portal</h1>
            <p class="form-description">Access your dashboard</p>
        </div>
        <div class="form-content">
            <form class="form">
                <div class="form-group">
                    <label class="form-label">
                        <span class="label-icon">👤</span>
                        Username
                    </label>
                    <input type="text" class="form-input patient" placeholder="Enter username">
                </div>
                <button type="submit" class="btn patient full-width">
                    <span>Sign In</span>
                </button>
            </form>
        </div>
    </div>
</div>
```

### Button System

#### Role-specific buttons:
```html
<!-- Patient buttons -->
<button class="btn patient">Patient Action</button>
<button class="btn patient large">Large Patient Button</button>
<button class="btn patient outline">Outline Patient Button</button>

<!-- Caregiver buttons -->
<button class="btn caregiver">Caregiver Action</button>

<!-- Provider buttons -->
<button class="btn provider">Provider Action</button>

<!-- Admin buttons -->
<button class="btn admin">Admin Action</button>

<!-- Generic buttons -->
<button class="btn secondary">Cancel</button>
```

### Task Components

#### Task pages should use:
```html
<div class="task-container">
    <div class="task-header">
        <h1 class="task-title">Memory Task</h1>
        <p class="task-description">Complete the following exercise</p>
    </div>
    
    <div class="task-stats">
        <div class="stat-item">
            <span class="stat-number">5</span>
            <span class="stat-label">Questions</span>
        </div>
        <div class="stat-item">
            <span class="stat-number" id="timer">00:00</span>
            <span class="stat-label">Time</span>
        </div>
    </div>
    
    <div class="task-content">
        <!-- Task specific content -->
    </div>
</div>
```

### Dashboard Components

#### Already implemented in base template:
- `.dashboard-container`
- `.dashboard-header` with role classes
- `.dashboard-section`
- `.section-title` with role classes
- `.enhanced-table`
- `.status-badge`
- `.action-btn`

## CSS Optimization Results

### Before Optimization:
- **31 templates** with inline CSS
- **~80% code duplication** across similar components
- **Maintenance nightmare** - changes needed in multiple files
- **Inconsistent styling** across similar elements

### After Optimization:
- **Centralized design system** in base template + design-system.css
- **~90% reduction** in duplicated CSS
- **Consistent theming** across all roles
- **Easy maintenance** - change once, apply everywhere
- **Future-proof** - new pages automatically inherit styles

## Best Practices for New Development

### 1. Always Extend Base Template
```html
{% extends 'layouts/base.html' %}
{% load static %}

{% block title %}Page Title{% endblock %}

{% block content %}
<!-- Your content here -->
{% endblock %}
```

### 2. Use Design System Classes
Instead of custom CSS, use existing classes:
- Form components: `.form-page`, `.form-container`, `.form-input`
- Buttons: `.btn` with role classes
- Tasks: `.task-container`, `.task-header`, `.task-content`
- Layout: `.grid`, `.card`, utility classes

### 3. Role-Based Styling
Always include role classes for consistent theming:
```html
<div class="form-container patient">
<button class="btn caregiver">
<div class="dashboard-header provider">
```

### 4. Minimal Custom CSS
Only add custom CSS for:
- Page-specific unique elements
- Complex interactions not covered by design system
- Animation/behavior that's truly unique

### 5. Mobile-First Responsive
The design system includes responsive breakpoints. Additional responsive rules should follow this pattern:
```css
@media (max-width: 768px) {
    /* Mobile styles */
}
```

## File Structure

```
templates/
├── layouts/
│   └── base.html          # Main template with design system
├── auth/                  # Authentication pages
├── dashboards/           # Role-specific dashboards  
├── tasks/                # Task interfaces
└── pages/                # Static pages

static/
└── css/
    └── design-system.css  # Reusable components
```

## Examples of Optimized Templates

### Login Page (Before: 200+ lines CSS)
```html
{% extends 'layouts/base.html' %}

{% block content %}
<div class="form-page patient">
    <div class="form-container patient">
        <!-- Content with design system classes -->
    </div>
</div>
{% endblock %}

<!-- No <style> block needed! -->
```

### Task Page (Before: 150+ lines CSS)
```html
{% extends 'layouts/base.html' %}

{% block content %}
<div class="task-container">
    <div class="task-header"><!-- Task header --></div>
    <div class="task-content"><!-- Task content --></div>
</div>
{% endblock %}

<!-- Minimal custom CSS only for task-specific behavior -->
```

## Migration Checklist for Existing Templates

1. ✅ **Remove duplicate CSS** from individual templates
2. ✅ **Replace custom classes** with design system classes
3. ✅ **Add role-based classes** for theming
4. ✅ **Test responsive behavior**
5. ✅ **Verify accessibility**

## Future Development Guidelines

### When Adding New Pages:
1. Start with base template extension
2. Use design system components
3. Add role-based classes
4. Only add custom CSS for truly unique elements
5. Test across all roles
6. Ensure mobile responsiveness

### When Modifying Existing Styles:
1. Check if it affects multiple templates
2. If yes, modify base template or design-system.css
3. If no, add minimal custom CSS to specific template
4. Document the change

This system ensures **consistency**, **maintainability**, and **scalability** for the CogniCare platform while dramatically reducing code duplication and development time. 