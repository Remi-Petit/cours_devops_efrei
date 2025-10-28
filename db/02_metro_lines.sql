-- Table pour les lignes de métro
CREATE TABLE IF NOT EXISTS public.metro_lines (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  color VARCHAR(30) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Données de test
INSERT INTO public.metro_lines (name, color) VALUES
  ('Ligne 1', 'Jaune'),
  ('Ligne 4', 'Violet'),
  ('Ligne 14', 'Bleu')
ON CONFLICT DO NOTHING;