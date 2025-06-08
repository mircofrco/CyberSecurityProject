import React, { useState } from 'react';
import { api } from '../api';

interface MFAVerifyProps {
  token: string;
  onCancel: () => void;
}

export const MFAVerify: React.FC<MFAVerifyProps> = ({ token, onCancel }) => {
  const [verificationCode, setVerificationCode] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const result = await api.verifyMFA(token, verificationCode);
      setSuccess(result.detail || 'MFA verification successful!');
      setVerificationCode('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h3>Test MFA Verification</h3>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <form onSubmit={handleVerify}>
        <div style={{ marginBottom: '20px' }}>
          <p>Enter the current 6-digit code from your authenticator app to test MFA:</p>
        </div>

        <div className="form-group">
          <label>Verification Code:</label>
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
              fontSize: '20px',
              letterSpacing: '4px',
              fontFamily: 'monospace'
            }}
          />
          <small style={{ color: '#666', fontSize: '12px' }}>
            Codes refresh every 30 seconds
          </small>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button type="submit" disabled={loading || verificationCode.length !== 6}>
            {loading ? 'Verifying...' : 'Verify Code'}
          </button>
          <button type="button" onClick={onCancel} className="link-button">
            Cancel
          </button>
        </div>
      </form>

      <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
        <p><strong>Note:</strong> This is just a test verification. In a real voting system, MFA would be required for sensitive operations like casting votes or accessing admin functions.</p>
      </div>
    </div>
  );
};