-- =====================================================
-- FIX: Agregar ON DELETE CASCADE a todas las Foreign Keys
-- Ejecutar en Supabase SQL Editor (https://supabase.com/dashboard → SQL Editor)
-- =====================================================

-- 1. USERS → INSTITUTION
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_inst_id_fkey;
ALTER TABLE users ADD CONSTRAINT users_inst_id_fkey
  FOREIGN KEY (inst_id) REFERENCES institution(id) ON DELETE CASCADE;

-- 2. PROGRAMS → INSTITUTION
ALTER TABLE programs DROP CONSTRAINT IF EXISTS programs_inst_id_fkey;
ALTER TABLE programs ADD CONSTRAINT programs_inst_id_fkey
  FOREIGN KEY (inst_id) REFERENCES institution(id) ON DELETE CASCADE;

-- 3. FACTORS → INSTITUTION
ALTER TABLE factors DROP CONSTRAINT IF EXISTS factors_inst_id_fkey;
ALTER TABLE factors ADD CONSTRAINT factors_inst_id_fkey
  FOREIGN KEY (inst_id) REFERENCES institution(id) ON DELETE CASCADE;

-- 4. FACTORS → PROGRAMS
ALTER TABLE factors DROP CONSTRAINT IF EXISTS factors_program_id_fkey;
ALTER TABLE factors ADD CONSTRAINT factors_program_id_fkey
  FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE;

-- 5. CHARACTERISTICS → FACTORS
ALTER TABLE characteristics DROP CONSTRAINT IF EXISTS characteristics_factor_id_fkey;
ALTER TABLE characteristics ADD CONSTRAINT characteristics_factor_id_fkey
  FOREIGN KEY (factor_id) REFERENCES factors(id) ON DELETE CASCADE;

-- 6. ASPECTS → CHARACTERISTICS
ALTER TABLE aspects DROP CONSTRAINT IF EXISTS aspects_char_id_fkey;
ALTER TABLE aspects ADD CONSTRAINT aspects_char_id_fkey
  FOREIGN KEY (char_id) REFERENCES characteristics(id) ON DELETE CASCADE;

-- 7. EVALUATIONS → INSTITUTION
ALTER TABLE evaluations DROP CONSTRAINT IF EXISTS evaluations_inst_id_fkey;
ALTER TABLE evaluations ADD CONSTRAINT evaluations_inst_id_fkey
  FOREIGN KEY (inst_id) REFERENCES institution(id) ON DELETE CASCADE;

-- 8. EVALUATIONS → PROGRAMS
ALTER TABLE evaluations DROP CONSTRAINT IF EXISTS evaluations_program_id_fkey;
ALTER TABLE evaluations ADD CONSTRAINT evaluations_program_id_fkey
  FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE;

-- 9. EVIDENCES → INSTITUTION
ALTER TABLE evidences DROP CONSTRAINT IF EXISTS evidences_inst_id_fkey;
ALTER TABLE evidences ADD CONSTRAINT evidences_inst_id_fkey
  FOREIGN KEY (inst_id) REFERENCES institution(id) ON DELETE CASCADE;

-- 10. EVIDENCES → PROGRAMS
ALTER TABLE evidences DROP CONSTRAINT IF EXISTS evidences_program_id_fkey;
ALTER TABLE evidences ADD CONSTRAINT evidences_program_id_fkey
  FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE;

-- 11. STATISTICS → INSTITUTION
ALTER TABLE statistics DROP CONSTRAINT IF EXISTS statistics_inst_id_fkey;
ALTER TABLE statistics ADD CONSTRAINT statistics_inst_id_fkey
  FOREIGN KEY (inst_id) REFERENCES institution(id) ON DELETE CASCADE;

-- 12. STATISTICS → PROGRAMS
ALTER TABLE statistics DROP CONSTRAINT IF EXISTS statistics_program_id_fkey;
ALTER TABLE statistics ADD CONSTRAINT statistics_program_id_fkey
  FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE;
