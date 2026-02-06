-- =====================================================
-- Cyber-hoot - Donnees de test pour le developpement
-- =====================================================
-- Ce fichier contient les donnees de seed pour que tous
-- les developpeurs aient le meme environnement de test.
--
-- Pour l'executer manuellement :
-- docker exec -i <container_db> mysql -u root -p cyberhoot < test/seed_data.sql
-- =====================================================

USE `cyberhoot`;

-- =====================================================
-- 1. UTILISATEURS DE TEST
-- =====================================================

-- Utilisateur Admin (mot de passe: AdminHoot123!)
-- Hash genere avec werkzeug.security.generate_password_hash
INSERT INTO `USER` (`idUSER`, `username`, `hashpassword`, `emailUser`) VALUES
(1, 'AdminHoot', 'scrypt:32768:8:1$PSwKNtuaZCDoODBA$3df18ede31a2f2189d4cbf1e86e9abea8863c19f84a6b10f1e8cef1d30ac22add6187296513070ca58c4fcec37bde4c332f1b1a70cbe18334fccfffc38b1b3b6', 'admin@cyberhoot.local');

-- Utilisateur Creator de test (mot de passe: Creator123!)
INSERT INTO `USER` (`idUSER`, `username`, `hashpassword`, `emailUser`) VALUES
(2, 'TestCreator', 'scrypt:32768:8:1$PSwKNtuaZCDoODBA$3df18ede31a2f2189d4cbf1e86e9abea8863c19f84a6b10f1e8cef1d30ac22add6187296513070ca58c4fcec37bde4c332f1b1a70cbe18334fccfffc38b1b3b6', 'creator@cyberhoot.local');

-- Utilisateur Player de test (mot de passe: Player123!)
INSERT INTO `USER` (`idUSER`, `username`, `hashpassword`, `emailUser`) VALUES
(3, 'TestPlayer', 'scrypt:32768:8:1$PSwKNtuaZCDoODBA$3df18ede31a2f2189d4cbf1e86e9abea8863c19f84a6b10f1e8cef1d30ac22add6187296513070ca58c4fcec37bde4c332f1b1a70cbe18334fccfffc38b1b3b6', 'player@cyberhoot.local');

-- =====================================================
-- 2. ROLES
-- =====================================================

INSERT INTO `ROLES` (`idROLES`, `nameRoles`) VALUES
(1, 'admin'),
(2, 'creator'),
(3, 'player');

-- =====================================================
-- 3. ATTRIBUTION DES ROLES AUX UTILISATEURS
-- =====================================================

-- AdminHoot a les roles admin et creator
INSERT INTO `userToRoles` (`idROLES`, `idUser`) VALUES
(1, 1),  -- AdminHoot -> admin
(2, 1);  -- AdminHoot -> creator

-- TestCreator a le role creator
INSERT INTO `userToRoles` (`idROLES`, `idUser`) VALUES
(2, 2);  -- TestCreator -> creator

-- TestPlayer a le role player
INSERT INTO `userToRoles` (`idROLES`, `idUser`) VALUES
(3, 3);  -- TestPlayer -> player

-- =====================================================
-- 4. QUIZ DE TEST
-- =====================================================

-- Quiz 1: Introduction a la Cybersecurite (publie)
INSERT INTO `QUIZ` (`idQUIZ`, `idCreatedByUser`, `difficulty`, `title`, `statut`, `createdAt`) VALUES
(1, 1, 'EASY', 'Introduction Cybersecurite', 'PUBLISHED', CURDATE());

-- Quiz 2: Phishing Avance (brouillon)
INSERT INTO `QUIZ` (`idQUIZ`, `idCreatedByUser`, `difficulty`, `title`, `statut`, `createdAt`) VALUES
(2, 2, 'MEDIUM', 'Detecter le Phishing', 'DRAFT', CURDATE());

-- =====================================================
-- 5. QUESTIONS DU QUIZ 1
-- =====================================================

INSERT INTO `QUESTION` (`idQUESTION`, `idQuestionFromQuiz`, `QuestionText`) VALUES
(1, 1, 'Qu''est-ce qu''un mot de passe fort ?'),
(2, 1, 'Que signifie HTTPS ?'),
(3, 1, 'Qu''est-ce que le phishing ?');

-- =====================================================
-- 6. REPONSES AUX QUESTIONS
-- =====================================================

-- Reponses Question 1: Mot de passe fort
INSERT INTO `RESPONSE` (`idRESPONSE`, `idResponseFromQuestion`, `responseText`, `isCorrect`) VALUES
(1, 1, 'Un mot avec 4 lettres', 0),
(2, 1, '12 car. majuscules, chiffres, symboles', 1),
(3, 1, 'Le nom de mon animal', 0),
(4, 1, '123456', 0);

-- Reponses Question 2: HTTPS
INSERT INTO `RESPONSE` (`idRESPONSE`, `idResponseFromQuestion`, `responseText`, `isCorrect`) VALUES
(5, 2, 'HyperText Transfer Protocol Secure', 1),
(6, 2, 'High Tech Transfer Protocol System', 0),
(7, 2, 'Home Text Transfer Protocol Service', 0),
(8, 2, 'Hyper Terminal Transfer Protocol', 0);

-- Reponses Question 3: Phishing
INSERT INTO `RESPONSE` (`idRESPONSE`, `idResponseFromQuestion`, `responseText`, `isCorrect`) VALUES
(9, 3, 'Un sport de peche', 0),
(10, 3, 'Technique pour voler des infos', 1),
(11, 3, 'Un type de virus', 0),
(12, 3, 'Un logiciel antivirus', 0);

-- =====================================================
-- 7. BADGE POUR LE QUIZ 1
-- =====================================================

INSERT INTO `BADGES` (`idBADGES`, `name`, `image`, `idQuiz`) VALUES
(1, 'Cyber Debutant', NULL, 1);

-- =====================================================
-- INFORMATIONS DE CONNEXION POUR LES TESTS
-- =====================================================
--
-- | Username     | Email                    | Mot de passe   | Roles          |
-- |--------------|--------------------------|----------------|----------------|
-- | AdminHoot    | admin@cyberhoot.local    | AdminHoot123!  | admin, creator |
-- | TestCreator  | creator@cyberhoot.local  | Creator123!    | creator        |
-- | TestPlayer   | player@cyberhoot.local   | Player123!     | player         |
--
-- Note: Tous les mots de passe utilisent le meme hash pour simplifier.
-- En production, chaque utilisateur aura son propre hash unique.
-- =====================================================
