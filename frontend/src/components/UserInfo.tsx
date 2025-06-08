import React, { useState } from 'react';
import type {User} from '../types';
import { MFASetup } from './MFASetup';
import { MFAVerify } from './MFAVerify';

interface UserInfoProps {
  user: User;
  token: string;
  onLogout: () => void;
  onUserUpdate: () => void;
}

export const UserInfo: React.FC<UserInfoProps> = ({ user, token, onLogout, onUserUpdate }) => {
  const [showMFASetup, setShowMFASetup] = useState(false);
  const [showMFAVerify, setShowMFAVerify] = useState(false);

  const handleMFAEnabled = () => {
    setShowMFASetup(false);
    onUserUpdate(); // Refresh user data to show updated MFA status
  };

  if (showMFASetup) {
    return (
      <MFASetup
        token={token}
        onMFAEnabled={handleMFAEnabled}
        onCancel={() => setShowMFASetup(false)}
      />
    );
  }

  if (showMFAVerify) {
    return (
      <MFAVerify
        token={token}
        onCancel={() => setShowMFAVerify(false)}
      />
    );
  }

  return (
    <div className="user-container">
      <div className="user-header">
        <h2>Welcome, {user.email}</h2>
        <button onClick={onLogout}>Logout</button>
      </div>

      <div className="user-details">
        <h3>Account Information</h3>

        <div className="info-item">
          <strong>User ID:</strong> {user.id}
        </div>

        <div className="info-item">
          <strong>Email:</strong> {user.email}
        </div>

        <div className="info-item">
          <strong>Account Status:</strong>{' '}
          <span className={user.is_active ? 'status-active' : 'status-inactive'}>
            {user.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>

        <div className="info-item">
          <strong>Email Verified:</strong>{' '}
          <span className={user.is_verified ? 'status-verified' : 'status-unverified'}>
            {user.is_verified ? 'Yes' : 'No'}
          </span>
        </div>

        <div className="info-item">
          <strong>2FA Enabled:</strong>{' '}
          <span className={user.mfa_enabled ? 'status-enabled' : 'status-disabled'}>
            {user.mfa_enabled ? 'Yes' : 'No'}
          </span>
        </div>

        <div className="info-item">
          <strong>Super User:</strong>{' '}
          <span className={user.is_superuser ? 'status-super' : 'status-regular'}>
            {user.is_superuser ? 'Yes' : 'No'}
          </span>
        </div>
      </div>

      {/* MFA Management Section */}
      <div className="user-details" style={{ marginTop: '30px' }}>
        <h3>Security Settings</h3>

        {!user.mfa_enabled ? (
          <div>
            <div className="info-item" style={{ background: '#fff3cd', border: '1px solid #ffeaa7' }}>
              <strong>⚠️ Two-Factor Authentication Disabled</strong>
              <p style={{ margin: '10px 0 0 0', color: '#856404' }}>
                Enable 2FA to secure your account before participating in elections.
              </p>
            </div>
            <button
              onClick={() => setShowMFASetup(true)}
              style={{ marginTop: '15px', background: '#28a745' }}
            >
              🔒 Enable Two-Factor Authentication
            </button>
          </div>
        ) : (
          <div>
            <div className="info-item" style={{ background: '#d4edda', border: '1px solid #c3e6cb' }}>
              <strong>✅ Two-Factor Authentication Enabled</strong>
              <p style={{ margin: '10px 0 0 0', color: '#155724' }}>
                Your account is protected with 2FA.
              </p>
            </div>
            <button
              onClick={() => setShowMFAVerify(true)}
              style={{ marginTop: '15px', background: '#007bff' }}
            >
              🔐 Test MFA Verification
            </button>
          </div>
        )}
      </div>

      {/* Account Security Tips */}
      <div className="user-details" style={{ marginTop: '30px' }}>
        <h3>Security Tips</h3>

        <div className="info-item">
          <ul style={{ paddingLeft: '20px', margin: '0' }}>
            <li>Keep your authenticator app installed and backed up</li>
            <li>Never share your verification codes with anyone</li>
            <li>Use a strong, unique password for your account</li>
            <li>Enable 2FA before participating in any elections</li>
          </ul>
        </div>
      </div>
    </div>
  );
};