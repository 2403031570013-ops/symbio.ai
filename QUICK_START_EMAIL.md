# Quick Start: Enable Real Email OTP Delivery

## For Gmail Users (Fastest Setup)

### Step 1: Enable 2-Factor Authentication (CRITICAL)
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. **This is required for App Passwords to work**

### Step 2: Generate Gmail App Password
1. Go to https://myaccount.google.com/apppasswords
2. Login to your Google account
3. Select "Mail" from the app dropdown
4. Select "Other (Custom name)" and enter "SymbioAI"
5. Click "Generate" 
6. Copy the 16-character password (it will look like: `abcd efgh ijkl mnop`)

### Step 3: Add to Render Environment Variables
In your Render dashboard, add these environment variables:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true
```

### Step 4: Redeploy
Click "Deploy" in Render and the system will start sending real OTPs to your Gmail!

## Alternative: Use Resend (Production Ready)

### Step 1: Get Resend API Key
1. Sign up at https://resend.com/
2. Go to API Keys section
3. Create a new API key
4. Copy the API key

### Step 2: Add to Render Environment Variables
```
RESEND_API_KEY=re_xxxxxxxxxxxxx
OTP_PROVIDER=resend
SMTP_FROM_EMAIL=your-email@yourdomain.com
```

### Step 3: Redeploy
Click "Deploy" in Render

## Test Your Setup
1. Go to your application
2. Start registration
3. Enter your email
4. Click "Send verification code"
5. Check your email inbox - you should receive a real OTP!

## Troubleshooting
- **Gmail not working**: 
  - Make sure 2-Step Verification is ENABLED
  - Make sure you're using an App Password, not your regular password
  - Regenerate the App Password if it's not working
- **Email not arriving**: Check spam folder, verify email address is correct
- **Resend not working**: Verify your API key and check your Resend dashboard
- **Authentication failed**: The App Password might be incorrect or revoked

## Debug Steps
1. Check Render logs for detailed error messages
2. Verify all environment variables are set correctly
3. Make sure SMTP_HOST is exactly `smtp.gmail.com` (not `antp.gmail.com` or similar)
4. Ensure the email matches the one used to generate the App Password
5. Check that 2-Step Verification is enabled on your Google account

## For Mobile OTP (Optional)
To enable SMS verification, set up Twilio:
1. Get credentials from https://www.twilio.com/
2. Add: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
3. Redeploy

The system will automatically use real email/SMS when configured, and fall back to development mode when not configured.
