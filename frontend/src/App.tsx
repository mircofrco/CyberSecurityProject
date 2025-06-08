import { useState, useEffect } from 'react';
import { Login } from './components/Login';
import { Register } from './components/Register';
import { UserInfo } from './components/UserInfo';
import { api } from './api';
import type {User} from './types';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [showLogin, setShowLogin] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Check for existing token on app load
  useEffect(() => {
    const savedToken = localStorage.getItem('securevote_token');
    if (savedToken) {
      validateToken(savedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const validateToken = async (token: string) => {
    try {
      const userData = await api.getCurrentUser(token);
      setUser(userData);
      setToken(token);
      setIsAuthenticated(true);
    } catch (err) {
      localStorage.removeItem('securevote_token');
      setError('Session expired. Please login again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (token: string) => {
    localStorage.setItem('securevote_token', token);
    await validateToken(token);
  };

  const handleLogout = () => {
    localStorage.removeItem('securevote_token');
    setIsAuthenticated(false);
    setUser(null);
    setToken(null);
    setShowLogin(true);
    setError('');
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="container">
      <header>
        <h1>SecureVote</h1>
        <p>Cryptographically Secure Voting System</p>
      </header>

      {error && <div className="error">{error}</div>}

      {isAuthenticated && user ? (
        <UserInfo user={user} onLogout={handleLogout} />
      ) : (
        <>
          {showLogin ? (
            <Login
              onLogin={handleLogin}
              onSwitchToRegister={() => setShowLogin(false)}
            />
          ) : (
            <Register
              onSwitchToLogin={() => setShowLogin(true)}
            />
          )}
        </>
      )}
    </div>
  );
}

export default App;