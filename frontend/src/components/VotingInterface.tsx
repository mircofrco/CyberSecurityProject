import React, { useState, useEffect } from 'react';
import type {Election, Candidate, VoterStatus} from '../types';
import { api } from '../api';

interface VotingInterfaceProps {
  election: Election;
  token: string;
  onBack: () => void;
  onVoteSuccess: () => void;
}

export const VotingInterface: React.FC<VotingInterfaceProps> = ({
  election,
  token,
  onBack,
  onVoteSuccess
}) => {
  const [voterStatus, setVoterStatus] = useState<VoterStatus | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<string>('');
  const [mfaCode, setMfaCode] = useState<string>('');
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  useEffect(() => {
    checkVoterStatus();
  }, []);

  const checkVoterStatus = async () => {
    try {
      setLoading(true);
      const status = await api.getVoterStatus(token, election.id);
      setVoterStatus(status);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to check voter status');
    } finally {
      setLoading(false);
    }
  };

  const handleCandidateSelect = (candidateId: string) => {
    setSelectedCandidate(candidateId);
    setError('');
  };

  const handleProceedToConfirmation = () => {
    if (!selectedCandidate) {
      setError('Please select a candidate');
      return;
    }
    setShowConfirmation(true);
  };

  const handleConfirmVote = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!mfaCode || mfaCode.length !== 6) {
      setError('Please enter a valid 6-digit MFA code');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await api.castVote(token, election.id, selectedCandidate, mfaCode);
      setSuccess(result.message);
      setTimeout(() => {
        onVoteSuccess();
      }, 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cast vote');
    } finally {
      setLoading(false);
    }
  };

  const getSelectedCandidateName = () => {
    const candidate = election.candidates.find(c => c.id === selectedCandidate);
    return candidate ? candidate.name : '';
  };

  if (loading && !voterStatus) {
    return (
      <div className="auth-container">
        <div className="loading">Checking voter eligibility...</div>
      </div>
    );
  }

  if (voterStatus && !voterStatus.can_vote) {
    return (
      <div className="auth-container">
        <h3>{election.title}</h3>
        <div className="error">{voterStatus.message}</div>
        <button onClick={onBack}>← Back to Elections</button>
      </div>
    );
  }

  if (success) {
    return (
      <div className="auth-container">
        <h3>Vote Cast Successfully! 🗳️</h3>
        <div className="success">{success}</div>
        <p>Thank you for participating in this election. Your vote has been securely recorded.</p>
        <button onClick={onBack}>← Back to Elections</button>
      </div>
    );
  }

  if (showConfirmation) {
    return (
      <div className="auth-container">
        <h3>Confirm Your Vote</h3>

        <div className="vote-confirmation">
          <div className="info-item">
            <strong>Election:</strong> {election.title}
          </div>
          <div className="info-item">
            <strong>Your Selection:</strong> {getSelectedCandidateName()}
          </div>
        </div>

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleConfirmVote}>
          <div className="form-group">
            <label>Enter your 2FA code to confirm your vote:</label>
            <input
              type="text"
              value={mfaCode}
              onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="000000"
              maxLength={6}
              required
              disabled={loading}
              className="mfa-code-input"
            />
            <small>Enter the 6-digit code from your authenticator app</small>
          </div>

          <div className="button-group">
            <button type="submit" disabled={loading || mfaCode.length !== 6}>
              {loading ? 'Casting Vote...' : '✅ Confirm Vote'}
            </button>
            <button
              type="button"
              onClick={() => setShowConfirmation(false)}
              className="btn-secondary"
            >
              ← Back to Candidates
            </button>
          </div>
        </form>

        <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
          <p><strong>⚠️ Important:</strong> Once you confirm your vote, it cannot be changed.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="election-header">
        <h3>{election.title}</h3>
        <button onClick={onBack} className="btn-secondary">← Back</button>
      </div>

      {election.description && (
        <p className="election-description">{election.description}</p>
      )}

      {error && <div className="error">{error}</div>}

      <div className="candidates-section">
        <h4>Select a Candidate:</h4>

        <div className="candidates-list">
          {election.candidates.map((candidate) => (
            <div
              key={candidate.id}
              className={`candidate-card ${selectedCandidate === candidate.id ? 'selected' : ''}`}
              onClick={() => handleCandidateSelect(candidate.id)}
            >
              <div className="candidate-header">
                <input
                  type="radio"
                  name="candidate"
                  value={candidate.id}
                  checked={selectedCandidate === candidate.id}
                  onChange={() => handleCandidateSelect(candidate.id)}
                />
                <h5>{candidate.name}</h5>
              </div>

              {candidate.party && (
                <div className="candidate-party">{candidate.party}</div>
              )}

              {candidate.description && (
                <p className="candidate-description">{candidate.description}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="voting-actions">
        <button
          onClick={handleProceedToConfirmation}
          disabled={!selectedCandidate}
          className="btn-primary"
        >
          Proceed to Vote Confirmation →
        </button>
      </div>

      <div className="voting-info">
        <h4>Important Information:</h4>
        <ul>
          <li>You can only vote once in this election</li>
          <li>You will need to enter your 2FA code to confirm your vote</li>
          <li>Your vote is encrypted and anonymous</li>
          <li>Once cast, your vote cannot be changed</li>
        </ul>
      </div>
    </div>
  );
};