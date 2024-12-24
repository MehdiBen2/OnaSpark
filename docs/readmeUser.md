# ONA SPARK - User Management Documentation

## User Creation Panel

The user creation functionality in ONA SPARK is implemented as a sliding panel that appears from the right side of the screen. This document details the implementation, fields, and functionality.

### Panel Structure

```html
<div id="userPanel" class="sliding-panel">
    <div class="sliding-panel-overlay"></div>
    <div class="sliding-panel-content">
        <!-- Panel content -->
    </div>
</div>
```

### Form Fields

1. **Username (Required)**
   - Field ID: `username`
   - Type: Text input
   - Validation: Required
   - Purpose: Main identifier for the user

2. **Nickname (Optional)**
   - Field ID: `nickname`
   - Type: Text input
   - Purpose: Alternative display name

3. **Password (Required)**
   - Field ID: `password`
   - Type: Password input with toggle visibility
   - Validation: Required
   - Features: Toggle button to show/hide password

4. **Role (Required)**
   - Field ID: `role`
   - Type: Select dropdown
   - Options:
     - Admin
     - Zone Director
     - Unit Director
     - Unit Officer
   - Behavior: Changes visible fields based on selection

5. **Zone (Conditional)**
   - Field ID: `zone_id`
   - Type: Select dropdown
   - Visibility: Shown for Zone Director, Unit Director, and Unit Officer
   - Required: For Zone Director, Unit Director, and Unit Officer
   - Data: Populated from database

6. **Unit (Conditional)**
   - Field ID: `unit_id`
   - Type: Select dropdown
   - Visibility: Shown for Unit Director and Unit Officer
   - Required: For Unit Director and Unit Officer
   - Data: Dynamically loaded based on selected zone

### Role-Based Field Display

```javascript
Role Type        | Zone Field | Unit Field
----------------|------------|------------
Admin           | Hidden     | Hidden
Zone Director   | Shown      | Hidden
Unit Director   | Shown      | Shown
Unit Officer    | Shown      | Shown
```

### API Endpoints

1. **Create User**
   - Route: `/admin/users/create`
   - Method: POST
   - Fields: All form fields

2. **Get Units by Zone**
   - Route: `/admin/zones/<zone_id>/units`
   - Method: GET
   - Returns: List of units for selected zone

### CSS Classes

```css
.sliding-panel           // Main panel container
.sliding-panel-overlay   // Dark overlay behind panel
.sliding-panel-content   // Panel content wrapper
.sliding-panel-header    // Panel header with gradient
.sliding-panel-body      // Main content area
.sliding-panel-footer    // Action buttons area
```

### JavaScript Functions

1. **Panel Control**
   ```javascript
   openUserPanel()       // Opens the sliding panel
   closeUserPanel()      // Closes the panel and resets form
   ```

2. **Form Handling**
   ```javascript
   handleRoleChange()    // Manages field visibility based on role
   loadUnits()          // Loads units when zone is selected
   ```

3. **Validation**
   ```javascript
   // Form validation on submit
   createUserForm.addEventListener('submit', function(event) {
       if (!this.checkValidity()) {
           event.preventDefault();
           event.stopPropagation();
       }
       this.classList.add('was-validated');
   });
   ```

### Event Listeners

1. **Panel Events**
   - Click outside panel to close
   - Close button click
   - Cancel button click

2. **Form Events**
   - Role selection change
   - Zone selection change
   - Form submission
   - Password visibility toggle

### Animation Details

The panel uses CSS transitions for smooth animations:
```css
.sliding-panel {
    transition: visibility 0s linear 0.3s;
}

.sliding-panel-content {
    transition: right 0.3s ease;
}

.sliding-panel-overlay {
    transition: opacity 0.3s ease, visibility 0.3s ease;
}
```

### Best Practices

1. **Form Reset**
   - Always reset form when closing panel
   - Clear validation states
   - Reset field visibility

2. **Error Handling**
   - Validate all inputs
   - Show clear error messages
   - Handle API errors gracefully

3. **Accessibility**
   - Maintain proper focus management
   - Use ARIA labels
   - Support keyboard navigation

### Common Issues and Solutions

1. **Panel Not Showing**
   - Check z-index values
   - Verify event listeners
   - Check for JavaScript errors

2. **Form Validation Issues**
   - Ensure all required fields are marked
   - Check role-based field requirements
   - Verify form submission event

3. **Unit Loading Problems**
   - Check API endpoint
   - Verify zone ID is being passed
   - Handle loading states properly

### Future Improvements

1. **Suggested Enhancements**
   - Add password strength indicator
   - Implement user avatar upload
   - Add role permission preview
   - Implement real-time username availability check

2. **Security Considerations**
   - Implement password complexity requirements
   - Add rate limiting for form submission
   - Implement CSRF protection

### Testing Checklist

1. **Functionality Tests**
   - [ ] Panel opens and closes smoothly
   - [ ] All form fields work correctly
   - [ ] Role-based field visibility works
   - [ ] Unit loading works for all zones
   - [ ] Form validation works properly
   - [ ] Password toggle works

2. **Visual Tests**
   - [ ] Panel animations are smooth
   - [ ] Overlay appears correctly
   - [ ] Form layout is consistent
   - [ ] Error states are visible
   - [ ] Loading states are clear

3. **Integration Tests**
   - [ ] API endpoints respond correctly
   - [ ] Data is saved properly
   - [ ] Error handling works
   - [ ] Success feedback is shown
