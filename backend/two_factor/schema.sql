-- Add 2FA columns to profiles table
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS two_factor_secret TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS two_factor_method TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS backup_codes TEXT[];
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS two_factor_enabled_at TIMESTAMP WITH TIME ZONE;

-- 2FA verification logs table
CREATE TABLE IF NOT EXISTS two_factor_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    method TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address TEXT
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_two_factor_logs_user_id ON two_factor_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_two_factor_logs_verified_at ON two_factor_logs(verified_at);

-- Row Level Security
ALTER TABLE two_factor_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own 2FA logs" ON two_factor_logs
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Admins can view all 2FA logs" ON two_factor_logs
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND is_admin = TRUE)
    );

