import React, { useState } from 'react';
import { api } from '../api';

interface MFASetupProps {
  token: string;
  onMFAEnabled: () => void;
  onCancel: () => void;
}

export const MFASetup: React.FC<MFASetupProps> = ({ token, onMFAEnabled, onCancel }) => {
  const [step, setStep] = useState<'initial' | 'qr' | 'verify'>('initial');
  const [qrCode, setQrCode] = useState<string>('');
  const [otpauthUrl, setOtpauthUrl] = useState<string>('');
  const [verificationCode, setVerificationCode] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  const handleSetupMFA = async () => {
    setLoading(true);
    setError('');

    try {
      const result = await api.setupMFA(token);
      setQrCode(result.qr);
      setOtpauthUrl(result.otpauth_url);
      setStep('qr');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'MFA setup failed');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyMFA = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api.verifyMFA(token, verificationCode);
      setSuccess('MFA successfully enabled!');
      setTimeout(() => {
        onMFAEnabled();
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  const extractSecret = (url: string): string => {
    const match = url.match(/secret=([A-Z2-7]+)/);
    return match ? match[1] : '';
  };

  if (step === 'initial') {
    return (
      <div className="auth-container">
        <h3>Enable Two-Factor Authentication</h3>

        {error && <div className="error">{error}</div>}

        <div style={{ marginBottom: '20px' }}>
          <p>Two-factor authentication adds an extra layer of security to your account.</p>
          <p>You'll need an authenticator app like:</p>
          <ul style={{ paddingLeft: '20px', margin: '10px 0' }}>
            <li>Google Authenticator</li>
            <li>Authy</li>
            <li>Microsoft Authenticator</li>
            <li>1Password</li>
          </ul>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={handleSetupMFA} disabled={loading}>
            {loading ? 'Setting up...' : 'Setup 2FA'}
          </button>
          <button onClick={onCancel} className="link-button">
            Cancel
          </button>
        </div>
      </div>
    );
  }

  if (step === 'qr') {
    return (
      <div className="auth-container">
        <h3>Scan QR Code</h3>

        {error && <div className="error">{error}</div>}

        <div style={{ marginBottom: '20px' }}>
          <p><strong>Step 1:</strong> Scan this QR code with your authenticator app</p>

          <div style={{ textAlign: 'center', margin: '20px 0' }}>
            <img
              src={qrCode}
              alt="QR Code for MFA"
              style={{ maxWidth: '200px', border: '1px solid #ddd', padding: '10px' }}
            />
          </div>

          <p><strong>Step 2:</strong> If you can't scan the QR code, manually enter this secret:</p>
          <div style={{
            background: '#f5f5f5',
            padding: '10px',
            borderRadius: '4px',
            fontFamily: 'monospace',
            wordBreak: 'break-all',
            fontSize: '14px'
          }}>
            {extractSecret(otpauthUrl)}
          </div>
        </div>

        <button onClick={() => setStep('verify')}>
          I've Added It to My App
        </button>
      </div>
    );
  }

  if (step === 'verify') {
    return (
      <div className="auth-container">
        <h3>Verify Setup</h3>

        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}

        <form onSubmit={handleVerifyMFA}>
          <div style={{ marginBottom: '20px' }}>
            <p>Enter the 6-digit code from your authenticator app:</p>
          </div>

          <div className="form-group">
            <input
              type="text"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="000000"
              maxLength={6}
              required
              disabled={loading}
              style={{
                textAlign: 'center',
                fontSize: '24px',
                letterSpacing: '8px',
                fontFamily: 'monospace'
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button type="submit" disabled={loading || verificationCode.length !== 6}>
              {loading ? 'Verifying...' : 'Verify & Enable 2FA'}
            </button>
            <button type="button" onClick={() => setStep('qr')} className="link-button">
              Back to QR Code
            </button>
          </div>
        </form>
      </div>
    );
  }

  return null;
};