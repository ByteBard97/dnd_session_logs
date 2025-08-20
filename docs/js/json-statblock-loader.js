// JSON Statblock Loader
// Converts JSON statblock format to our statblock generator format

async function loadJsonStatblock(jsonPath, targetElementId) {
  try {
    const response = await fetch(jsonPath);
    if (!response.ok) {
      throw new Error(`Failed to load JSON: ${response.status}`);
    }
    
    const jsonData = await response.json();
    const statblockData = convertJsonToStatblock(jsonData);
    
    if (typeof createStatblock !== 'undefined' && typeof ability !== 'undefined') {
      document.getElementById(targetElementId).innerHTML = createStatblock(statblockData);
    } else {
      console.error('Statblock generator functions not loaded');
    }
  } catch (error) {
    console.error('Error loading JSON statblock:', error);
    document.getElementById(targetElementId).innerHTML = `<p style="color: red;">Failed to load statblock: ${error.message}</p>`;
  }
}

function convertJsonToStatblock(jsonData) {
  // Convert JSON format to our statblock format
  const data = {
    name: jsonData.name,
    size: jsonData.size,
    type: jsonData.type,
    alignment: null,  // Always hide alignment for NPCs
    ac: formatAC(jsonData.ac),
    hp: formatHP(jsonData.hp),
    speed: jsonData.speed,
    abilities: {
      str: ability(jsonData.abilities.str),
      dex: ability(jsonData.abilities.dex),
      con: ability(jsonData.abilities.con),
      int: ability(jsonData.abilities.int),
      wis: ability(jsonData.abilities.wis),
      cha: ability(jsonData.abilities.cha)
    }
  };

  // Add optional fields if they exist
  if (jsonData.saves) {
    data.saves = formatSaves(jsonData.saves);
  }
  
  if (jsonData.skills) {
    data.skills = formatSkills(jsonData.skills);
  }
  
  if (jsonData.senses) {
    data.senses = jsonData.senses;
  }
  
  if (jsonData.languages) {
    data.languages = jsonData.languages;
  }
  
  // Calculate CR based on level or use a default
  data.challenge = calculateChallenge(jsonData);
  
  // Convert traits
  if (jsonData.traits && jsonData.traits.length > 0) {
    data.traits = jsonData.traits.map(trait => ({
      name: trait.name,
      description: trait.desc || trait.description
    }));
  }
  
  // Convert actions
  if (jsonData.actions && jsonData.actions.length > 0) {
    data.actions = jsonData.actions.map(action => ({
      name: action.name,
      description: formatAction(action)
    }));
  }
  
  // Add bonus actions if they exist
  if (jsonData.bonus_actions && jsonData.bonus_actions.length > 0) {
    if (!data.actions) data.actions = [];
    data.actions.push({
      name: "Bonus Actions",
      description: jsonData.bonus_actions.map(ba => `<strong>${ba.name}.</strong> ${ba.desc}`).join('<br><br>')
    });
  }
  
  // Add reactions if they exist
  if (jsonData.reactions && jsonData.reactions.length > 0) {
    if (!data.actions) data.actions = [];
    data.actions.push({
      name: "Reactions", 
      description: jsonData.reactions.map(reaction => `<strong>${reaction.name}.</strong> ${reaction.desc}`).join('<br><br>')
    });
  }

  return data;
}

function formatAC(ac) {
  if (typeof ac === 'object') {
    return ac.notes ? `${ac.value} (${ac.notes})` : ac.value.toString();
  }
  return ac.toString();
}

function formatHP(hp) {
  if (typeof hp === 'object') {
    return hp.formula ? `${hp.average} (${hp.formula})` : hp.average.toString();
  }
  return hp.toString();
}

function formatSaves(saves) {
  return Object.entries(saves)
    .map(([stat, bonus]) => `${stat.charAt(0).toUpperCase() + stat.slice(1)} ${bonus}`)
    .join(', ');
}

function formatSkills(skills) {
  return Object.entries(skills)
    .map(([skill, bonus]) => `${skill.charAt(0).toUpperCase() + skill.slice(1).replace('_', ' ')} ${bonus}`)
    .join(', ');
}

function calculateChallenge(jsonData) {
  // Simple CR calculation based on caster level or default
  if (jsonData.caster_level) {
    const cr = Math.max(1, Math.floor(jsonData.caster_level / 2));
    const xp = [0, 200, 450, 700, 1100, 1800, 2300, 2900, 3900, 5000, 5900][cr] || 5900;
    return `${cr} (${xp.toLocaleString()} XP)`;
  }
  return "5 (1,800 XP)"; // Default
}

function formatAction(action) {
  if (action.attack) {
    const attack = action.attack;
    let desc = `<i>${attack.type} Attack:</i> ${attack.tohit} to hit, `;
    
    if (attack.reach) {
      desc += `reach ${attack.reach}, `;
    }
    if (attack.range) {
      desc += `range ${attack.range}, `;
    }
    
    desc += `${attack.target}. <i>Hit:</i> ${attack.dmg1} ${attack.type1} damage`;
    
    if (attack.dmg2) {
      desc += ` plus ${attack.dmg2} ${attack.type2} damage`;
    }
    
    desc += '.';
    
    if (action.desc) {
      desc += ` ${action.desc}`;
    }
    
    return desc;
  }
  
  return action.desc || action.description || '';
}