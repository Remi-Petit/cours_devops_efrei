const request = require('supertest');
const express = require('express');
const { Pool } = require('pg');
require('dotenv').config();

const app = express();
app.use(express.json());

// Setup pool de test
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

// Endpoint de test
app.get('/metro-lines', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM metro_lines ORDER BY id');
    res.status(200).json({ count: result.rows.length, data: result.rows });
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







describe('GET /metro-lines', () => {
  test('retourne la liste des lignes', async () => {
    const response = await request(app).get('/metro-lines');

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('count');
    expect(response.body).toHaveProperty('data');
    expect(Array.isArray(response.body.data)).toBe(true);
  });

  test('chaque ligne a les propriétés requises', async () => {
    const response = await request(app).get('/metro-lines');

    const line = response.body.data[0];
    expect(line).toHaveProperty('id');
    expect(line).toHaveProperty('name');
    expect(line).toHaveProperty('color');
  });
});

describe('POST /metro-lines', () => {
  test('crée une nouvelle ligne', async () => {
    const newLine = {
      name: 'Ligne Test',
      color: 'Bleu',
    };

    const response = await request(app)
      .post('/metro-lines')
      .send(newLine);

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
    expect(response.body.name).toBe('Ligne Test');
  });

  test('rejette une ligne sans nom', async () => {
    const response = await request(app)
      .post('/metro-lines')
      .send({ color: 'Rouge' });

    expect(response.status).toBe(400);
    expect(response.body).toHaveProperty('error');
  });
});

describe('Flow complet CREATE → GET → DELETE', () => {
  test('cycle de vie d\'une ligne', async () => {
    // 1. Créer
    const createResponse = await request(app)
      .post('/metro-lines')
      .send({ name: 'Ligne Flow', color: 'Vert' });

    expect(createResponse.status).toBe(201);
    const lineId = createResponse.body.id;

    // 2. Lire
    const getResponse = await request(app)
      .get(`/metro-lines/${lineId}`);

    expect(getResponse.status).toBe(200);
    expect(getResponse.body.name).toBe('Ligne Flow');

    // 3. Supprimer
    const deleteResponse = await request(app)
      .delete(`/metro-lines/${lineId}`);

    expect(deleteResponse.status).toBe(204);

    // 4. Vérifier suppression
    const getAfterDelete = await request(app)
      .get(`/metro-lines/${lineId}`);

    expect(getAfterDelete.status).toBe(404);
  });
});

// Cleanup après les tests
afterAll(async () => {
  await pool.end();
});

// Export pour les tests
module.exports = { app, pool };