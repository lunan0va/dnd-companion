import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

function Navbar({ isLoggedIn, onLogin, onLogout }) {
  return (
    <nav className="navbar navbar-expand-lg sticky-top">
      <div className="container-fluid">
        <Link className="navbar-brand" to="/">D&D Companion</Link>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav ms-auto">
            {isLoggedIn && (
              <li className="nav-item">
                <Link className="nav-link" to="/characters">Charaktere</Link>
              </li>
            )}
            {!isLoggedIn ? (
              <li className="nav-item">
                <a className="nav-link" href="#" onClick={onLogin}>Login</a>
              </li>
            ) : (
              <li className="nav-item">
                <a className="nav-link" href="#" onClick={onLogout}>Logout</a>
              </li>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default Navbar; 