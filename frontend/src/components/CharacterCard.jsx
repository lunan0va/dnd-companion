import './CharacterCard.css';

function CharacterCard({ name, speciesClass, level, image }) {
  return (
    <div className="character-card">
      <div className="character-avatar">
        <img src={image} alt={name} />
      </div>
      <div>
        <div className="character-name">{name}</div>
        <div className="character-class">{speciesClass}</div>
        <div className="character-level">Stufe {level}</div>
      </div>
    </div>
  );
}

export default CharacterCard;
