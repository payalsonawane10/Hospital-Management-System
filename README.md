I want to create a highly attractive, premium and professional **Authentication UI** for my existing Django Hospital Management System called **MediCare Hospital**.

This task is specifically for:

1. Login Page
2. Register Page
3. Logout functionality and Logout section

Do NOT modify or break my existing hospital management functionality.

## IMPORTANT USER FLOW

Implement this authentication flow:

### First Visit

When a user opens the website for the first time and is NOT authenticated:

Show the **Login page** first.

The Login page should have a clear option:
**“Don't have an account? Create an account”**

Clicking it should open the **Register page**.

### After Registration

After successful registration:

* Automatically redirect the user to the Login page.
* Show a professional success message such as:
  “Registration successful. Please login to continue.”

### After Login

After successful login:

* Redirect the user to the existing Dashboard.
* Show the complete hospital management system.

### Logout

Add a clearly visible **Logout** section/button in the existing sidebar navigation.

When the user clicks Logout:

* Log the user out securely using Django authentication.
* Redirect them to the Login page.
* Prevent access to protected hospital pages after logout.
* If an unauthenticated user tries to directly open Dashboard/Patients/Doctors/etc., redirect them to Login.

---

# LOGIN PAGE – PREMIUM UI

Create a highly attractive hospital-themed Login page.

### Visual Design

Use:

* Modern premium healthcare design
* Professional hospital imagery
* Doctor/medical/healthcare visual elements
* Elegant blue/teal healthcare color palette
* Dark navy text
* Clean white cards
* Soft gradients
* Subtle shadows
* Rounded corners
* Beautiful typography
* Smooth animations
* Responsive design

Create a split-screen layout where appropriate:

### Left Section

Show:

* High-quality hospital/healthcare image or video
* “MediCare Hospital”
* Short professional tagline such as:
  **“Smart Healthcare. Better Care.”**

Add subtle visual overlay and animation.

### Right Section

Create a beautiful login card containing:

* MediCare Hospital logo/name
* Welcome Back
* “Login to your hospital management account”
* Email/Username field
* Password field
* Show/Hide password icon
* Remember Me checkbox
* Forgot Password link if password reset exists
* Large attractive **Login** button

Below the form:
**“Don't have an account? Register Now”**

Clicking Register Now should open the Register page.

Add:

* Form validation messages
* Error messages
* Loading state on login
* Smooth button hover effects

---

# REGISTER PAGE – PREMIUM UI

Create a matching premium Register page.

Use the same visual language as the Login page.

### Left Section

Use a different suitable healthcare image/visual if appropriate.

Display:

* MediCare Hospital
* Healthcare-related tagline
* Professional medical visual

### Right Section

Create a registration card with:

* Create Your Account
* Full Name
* Email
* Username
* Phone Number
* Password
* Confirm Password
* Show/Hide password
* Terms & Conditions checkbox
* Attractive **Create Account** button

Below:
**“Already have an account? Login”**

Clicking Login should return to the Login page.

### Registration Validation

Implement proper validation:

* Required fields
* Valid email
* Username validation
* Password strength
* Password confirmation
* Duplicate username/email handling
* Clear error messages

Use Django's existing authentication system where possible.

Do NOT create a duplicate authentication system if Django authentication already exists.

---

# LOGOUT SECTION

Add a professional **Logout** item to the existing sidebar.

Sidebar should contain:

* Dashboard
* Patients
* Doctors
* Appointments
* Departments
* Billing
* Reports
* Settings
* **Logout**

Use an appropriate logout icon.

Logout should:

* Use Django's secure logout mechanism.
* Clear the authenticated session.
* Redirect to `/login/` or the existing login URL.
* Prevent access to protected pages after logout.

Do NOT simply create a frontend-only logout button.

---

# AUTHENTICATION PROTECTION

Make sure protected pages require authentication.

Protect pages such as:

* Dashboard
* Patients
* Doctors
* Appointments
* Departments
* Billing
* Reports
* Settings

If the user is not logged in:
→ Redirect to Login.

If the user is already logged in:
→ Do not unnecessarily show the Login/Register pages.
→ Redirect them to the Dashboard.

---

# ATTRACTIVE UI REQUIREMENTS

Make the Login and Register pages more visually impressive than a basic form.

Add appropriate:

* Healthcare images
* Medical illustrations
* Hospital visuals
* Subtle animated background elements
* Glass/modern card effects where suitable
* Smooth transitions
* Beautiful input fields
* Professional icons
* Password visibility toggle
* Button animations
* Success/error notifications

However, keep the design:
**Professional + Medical + Premium**

Do NOT make it look like a gaming website or overly colorful template.

---

# RESPONSIVE DESIGN

The Login and Register pages must work perfectly on:

* Desktop
* Laptop
* Tablet
* Mobile

On mobile, automatically convert the split-screen design into a clean single-column layout.

---

# IMPORTANT – EXISTING WEBSITE

First inspect my existing Django project.

Use the same:

* MediCare Hospital branding
* Colors
* Typography
* Components
* CSS
* Sidebar style
* Overall design language

The Login/Register pages should feel like they belong to the same hospital application.

Do NOT break any existing Dashboard, Patient, Doctor, Appointment, Department, Billing or Reports functionality.

---

# FINAL TESTING

After implementation, test the complete flow:

1. Open website while logged out → Login page
2. Click Register → Register page
3. Create account → Login page
4. Login → Dashboard
5. Navigate through protected pages
6. Click Logout → Login page
7. Try opening Dashboard directly after logout → Login page
8. Login again → Dashboard

After completing the work, tell me:

* Files created/modified
* Authentication URLs
* Login URL
* Register URL
* Logout URL
* Any migrations required
* Any packages installed
* Any commands I need to run

Do not consider the task complete until the complete Login → Register → Login → Dashboard → Logout → Login flow works correctly.
