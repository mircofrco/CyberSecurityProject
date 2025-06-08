export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  mfa_enabled: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterData {
  email: string;
  password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

// Voting Types
export interface Candidate {
  id: string;
  name: string;
  description?: string;
  party?: string;
}

export interface Election {
  id: string;
  title: string;
  description?: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
  is_voting_open: boolean;
  candidates: Candidate[];
}

export interface VoterStatus {
  can_vote: boolean;
  has_voted: boolean;
  message: string;
}

export interface VoteResponse {
  success: boolean;
  message: string;
  vote_id?: string;
}

export interface ElectionResults {
  election: Election;
  total_votes: number;
  results: Array<{
    candidate: Candidate;
    votes: number;
    percentage: number;
  }>;
  voter_turnout: {
    eligible: number;
    voted: number;
    percentage: number;
  };
}