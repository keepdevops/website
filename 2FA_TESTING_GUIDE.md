# 2FA Implementation Testing Guide

## Quick Start

### 1. Database Setup
Ensure the database schema is applied:
```bash
# The schema should already be applied, but verify:
psql $DATABASE_URL -f backend/two_factor/schema.sql
```

### 2. Start Backend
```bash
cd backend
python main.py
```

The backend should show:
```
INFO:     Loaded router for plugin: two_factor
```

### 3. Start Frontend
```bash
npm run dev
```

## Testing Workflow

### Step 1: Create Test Account
1. Navigate to http://localhost:3000/register
2. Register with:
   - Email: test@example.com
   - Password: TestPassword123!
   - Full Name: Test User

### Step 2: Enable 2FA
1. Login with test account
2. Navigate to http://localhost:3000/dashboard/settings
3. Click "Setup 2FA"
4. You should see:
   - QR code image
   - Manual entry secret key
   - 8 backup codes

5. Use an authenticator app to scan the QR code:
   - **Google Authenticator** (recommended)
   - **Authy**
   - **Microsoft Authenticator**

6. **IMPORTANT**: Save the backup codes somewhere safe!

7. Enter the 6-digit code from your authenticator app
8. Click "Enable 2FA"
9. You should see: "2FA enabled successfully!"

### Step 3: Test Login with 2FA
1. Logout
2. Login again with the same credentials
3. After entering email/password, you should see the 2FA verification screen
4. Enter the current 6-digit code from your authenticator app
5. You should be logged in successfully

### Step 4: Test Backup Code
1. Logout
2. Login with credentials
3. On the 2FA screen, click "Use backup code"
4. Enter one of your saved backup codes (format: XXXX-XXXX-XXXX)
5. You should be logged in successfully
6. Navigate to Settings - the backup code count should decrease by 1

### Step 5: Test Invalid Codes
1. Logout and login again
2. Enter an incorrect code (e.g., 000000)
3. You should see: "Invalid 2FA code"
4. The login should NOT complete

### Step 6: Disable 2FA
1. Login successfully (using valid code)
2. Go to Settings
3. Click "Disable 2FA"
4. Enter your password
5. Click "Confirm Disable"
6. 2FA should be disabled
7. Logout and login - should NOT require 2FA anymore

## API Testing with curl

### 1. Login and Get Token
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPassword123!"}'

# Save the access_token from response
export TOKEN="your_access_token_here"
```

### 2. Setup 2FA
```bash
curl -X POST http://localhost:8000/api/2fa/setup \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

Expected response:
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code_url": "data:image/png;base64,...",
  "backup_codes": ["AAAA-BBBB-CCCC", ...]
}
```

### 3. Enable 2FA
```bash
# Get current code from authenticator app
curl -X POST http://localhost:8000/api/2fa/enable \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"123456"}'
```

### 4. Check 2FA Status
```bash
curl -X GET http://localhost:8000/api/2fa/status \
  -H "Authorization: Bearer $TOKEN"
```

Expected response:
```json
{
  "enabled": true,
  "method": "totp",
  "backup_codes_remaining": 8
}
```

### 5. Test 2FA Login Flow
```bash
# Step 1: Login (will fail with 403 if 2FA enabled)
curl -i -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPassword123!"}'

# You should see:
# HTTP/1.1 403 Forbidden
# X-Requires-2FA: true
# X-User-ID: <user_id>

# Step 2: Complete 2FA login
curl -X POST http://localhost:8000/api/auth/login/2fa \
  -H "Content-Type: application/json" \
  -d '{"user_id":"<user_id_from_header>","code":"123456"}'
```

### 6. Verify Code
```bash
curl -X POST http://localhost:8000/api/2fa/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"123456"}'
```

### 7. Verify Backup Code
```bash
curl -X POST http://localhost:8000/api/2fa/verify-backup \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"backup_code":"AAAA-BBBB-CCCC"}'
```

### 8. Disable 2FA
```bash
curl -X POST http://localhost:8000/api/2fa/disable \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password":"TestPassword123!"}'
```

## Database Verification

### Check 2FA Status in Database
```sql
-- Connect to your database
psql $DATABASE_URL

-- Check user's 2FA status
SELECT 
  id, 
  email, 
  two_factor_enabled, 
  two_factor_method,
  array_length(backup_codes, 1) as backup_codes_count,
  two_factor_enabled_at
FROM profiles 
WHERE email = 'test@example.com';
```

### View 2FA Logs
```sql
SELECT 
  l.id,
  p.email,
  l.method,
  l.success,
  l.verified_at
FROM two_factor_logs l
JOIN profiles p ON l.user_id = p.id
ORDER BY l.verified_at DESC
LIMIT 10;
```

## Automated Tests

### Run Backend Tests
```bash
cd backend
pytest tests/test_two_factor.py -v
```

Expected output:
```
test_two_factor.py::TestTwoFactorService::test_setup_totp PASSED
test_two_factor.py::TestTwoFactorService::test_enable_2fa_success PASSED
test_two_factor.py::TestTwoFactorService::test_enable_2fa_invalid_code PASSED
test_two_factor.py::TestTwoFactorService::test_verify_totp_success PASSED
...
```

## Common Issues & Solutions

### Issue: "No 2FA setup in progress"
**Cause**: Setup session expired (15 minutes) or cache cleared
**Solution**: Start setup process again

### Issue: "Invalid verification code"
**Cause**: 
- Device time not synchronized
- Code expired (30-second window)
- Wrong secret scanned

**Solution**:
- Ensure device time is set to automatic/NTP
- Try the next code from authenticator
- Re-scan QR code

### Issue: QR code not displaying
**Cause**: Missing dependencies or image generation error
**Solution**:
```bash
pip install qrcode[pil] pillow
```

### Issue: "No pending 2FA login found"
**Cause**: Login session expired (5 minutes)
**Solution**: Start login process again

### Issue: Backup codes not working
**Cause**: 
- Code already used
- Typo in code entry
- Codes not saved correctly

**Solution**:
- Try another backup code
- Ensure correct format: XXXX-XXXX-XXXX
- Check database for remaining codes

## Security Testing

### Test Rate Limiting
```bash
# Rapid login attempts should be rate-limited
for i in {1..20}; do
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}'
done
```

### Test Session Expiration
1. Start 2FA setup
2. Wait 15+ minutes
3. Try to enable - should fail

### Test Code Validation
```bash
# Try various invalid codes
curl -X POST http://localhost:8000/api/2fa/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"000000"}'  # Should fail

curl -X POST http://localhost:8000/api/2fa/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"abcdef"}'  # Should fail
```

## Performance Testing

### Check Response Times
```bash
# Setup endpoint
time curl -X POST http://localhost:8000/api/2fa/setup \
  -H "Authorization: Bearer $TOKEN"

# Verify endpoint
time curl -X POST http://localhost:8000/api/2fa/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"123456"}'
```

Expected:
- Setup: < 500ms
- Verify: < 100ms

## Checklist

- [ ] Database schema applied successfully
- [ ] Backend starts without errors
- [ ] 2FA router loaded in plugin registry
- [ ] Can setup 2FA and receive QR code
- [ ] Can scan QR code with authenticator app
- [ ] Can enable 2FA with valid code
- [ ] Login requires 2FA after enabling
- [ ] Can login with TOTP code
- [ ] Can login with backup code
- [ ] Backup code is removed after use
- [ ] Can disable 2FA
- [ ] All automated tests pass
- [ ] Settings page displays correctly
- [ ] 2FA status updates in real-time

## Next Steps

After successful testing:
1. Deploy to staging environment
2. Test with real email/phone numbers
3. Add monitoring for 2FA events
4. Document user-facing 2FA guide
5. Train support team on 2FA issues
6. Consider enforcing 2FA for admin users


