const express = require('express');
const { Pool } = require('pg');
const app = express();
const PORT = process.env.PORT || 3000;

// Configuration du pool de connexions PostgreSQL
const pool = new Pool({
  // Connexion
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'dernier_metro',
  user: process.env.DB_USER || 'app',
  password: process.env.DB_PASSWORD || 'app',

  // ⭐ CONNECTION POOLING - CRITICAL CONFIG
  max: 20,                      // Maximum 20 connexions (PostgreSQL default = 100)
  min: 2,                       // Minimum 2 connexions toujours ouvertes
  idleTimeoutMillis: 30000,     // Fermer connexion après 30s d'inactivité
  connectionTimeoutMillis: 2000, // Timeout si connexion prend > 2s

  // ⭐ ERROR HANDLING
  allowExitOnIdle: false,        // Ne pas exit si toutes les connexions sont idle
});

// Test de connexion au démarrage
pool.query('SELECT NOW()', (err, res) => {
  if (err) {
    console.error('❌ Erreur de connexion à PostgreSQL:', err);
  } else {
    console.log('✅ Connecté à PostgreSQL à', res.rows[0].now);
  }
});

app.use(express.json());

// Logger
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`${req.method} ${req.path} -> ${res.statusCode} (${duration}ms)`);
  });
  next();
});

// ENDPOINT 1 : Health check (avec test DB)
app.get('/health', async (req, res) => {
  try {
    await pool.query('SELECT 1');
    res.status(200).json({
      status: 'ok',
      service: 'lastmetro-api',
      database: 'connected',
      timestamp: new Date().toISOString()
    });
  } catch (err) {
    res.status(503).json({
      status: 'error',
      service: 'lastmetro-api',
      database: 'disconnected',
      error: err.message
    });
  }
});

// ENDPOINT 2 : Lire la config depuis PostgreSQL
app.get('/config', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM config ORDER BY key');
    res.status(200).json({
      count: result.rows.length,
      data: result.rows
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ENDPOINT 3 : Next metro (avec données de la DB)
app.get('/next-metro', async (req, res) => {
  const station = req.query.station;

  if (!station) {
    return res.status(400).json({ error: 'missing station parameter' });
  }

  try {
    // Récupérer les defaults depuis la DB
    const result = await pool.query(
      "SELECT value FROM config WHERE key = 'metro.defaults'"
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'config not found' });
    }

    const defaults = result.rows[0].value;
    const headwayMin = defaults.headwayMin || 5;

    // Calculer le prochain métro
    const now = new Date();
    const next = new Date(now.getTime() + headwayMin * 60 * 1000);
    const nextTime = `${String(next.getHours()).padStart(2, '0')}:${String(next.getMinutes()).padStart(2, '0')}`;

    res.status(200).json({
      station: station,
      line: defaults.line,
      nextArrival: nextTime,
      headwayMin: headwayMin,
      source: 'database'
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});













// GET /metro-lines - Lister toutes les lignes
app.get('/metro-lines', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT id, name, color, created_at FROM metro_lines ORDER BY id'
    );

    res.status(200).json({
      count: result.rows.length,
      data: result.rows
    });
  } catch (err) {
    console.error('Erreur GET /metro-lines:', err);
    res.status(500).json({ error: 'database error' });
  }
});

// GET /metro-lines/:id - Récupérer une ligne spécifique
app.get('/metro-lines/:id', async (req, res) => {
  const { id } = req.params;

  try {
    const result = await pool.query(
      'SELECT id, name, color, created_at FROM metro_lines WHERE id = $1',
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'ligne non trouvée' });
    }

    res.status(200).json(result.rows[0]);
  } catch (err) {
    console.error('Erreur GET /metro-lines/:id:', err);
    res.status(500).json({ error: 'database error' });
  }
});

// POST /metro-lines - Créer une nouvelle ligne
app.post('/metro-lines', async (req, res) => {
  const { name, color } = req.body;

  // ⭐ Validation des champs requis
  if (!name || !color) {
    return res.status(400).json({
      error: 'champs requis: name, color'
    });
  }

  try {
    const result = await pool.query(
      'INSERT INTO metro_lines (name, color) VALUES ($1, $2) RETURNING *',
      [name, color]
    );

    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error('Erreur POST /metro-lines:', err);
    res.status(500).json({ error: 'database error' });
  }
});

// PUT /metro-lines/:id - Modifier une ligne
app.put('/metro-lines/:id', async (req, res) => {
  const { id } = req.params;
  const { name, color } = req.body;

  if (!name || !color) {
    return res.status(400).json({
      error: 'champs requis: name, color'
    });
  }

  try {
    const result = await pool.query(
      'UPDATE metro_lines SET name = $1, color = $2 WHERE id = $3 RETURNING *',
      [name, color, id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'ligne non trouvée' });
    }

    res.status(200).json(result.rows[0]);
  } catch (err) {
    console.error('Erreur PUT /metro-lines/:id:', err);
    res.status(500).json({ error: 'database error' });
  }
});

// DELETE /metro-lines/:id - Supprimer une ligne
app.delete('/metro-lines/:id', async (req, res) => {
  const { id } = req.params;

  try {
    const result = await pool.query(
      'DELETE FROM metro_lines WHERE id = $1 RETURNING *',
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'ligne non trouvée' });
    }

    // ⭐ Status 204 = Success mais pas de contenu
    res.status(204).send();
  } catch (err) {
    console.error('Erreur DELETE /metro-lines/:id:', err);
    res.status(500).json({ error: 'database error' });
  }
});

// 404
app.use((req, res) => {
  res.status(404).json({ error: 'not found' });
});

// Démarrer
app.listen(PORT, () => {
  console.log(`🚇 Last Metro API sur http://localhost:${PORT}`);
  console.log(`📊 Health: http://localhost:${PORT}/health`);
  console.log(`⚙️  Config: http://localhost:${PORT}/config`);
});

// Cleanup à l'arrêt
process.on('SIGTERM', () => {
  pool.end(() => {
    console.log('Pool PostgreSQL fermé');
    process.exit(0);
  });
});