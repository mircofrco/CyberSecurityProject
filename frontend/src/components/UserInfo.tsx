import React from 'react';
import type {User} from '../types';

interface UserInfoProps {
  user: User;
  onLogout: () => void;
}

export const UserInfo: React.FC<UserInfoProps> = ({ user, onLogout }) => {
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
    </div>
  );
};