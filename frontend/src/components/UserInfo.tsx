import React, { useState } from 'react';
import type {User, Election} from '../types';
import { MFASetup } from './MFASetup';
import { MFAVerify } from './MFAVerify';
import { ElectionList } from './ElectionList';
import { VotingInterface } from './VotingInterface';

interface UserInfoProps {
  user: User;
  token: string;
  onLogout: () => void;
  onUserUpdate: () => void;
}

type ViewMode = 'dashboard' | 'mfa-setup' | 'mfa-verify' | 'elections' | 'voting';

export const UserInfo: React.FC<UserInfoProps> = ({ user, token, onLogout, onUserUpdate }) => {
  const [currentView, setCurrentView] = useState<ViewMode>('dashboard');
  const [selectedElection, setSelectedElection] = useState<Election | null>(null);

  const handleMFAEnabled = () => {
    setCurrentView('dashboard');
    onUserUpdate(); // Refresh user data to show updated MFA status
  };

  const handleSelectElection = (election: Election) => {
    setSelectedElection(election);
    setCurrentView('voting');
  };

  const handleVoteSuccess = () => {
    setCurrentView('elections');
    setSelectedElection(null);
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'mfa-setup':
        return (
          <MFASetup
            token={token}
            onMFAEnabled={handleMFAEnabled}
            onCancel={() => setCurrentView('dashboard')}
          />
        );

      case 'mfa-verify':
        return (
          <MFAVerify
            token={token}
            onCancel={() => setCurrentView('dashboard')}
          />
        );

      case 'elections':
        return (
          <ElectionList
            token={token}
            onSelectElection={handleSelectElection}
          />
        );

      case 'voting':
        return selectedElection ? (
          <VotingInterface
            election={selectedElection}
            token={token}
            onBack={() => setCurrentView('elections')}
            onVoteSuccess={handleVoteSuccess}
          />
        ) : (
          <div>Error: No election selected</div>
        );

      default:
        return renderDashboard();
    }
  };

  const renderDashboard = () => (
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

      {/* Voting Section */}
      <div className="user-details" style={{ marginTop: '30px' }}>
        <h3>🗳️ Voting</h3>

        {!user.mfa_enabled ? (
          <div className="info-item alert-warning">
            <strong>⚠️ 2FA Required for Voting</strong>
            <p style={{ margin: '10px 0 0 0' }}>
              You must enable two-factor authentication before you can vote in elections.
            </p>
          </div>
        ) : (
          <div className="info-item alert-success">
            <strong>✅ Ready to Vote</strong>
            <p style={{ margin: '10px 0 0 0' }}>
              Your account is set up for secure voting.
            </p>
          </div>
        )}

        <button
          onClick={() => setCurrentView('elections')}
          disabled={!user.mfa_enabled}
          style={{
            marginTop: '15px',
            background: user.mfa_enabled ? '#007bff' : '#ccc',
            fontSize: '16px',
            padding: '12px 24px'
          }}
        >
          🗳️ View Available Elections
        </button>
      </div>

      {/* MFA Management Section */}
      <div className="user-details" style={{ marginTop: '30px' }}>
        <h3>🔐 Security Settings</h3>

        {!user.mfa_enabled ? (
          <div>
            <div className="info-item alert-warning">
              <strong>⚠️ Two-Factor Authentication Disabled</strong>
              <p style={{ margin: '10px 0 0 0' }}>
                Enable 2FA to secure your account and participate in elections.
              </p>
            </div>
            <button
              onClick={() => setCurrentView('mfa-setup')}
              style={{ marginTop: '15px', background: '#28a745' }}
            >
              🔒 Enable Two-Factor Authentication
            </button>
          </div>
        ) : (
          <div>
            <div className="info-item alert-success">
              <strong>✅ Two-Factor Authentication Enabled</strong>
              <p style={{ margin: '10px 0 0 0' }}>
                Your account is protected with 2FA.
              </p>
            </div>
            <button
              onClick={() => setCurrentView('mfa-verify')}
              style={{ marginTop: '15px', background: '#007bff' }}
            >
              🔐 Test MFA Verification
            </button>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="user-details" style={{ marginTop: '30px' }}>
        <h3>📋 Quick Actions</h3>

        <div className="button-group">
          <button
            onClick={() => setCurrentView('elections')}
            disabled={!user.mfa_enabled}
            className="btn-primary"
          >
            🗳️ Elections
          </button>

          <button
            onClick={() => setCurrentView('mfa-setup')}
            className="btn-secondary"
          >
            🔒 Security
          </button>
        </div>
      </div>

      {/* Account Security Tips */}
      <div className="user-details" style={{ marginTop: '30px' }}>
        <h3>💡 Security Tips</h3>

        <div className="info-item">
          <ul style={{ paddingLeft: '20px', margin: '0' }}>
            <li>Keep your authenticator app installed and backed up</li>
            <li>Never share your verification codes with anyone</li>
            <li>Use a strong, unique password for your account</li>
            <li>Enable 2FA before participating in any elections</li>
            <li>Your votes are encrypted and anonymous</li>
          </ul>
        </div>
      </div>
    </div>
  );

  return renderCurrentView();
};