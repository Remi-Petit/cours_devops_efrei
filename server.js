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
app.get('/metro-lines', async (req, res) => {
  const client = await pool.connect();
  try {
    const result = await client.query('SELECT * FROM metro_lines');
    res.status(200).json(result.rows);
  } catch (err) {
    console.error('Erreur query:', err);
    res.status(500).json({ error: 'database error' });
  } finally {
    // ⭐ TOUJOURS exécuté, même si erreur!
    client.release();
  }
});

app.get('/pool-status', (req, res) => {
  res.status(200).json({
    totalConnections: pool.totalCount,    // Total connexions créées
    idleConnections: pool.idleCount,      // Connexions disponibles
    waitingClients: pool.waitingCount,    // Clients en attente d'une connexion
  });
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