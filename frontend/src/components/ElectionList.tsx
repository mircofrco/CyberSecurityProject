import React, { useState, useEffect } from 'react';
import type {Election} from '../types';
import { api } from '../api';

interface ElectionListProps {
  token: string;
  onSelectElection: (election: Election) => void;
}

export const ElectionList: React.FC<ElectionListProps> = ({ token, onSelectElection }) => {
  const [elections, setElections] = useState<Election[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadElections();
  }, []);

  const loadElections = async () => {
    try {
      setLoading(true);
      const data = await api.getElections(token);
      setElections(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load elections');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="auth-container">
        <div className="loading">Loading elections...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="auth-container">
        <div className="error">{error}</div>
        <button onClick={loadElections}>Try Again</button>
      </div>
    );
  }

  if (elections.length === 0) {
    return (
      <div className="auth-container">
        <h3>No Elections Available</h3>
        <p>There are currently no active elections.</p>
        <button onClick={loadElections}>Refresh</button>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <h3>Available Elections</h3>

      <div className="elections-list">
        {elections.map((election) => (
          <div key={election.id} className="election-card">
            <div className="election-header">
              <h4>{election.title}</h4>
              <span className={`election-status ${election.is_voting_open ? 'open' : 'closed'}`}>
                {election.is_voting_open ? '🟢 Voting Open' : '🔴 Voting Closed'}
              </span>
            </div>

            {election.description && (
              <p className="election-description">{election.description}</p>
            )}

            <div className="election-details">
              <div className="election-timing">
                <strong>Voting Period:</strong><br />
                <small>
                  {formatDate(election.start_date)} - {formatDate(election.end_date)}
                </small>
              </div>

              <div className="candidates-count">
                <strong>Candidates:</strong> {election.candidates.length}
              </div>
            </div>

            <div className="election-actions">
              <button
                onClick={() => onSelectElection(election)}
                disabled={!election.is_voting_open}
                className={election.is_voting_open ? 'btn-primary' : 'btn-secondary'}
              >
                {election.is_voting_open ? 'Vote Now' : 'View Details'}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <button onClick={loadElections} className="btn-secondary">
          🔄 Refresh Elections
        </button>
      </div>
    </div>
  );
};