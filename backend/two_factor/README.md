# Two-Factor Authentication (2FA) Module

## Overview
This module implements TOTP-based Two-Factor Authentication for the SaaS platform, providing an additional layer of security for user accounts.

## Features
- ✅ TOTP (Time-based One-Time Password) support
- ✅ QR code generation for easy authenticator app setup
- ✅ Backup codes for account recovery
- ✅ 2FA verification logs
- ✅ Integration with login flow
- ✅ Row-level security policies

## Database Schema
The module uses two database components:
1. **profiles table** - Extended with 2FA columns:
   - `two_factor_enabled` (boolean)
   - `two_factor_secret` (text)
   - `two_factor_method` (text)
   - `backup_codes` (text array)
   - `two_factor_enabled_at` (timestamp)

2. **two_factor_logs table** - Audit trail:
   - `id` (uuid)
   - `user_id` (uuid, FK to profiles)
   - `method` (text: 'totp' or 'backup_code')
   - `success` (boolean)
   - `verified_at` (timestamp)
   - `ip_address` (text)

## API Endpoints

### Setup 2FA
```http
POST /api/2fa/setup
Authorization: Bearer <token>

Response:
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code_url": "data:image/png;base64,...",
  "backup_codes": [
    "AAAA-BBBB-CCCC",
    "DDDD-EEEE-FFFF",
    ...
  ]
}
```

### Enable 2FA
```http
POST /api/2fa/enable
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "123456"
}

Response:
{
  "message": "2FA enabled successfully"
}
```

### Verify 2FA Code
```http
POST /api/2fa/verify
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "123456"
}

Response:
{
  "verified": true
}
```

### Verify Backup Code
```http
POST /api/2fa/verify-backup
Authorization: Bearer <token>
Content-Type: application/json

{
  "backup_code": "AAAA-BBBB-CCCC"
}

Response:
{
  "verified": true
}
```

### Disable 2FA
```http
POST /api/2fa/disable
Authorization: Bearer <token>
Content-Type: application/json

{
  "password": "user_password"
}

Response:
{
  "message": "2FA disabled successfully"
}
```

### Get 2FA Status
```http
GET /api/2fa/status
Authorization: Bearer <token>

Response:
{
  "enabled": true,
  "method": "totp",
  "backup_codes_remaining": 8
}
```

### Complete 2FA Login
```http
POST /api/auth/login/2fa
Content-Type: application/json

{
  "user_id": "uuid",
  "code": "123456"
}

Response:
{
  "access_token": "...",
  "token_type": "bearer",
  "user": { ... }
}
```

## Login Flow with 2FA

1. User submits credentials to `/api/auth/login`
2. If user has 2FA enabled:
   - Server returns 403 with `X-Requires-2FA: true` header
   - Pending login stored in Redis cache (5 min expiration)
3. Frontend shows 2FA verification screen
4. User enters TOTP code or backup code
5. Submit to `/api/auth/login/2fa`
6. On success, receive access token and complete login

## Setup Process

### User Setup Flow:
1. User navigates to Security Settings
2. Clicks "Setup 2FA"
3. Backend generates secret and QR code
4. User scans QR code with authenticator app (Google Authenticator, Authy, etc.)
5. User saves backup codes
6. User enters verification code
7. 2FA is enabled

### Authenticator Apps:
- Google Authenticator (iOS/Android)
- Microsoft Authenticator (iOS/Android)
- Authy (iOS/Android/Desktop)
- 1Password
- LastPass Authenticator

## Security Features

### Password Hashing
- Backup codes are hashed using SHA-256 before storage
- Codes are single-use and removed after verification

### Rate Limiting
- Login attempts are rate-limited
- 2FA verification attempts tracked

### Session Management
- Pending 2FA logins expire after 5 minutes
- Setup sessions expire after 15 minutes

### Audit Trail
- All 2FA verification attempts logged
- Includes success/failure, method, timestamp
- IP address tracking (when implemented)

## Testing

### Run Tests
```bash
cd backend
pytest tests/test_two_factor.py -v
```

### Manual Testing Checklist

1. **Setup 2FA**
   - [ ] Generate QR code
   - [ ] Receive backup codes
   - [ ] Secret stored temporarily in cache

2. **Enable 2FA**
   - [ ] Valid code enables 2FA
   - [ ] Invalid code rejected
   - [ ] Data persisted to database
   - [ ] Cache cleared after enable

3. **Login with 2FA**
   - [ ] Login requires 2FA verification
   - [ ] Valid TOTP code completes login
   - [ ] Invalid code rejected
   - [ ] Backup code works
   - [ ] Used backup code removed

4. **Disable 2FA**
   - [ ] Password required
   - [ ] 2FA data cleared from database
   - [ ] Login works without 2FA

5. **Status Check**
   - [ ] Correct status returned
   - [ ] Backup code count accurate

## Frontend Integration

### Components:
- `TwoFactorSetup` - Setup wizard with QR code
- `TwoFactorVerify` - Verification during login
- `TwoFactorDisable` - Disable 2FA
- `SettingsPage` - Security settings page

### API Client Functions:
```typescript
setup2FA()
enable2FA(code)
verify2FA(code)
verifyBackupCode(backupCode)
disable2FA(password, code?)
get2FAStatus()
complete2FALogin(userId, code)
```

## Troubleshooting

### QR Code Not Scanning
- Ensure adequate screen brightness
- Try manual entry with the secret key
- Check authenticator app compatibility

### Code Not Working
- Verify device time is synchronized (NTP)
- Code expires every 30 seconds
- Check for typos in manual entry

### Lost Backup Codes
- User must disable 2FA (if they can still log in)
- Admin can disable 2FA for user in database
- Re-enable and generate new codes

### Database Issues
```sql
-- Check 2FA status for user
SELECT two_factor_enabled, two_factor_method, 
       array_length(backup_codes, 1) as backup_codes_count
FROM profiles 
WHERE id = 'user_id';

-- View recent 2FA logs
SELECT * FROM two_factor_logs 
WHERE user_id = 'user_id' 
ORDER BY verified_at DESC 
LIMIT 10;

-- Disable 2FA for user (admin only)
UPDATE profiles 
SET two_factor_enabled = false,
    two_factor_secret = NULL,
    two_factor_method = NULL,
    backup_codes = ARRAY[]::text[]
WHERE id = 'user_id';
```

## Dependencies
- `pyotp` - TOTP generation and verification
- `qrcode` - QR code generation
- `Pillow` - Image processing for QR codes

## Future Enhancements
- [ ] SMS-based 2FA
- [ ] WebAuthn/FIDO2 support
- [ ] Remember device functionality
- [ ] IP address logging
- [ ] Backup code regeneration
- [ ] 2FA enforcement for admin users
- [ ] Email notifications on 2FA changes
