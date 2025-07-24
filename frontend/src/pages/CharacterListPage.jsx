import React, { useEffect, useState } from 'react';
import { fetchCharacters } from '../services/api';
import CharacterCard from '../components/CharacterCard';
import './CharacterListPage.css';
import { useNavigate } from 'react-router-dom';

function CharacterListPage() {
  const [characters, setCharacters] = useState([]);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Nicht eingeloggt!');
      return;
    }
    fetchCharacters(token)
      .then(setCharacters)
      .catch(() => setError('Fehler beim Laden der Charaktere.'));
  }, []);

  if (error) {
    return <div className="alert alert-danger mt-4">{error}</div>;
  }

  return (
    <div>
      <h2 className="dashboard-title">CHARAKTERÜBERSICHT</h2>
      <div className="row">
        {characters.map(char => (
          <div
            className="col-md-6 col-lg-4"
            key={char.id}
            style={{ cursor: 'pointer' }}
            onClick={() => navigate(`/characters/${char.id}`)}
          >
            <CharacterCard
              name={char.name}
              speciesClass={`${char.species  || ''} ${char.gameclass}`}
              level={char.level}
              image={char.image || '/default-avatar.png'}
            />
          </div>
        ))}
      </div>
      <div className="row mt-4">
        <div className="col text-center">
          <button className="btn-new-character">+ NEUER CHARAKTER</button>
        </div>
      </div>
    </div>
  );
}

export default CharacterListPage;
