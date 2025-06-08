import type {User, LoginResponse, RegisterData, LoginData} from './types';

const API_BASE = 'http://127.0.0.1:8000';

export const api = {
  async register(data: RegisterData): Promise<User> {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  },

  async login(data: LoginData): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE}/auth/jwt/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${encodeURIComponent(data.email)}&password=${encodeURIComponent(data.password)}`,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  },

  async getCurrentUser(token: string): Promise<User> {
    const response = await fetch(`${API_BASE}/auth/users/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get user info');
    }

    return response.json();
  },

  // MFA Functions
  async setupMFA(token: string): Promise<{ otpauth_url: string; qr: string }> {
    const response = await fetch(`${API_BASE}/mfa/setup`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'MFA setup failed');
    }

    return response.json();
  },

  async verifyMFA(token: string, code: string): Promise<{ detail: string }> {
    const response = await fetch(`${API_BASE}/mfa/verify`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'MFA verification failed');
    }

    return response.json();
  },

  // Voting Functions
  async getElections(token: string): Promise<Election[]> {
    const response = await fetch(`${API_BASE}/voting/elections`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch elections');
    }

    return response.json();
  },

  async getVoterStatus(token: string, electionId: string): Promise<VoterStatus> {
    const response = await fetch(`${API_BASE}/voting/elections/${electionId}/status`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to check voter status');
    }

    return response.json();
  },

  async castVote(token: string, electionId: string, candidateId: string, mfaCode: string): Promise<VoteResponse> {
    const response = await fetch(`${API_BASE}/voting/elections/${electionId}/vote`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        candidate_id: candidateId,
        mfa_code: mfaCode,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to cast vote');
    }

    return response.json();
  },

  async getElectionResults(token: string, electionId: string): Promise<ElectionResults> {
    const response = await fetch(`${API_BASE}/voting/elections/${electionId}/results`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch election results');
    }

    return response.json();
  },
};