# Implement Registration and Forgot Password

The goal is to implement a robust user registration flow and a fully functional "Forgot Password" feature to allow users to securely recover their accounts.

## User Review Required

- **Registration Roles:** I plan to add a dropdown to the registration form allowing the user to select whether they are registering as a **Creditor** or a **Debtor**. When they register, an associated empty profile (Creditor/Debtor) will be created for them so they can fill in their details later in Settings. Does this approach work for you?
- **Email Delivery:** Since we don't have a live SMTP server configured to send real emails, I will simulate the email delivery by **printing the password reset link to the server console** and **flashing a debug message on the screen** with the link so you can test it locally. Let me know if you prefer setting up a real SMTP server like SendGrid or Gmail.

## Proposed Changes

### `app/auth/`
- **[MODIFY] `routes.py`**:
  - Implement `@bp.route('/register')` to handle creating new users and assigning them roles.
  - Update `forgot_password` to generate a secure timed token using `itsdangerous.URLSafeTimedSerializer`.
  - Add `@bp.route('/reset_password/<token>')` to handle password resets.
  
### `app/templates/auth/`
- **[NEW] `register.html`**: A clean, localized UI for the registration form with fields for Username, Email, Password, and Role selection.
- **[MODIFY] `login.html`**: Add a "Don't have an account? Sign up" link.
- **[NEW] `reset_password.html`**: A form for users to enter their new password after clicking the reset link.

### `app/models/`
- **[MODIFY] `user.py`**: We'll ensure the `User` model has a helper method or use `itsdangerous` directly in the auth routes to generate/verify reset tokens.

## Verification Plan

### Automated Tests
- Run `pytest` to ensure existing authentication flows still work.
- Add basic unit tests for the `/register` and `/forgot_password` endpoints.

### Manual Verification
- Manually register a new Creditor and a new Debtor through the UI.
- Verify they can log in and reach their respective dashboards.
- Test the "Forgot Password" flow by requesting a reset, copying the simulated link, and resetting the password.
