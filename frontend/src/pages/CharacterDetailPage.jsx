import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { fetchCharacterById } from '../services/api';
import './CharacterDetailPage.css';

function CharacterDetailPage() {
  const { id } = useParams();
  const [character, setCharacter] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Nicht eingeloggt!');
      return;
    }
    fetchCharacterById(id, token)
      .then(setCharacter)
      .catch(() => setError('Fehler beim Laden des Charakters.'));
  }, [id]);

  if (error) {
    return <div className="alert alert-danger mt-4">{error}</div>;
  }
  if (!character) {
    return <div className="text-center mt-5">Lade Charakterdaten...</div>;
  }

  return (
    <div className="char-sheet-container">
      <div className="char-sheet">
        <div className="char-header">
          <img
            src={character.image || '/default-avatar.png'}
            alt={character.name}
            className="char-avatar"
          />
          <div>
            <h1 className="char-name">{character.name}</h1>
            <div className="char-class-level">
              {character.gameclass} | Stufe {character.level}
            </div>
          </div>
        </div>
        <hr className="char-divider" />
        <div className="char-section">
          <h2>Attribute</h2>
          {/* Beispiel: Passe an deine Datenstruktur an */}
          <ul className="char-attributes">
            <li><strong>Stärke:</strong> {character.strength || '-'}</li>
            <li><strong>Geschicklichkeit:</strong> {character.dexterity || '-'}</li>
            <li><strong>Konstitution:</strong> {character.constitution || '-'}</li>
            <li><strong>Intelligenz:</strong> {character.intelligence || '-'}</li>
            <li><strong>Weisheit:</strong> {character.wisdom || '-'}</li>
            <li><strong>Charisma:</strong> {character.charisma || '-'}</li>
          </ul>
        </div>
        <div className="char-section">
          <h2>Zauber</h2>
          <ul>
            {character.spells && character.spells.length > 0 ? (
              character.spells.map((spell, i) => (
                <li key={i}>{spell.name_de || spell.name_en}</li>
              ))
            ) : (
              <li>Keine Zauber</li>
            )}
          </ul>
        </div>
        <div className="char-section">
          <h2>Items</h2>
          <ul>
            {character.items && character.items.length > 0 ? (
              character.items.map((item, i) => (
                <li key={i}>{item.name_de || item.name_en}</li>
              ))
            ) : (
              <li>Keine Items</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default CharacterDetailPage;