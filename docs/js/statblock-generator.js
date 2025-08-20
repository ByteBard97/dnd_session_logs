// D&D 5e Statblock Generator
function createStatblock(data) {
  return `
<div class="stat-block">
  <hr class="orange-border" />
  <div class="creature-heading">
    <h1>${data.name}</h1>
    <h2>${data.size} ${data.type}${data.alignment ? ', ' + data.alignment : ''}</h2>
  </div>
  
  <svg height="5" width="100%" class="tapered-rule">
    <polyline points="0,0 400,2.5 0,5"></polyline>
  </svg>
  
  <div class="top-stats">
    <div class="property-line first">
      <h4>Armor Class</h4>
      <p>${data.ac}</p>
    </div>
    
    <div class="property-line">
      <h4>Hit Points</h4>
      <p>${data.hp}</p>
    </div>
    
    <div class="property-line last">
      <h4>Speed</h4>
      <p>${data.speed}</p>
    </div>
    
    <svg height="5" width="100%" class="tapered-rule">
      <polyline points="0,0 400,2.5 0,5"></polyline>
    </svg>
    
    <div class="abilities">
      <div class="ability-strength">
        <h4>STR</h4>
        <p>${data.abilities.str.score} (${data.abilities.str.modifier >= 0 ? '+' : ''}${data.abilities.str.modifier})</p>
      </div>
      
      <div class="ability-dexterity">
        <h4>DEX</h4>
        <p>${data.abilities.dex.score} (${data.abilities.dex.modifier >= 0 ? '+' : ''}${data.abilities.dex.modifier})</p>
      </div>
      
      <div class="ability-constitution">
        <h4>CON</h4>
        <p>${data.abilities.con.score} (${data.abilities.con.modifier >= 0 ? '+' : ''}${data.abilities.con.modifier})</p>
      </div>
      
      <div class="ability-intelligence">
        <h4>INT</h4>
        <p>${data.abilities.int.score} (${data.abilities.int.modifier >= 0 ? '+' : ''}${data.abilities.int.modifier})</p>
      </div>
      
      <div class="ability-wisdom">
        <h4>WIS</h4>
        <p>${data.abilities.wis.score} (${data.abilities.wis.modifier >= 0 ? '+' : ''}${data.abilities.wis.modifier})</p>
      </div>
      
      <div class="ability-charisma">
        <h4>CHA</h4>
        <p>${data.abilities.cha.score} (${data.abilities.cha.modifier >= 0 ? '+' : ''}${data.abilities.cha.modifier})</p>
      </div>
    </div>
    
    <svg height="5" width="100%" class="tapered-rule">
      <polyline points="0,0 400,2.5 0,5"></polyline>
    </svg>
    
    ${data.saves ? `<div class="property-line first">
      <h4>Saving Throws</h4>
      <p>${data.saves}</p>
    </div>` : ''}
    
    ${data.skills ? `<div class="property-line ${data.saves ? '' : 'first'}">
      <h4>Skills</h4>
      <p>${data.skills}</p>
    </div>` : ''}
    
    ${data.senses ? `<div class="property-line ${!data.saves && !data.skills ? 'first' : ''}">
      <h4>Senses</h4>
      <p>${data.senses}</p>
    </div>` : ''}
    
    ${data.languages ? `<div class="property-line ${!data.saves && !data.skills && !data.senses ? 'first' : ''}">
      <h4>Languages</h4>
      <p>${data.languages}</p>
    </div>` : ''}
    
    <div class="property-line last">
      <h4>Challenge</h4>
      <p>${data.challenge}</p>
    </div>
  </div>
  
  <svg height="5" width="100%" class="tapered-rule">
    <polyline points="0,0 400,2.5 0,5"></polyline>
  </svg>
  
  ${data.traits ? data.traits.map(trait => `
  <div class="property-block">
    <h4>${trait.name}.</h4>
    <p>${trait.description}</p>
  </div>`).join('') : ''}
  
  ${data.actions ? `
  <div class="actions">
    <h3>Actions</h3>
    ${data.actions.map(action => `
    <div class="property-block">
      <h4>${action.name}.</h4>
      <p>${action.description}</p>
    </div>`).join('')}
  </div>` : ''}
  
  <hr class="orange-border bottom" />
</div>`;
}

// Helper function to calculate ability modifier
function calculateModifier(score) {
  return Math.floor((score - 10) / 2);
}

// Helper function to create ability object
function ability(score) {
  return {
    score: score,
    modifier: calculateModifier(score)
  };
}