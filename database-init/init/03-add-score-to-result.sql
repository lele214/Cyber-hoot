-- Migration pour ajouter le champ score à la table RESULT
-- Ce fichier ajoute la colonne score pour stocker les résultats des quiz

USE `cyberhoot`;

-- Ajouter la colonne score à la table RESULT
ALTER TABLE `RESULT`
ADD COLUMN `score` INT NULL COMMENT 'Score obtenu par l\'utilisateur pour ce quiz' AFTER `date`,
ADD COLUMN `totalQuestions` INT NULL COMMENT 'Nombre total de questions dans le quiz' AFTER `score`;

-- Mettre à jour les données existantes avec des scores de test
UPDATE `RESULT` SET `score` = 8, `totalQuestions` = 10 WHERE `idRESULT` = 1;
UPDATE `RESULT` SET `score` = 6, `totalQuestions` = 10 WHERE `idRESULT` = 2;
UPDATE `RESULT` SET `score` = 9, `totalQuestions` = 10 WHERE `idRESULT` = 3;
UPDATE `RESULT` SET `score` = 7, `totalQuestions` = 10 WHERE `idRESULT` = 4;
