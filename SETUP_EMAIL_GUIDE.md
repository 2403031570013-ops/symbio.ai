# Email & SMS Setup Guide for SymbioAI

## Option 1: Using Gmail (Recommended for Testing)

### Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled

### Step 2: Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" from the app dropdown
3. Select "Other (Custom name)" and enter "SymbioAI"
4. Click "Generate"
5. Copy the 16-character password (without spaces)

### Step 3: Configure Environment Variables
Add these to your `.env` file or Render dashboard:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true
```

### Step 4: Test
Restart your application and try sending an OTP. You should receive it in your Gmail inbox.

## Option 2: Using Resend (Production Ready)

### Step 1: Get Resend API Key
1. Sign up at https://resend.com/
2. Go to API Keys section
3. Create a new API key
4. Copy the API key

### Step 2: Configure Environment Variables
Add these to your `.env` file or Render dashboard:

```
RESEND_API_KEY=re_xxxxxxxxxxxxx
OTP_PROVIDER=resend
```

### Step 3: Test
Restart your application and try sending an OTP.

## Option 3: Development Mode (No Email Required)

For testing without email configuration, the system will:
- Display OTP codes directly in the UI
- Use test codes: Email OTP = 654321, Mobile OTP = 123456, Factory Code = 123456

This is automatically enabled when:
- `ENVIRONMENT=development`
- No email provider is configured

## Troubleshooting

### Gmail not sending emails:
- Make sure you're using an App Password, not your regular password
- Check if "Less Secure Apps" is enabled (if using older Gmail)
- Verify SMTP port is 587 (TLS) or 465 (SSL)

### Resend not working:
- Verify your API key is correct
- Check your Resend dashboard for API usage limits
- Ensure your domain is verified in Resend

### Development OTP not showing:
- Check that `ENVIRONMENT=development` is set
- Ensure no email provider is configured
- Look for the OTP in the API response data

## SMS Setup (Optional)

### Using Twilio for Mobile OTP

### Step 1: Get Twilio Account
1. Sign up at https://www.twilio.com/
2. Get your Account SID and Auth Token from the console
3. Purchase a phone number or use the trial number

### Step 2: Configure Environment Variables
Add these to your `.env` file or Render dashboard:

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

### Step 3: Test
Restart your application and try sending a mobile OTP.

## Security Notes

- Never commit your email/SMS credentials to git
- Use environment variables for all sensitive data
- Rotate API keys and passwords regularly
- Use separate credentials for development and production
- For Gmail, always use App Passwords, not regular passwords
