import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import CharacterListPage from './pages/CharacterListPage';
import CharacterDetailPage from './pages/CharacterDetailPage';
import './App.css';

function AppContent() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsLoggedIn(!!token);
  }, []);

  const handleLogin = () => {
    setIsLoggedIn(true);
    navigate('/')
  };

  const handleLogout = (e) => {
    e.preventDefault();
    localStorage.removeItem('access_token');
    setIsLoggedIn(false);
    navigate('/')
  };

  const navigateToLogin = (e) => {
    e.preventDefault();
    navigate('/login');
  };

  return (
    <>
      <Navbar isLoggedIn={isLoggedIn} onLogin={navigateToLogin} onLogout={handleLogout} />
      <div className="container py-5">
        <Routes>
          <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
          <Route path="/characters/:id" element={<CharacterDetailPage />} />
          <Route path="/characters" element={<CharacterListPage />} />
          <Route path="/" element={
            <div className="startpage-container">
              <h1 className="startpage-title">D&D Companion</h1>
              <p className="startpage-lead">
                Willkommen beim <span className="highlight">Dungeons & Dragons Companion</span>!<br/>
                Dein digitales Nachschlagewerk für Charaktere, Zauber und Gegenstände.<br/>
                <span className="startpage-desc">
                Behalte jederzeit den Überblick über deine Helden, ihre Fähigkeiten und magischen Besitztümer – direkt im Browser und auf Deutsch.
                </span>
              </p>
              <hr className="startpage-divider" />
              <p className="startpage-action">
                <strong>Starte jetzt:</strong> Melde dich an und nutze den Companion als stilvolle Unterstützung für deine nächsten Abenteuer!
              </p>
            </div>
          } />
        </Routes>
      </div>
    </>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;