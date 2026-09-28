# 🚀 User Registration and Forgot Password

I've fully implemented the user registration and password recovery flows, wrapping up the authentication enhancements.

### 🗂️ What Changed?
- **User Registration (`/auth/register`)**: Added a dynamic sign-up page where users can specify a username, email, password, and their chosen role (Creditor or Debtor). A profile row for their specific role is created securely in the database under the hood.
- **Forgot Password (`/auth/forgot_password`)**: The forgot password page is now fully functional. It securely locates the user via their email and generates an expiring, cryptographically secure reset token using `itsdangerous.URLSafeTimedSerializer` with the application's secret key. 
  - *Note:* The reset link is flashed to the screen as an alert and logged to the console for testing since an SMTP email server is not configured yet. 
- **Reset Password (`/auth/reset_password/<token>`)**: Built a secure route and template that validates the timestamped token, ensures it has not expired, and permits the user to enter a new password.
- **Audit Logging**: All registration and password reset actions are seamlessly tracked inside the central Audit Log.

### ✅ Validation
- Run comprehensive pytest suite (`tests/test_auth.py`). 
- Verified `test_register` validates the full signup form flow and successfully issues a session token.
- Verified `test_forgot_and_reset_password` properly retrieves a mocked URL token, completes the password reset sequence, and subsequently logs in correctly using the newly set password.
- Total tests passed: `11/11`.
