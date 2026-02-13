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

-- Utilisateur Admin (mot de passe: Adm!nP@ss450)
-- Hash genere avec werkzeug.security.generate_password_hash
INSERT INTO `USER` (`idUSER`, `username`, `hashpassword`, `emailUser`) VALUES
(1, 'AdminHoot', 'scrypt:32768:8:1$e8xXe38o4ynAEbwc$0b05bf85a8b2fb865f946956e9b411309505e38cf42503b5791dd74d37e77444140c567d384622a835268f7cf15acd979876941dbaf97904a0ef9a012f7b23f3', 'admin@cyberhoot.local');

-- Utilisateur Creator de test (mot de passe: testCre@t0r!)
INSERT INTO `USER` (`idUSER`, `username`, `hashpassword`, `emailUser`) VALUES
(2, 'TestCreator', 'scrypt:32768:8:1$vtc9D78a21LAyvWJ$4f168ada7caf674a61d5248f4e8066fd4e09cea1d871b3beef4383dbe31f0fcce0c979c205df776e8c9d7f848bba1f7a354b049ccd0eba0985409f5bc14f280c', 'creator@cyberhoot.local');

-- Utilisateur Player de test (mot de passe: Player123!)
INSERT INTO `USER` (`idUSER`, `username`, `hashpassword`, `emailUser`) VALUES
(3, 'TestPlayer', 'scrypt:32768:8:1$gjvLcW0Rdr1X4o7x$f85dfc6d3185cd563d57c1913fdc9e7288b933cfb61652732c0874b58abfe2c9e41fe6df480a78c09a40d6fb0f6a39df0823e326e91496b76bb981cf6a5dbb16', 'player@cyberhoot.local');

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
-- 7. QUIZ 3 : Ingenierie sociale (recupere depuis quiz1.html)
-- =====================================================

INSERT INTO `QUIZ` (`idQUIZ`, `idCreatedByUser`, `difficulty`, `title`, `statut`, `category`, `createdAt`) VALUES
(3, 1, 'EASY', 'Ingenierie sociale : comment s''en proteger ?', 'PUBLISHED', 'INGENIERIE_SOCIALE', CURDATE());

-- =====================================================
-- 8. QUESTIONS DU QUIZ 3
-- =====================================================

INSERT INTO `QUESTION` (`idQUESTION`, `idQuestionFromQuiz`, `QuestionText`) VALUES
(4, 3, 'Qu''est-ce que l''ingenierie sociale ?'),
(5, 3, 'Qu''est-ce que le phishing ?'),
(6, 3, 'Vous recevez un e-mail urgent de votre "banque" vous demandant de confirmer votre mot de passe. Que devez-vous faire ?'),
(7, 3, 'Qu''est-ce que le "vishing" ?'),
(8, 3, 'Quelle technique les pirates utilisent-ils pour creer un sentiment d''urgence ?'),
(9, 3, 'Qu''est-ce que le "smishing" ?'),
(10, 3, 'Comment reconnaitre un e-mail de phishing ?'),
(11, 3, 'Quelle est la meilleure protection contre l''ingenierie sociale ?'),
(12, 3, 'Un inconnu vous appelle en se presentant comme un technicien de votre service informatique et vous demande votre mot de passe. Que faites-vous ?'),
(13, 3, 'Qu''est-ce que l''authentification multifacteur (MFA) ?');

-- =====================================================
-- 9. REPONSES DU QUIZ 3
-- =====================================================

-- Q4: Qu'est-ce que l'ingenierie sociale ?
INSERT INTO `RESPONSE` (`idRESPONSE`, `idResponseFromQuestion`, `responseText`, `isCorrect`) VALUES
(13, 4, 'Une technique qui exploite les failles techniques des ordinateurs', 0),
(14, 4, 'Une methode qui manipule les personnes pour obtenir des informations confidentielles', 1),
(15, 4, 'Un logiciel antivirus pour proteger les reseaux sociaux', 0),
(16, 4, 'Une formation pour ameliorer les competences sociales', 0);

-- Q5: Qu'est-ce que le phishing ?
INSERT INTO `RESPONSE` (`idRESPONSE`, `idResponseFromQuestion`, `responseText`, `isCorrect`) VALUES
(17, 5, 'Un sport nautique tres populaire', 0),
(18, 5, 'Une technique pour tromper les gens via de faux e-mails ou sites web', 1),
(19, 5, 'Un outil de recherche sur internet', 0),
(20, 5, 'Un nouveau type de reseau social', 0);

-- Q6: E-mail urgent de la banque
INSERT INTO `RESPONSE` (`idRESPONSE`, `idResponseFromQuestion`, `responseText`, `isCorrect`) VALUES
(21, 6, 'Repondre immediatement avec votre mot de passe', 0),
(22, 6, 'Cliquer sur le lien dans l''e-mail', 0),
(23, 6, 'Supprimer l''e-mail et contacter votre banque par un canal officiel', 1),
(24, 6, 'Transferer l''e-mail a tous vos collegues', 0);

-- Q7: Qu'est-ce que le vishing ?
INSERT INTO `RESPONSE` (`idRESPONSE`, `idResponseFromQuestion`, `responseText`, `isCorrect`) VALUES
(25, 7, 'Du phishing par telephone (appels vocaux)', 1),
(26, 7, 'Un nouveau type de virus informatique', 0),
(27, 7, 'Une application de messagerie securisee', 0),
(28, 7, 'Un jeu video en ligne', 0);

-- Q8: Technique pour creer un sentiment d'urgence
INSERT INTO `RESPONSE` (`idRESPONSE`, `idResponseFromQuestion`, `responseText`, `isCorrect`) VALUES
(29, 8, 'Envoyer des messages amicaux et polis', 0),
(30, 8, 'Menacer de bloquer un compte ou signaler une violation imminente', 1),
(31, 8, 'Proposer des formations gratuites', 0),
(32, 8, 'Offrir des conseils en securite', 0);

-- Q9: Qu'est-ce que le smishing ?
INSERT INTO `RESPONSE` (`idRESPONSE`, `idResponseFromQuestion`, `responseText`, `isCorrect`) VALUES
(33, 9, 'Du phishing par SMS', 1),
(34, 9, 'Un reseau social pour professionnels', 0),
(35, 9, 'Un logiciel de protection contre les virus', 0),
(36, 9, 'Une technique de piratage de carte SIM', 0);

-- Q10: Comment reconnaitre un e-mail de phishing ?
INSERT INTO `RESPONSE` (`idRESPONSE`, `idResponseFromQuestion`, `responseText`, `isCorrect`) VALUES
(37, 10, 'Il contient toujours des images de haute qualite', 0),
(38, 10, 'Il peut contenir des fautes d''orthographe, une adresse suspecte, ou creer un sentiment d''urgence', 1),
(39, 10, 'Il provient toujours d''une adresse gmail.com', 0),
(40, 10, 'Il est impossible de reconnaitre un e-mail de phishing', 0);

-- Q11: Meilleure protection contre l'ingenierie sociale
INSERT INTO `RESPONSE` (`idRESPONSE`, `idResponseFromQuestion`, `responseText`, `isCorrect`) VALUES
(41, 11, 'Installer un antivirus couteux', 0),
(42, 11, 'Ne jamais utiliser internet', 0),
(43, 11, 'La formation et la sensibilisation des employes', 1),
(44, 11, 'Changer son ordinateur tous les mois', 0);

-- Q12: Inconnu demande votre mot de passe
INSERT INTO `RESPONSE` (`idRESPONSE`, `idResponseFromQuestion`, `responseText`, `isCorrect`) VALUES
(45, 12, 'Lui donner immediatement votre mot de passe', 0),
(46, 12, 'Refuser et verifier aupres de votre service informatique', 1),
(47, 12, 'Raccrocher et ne rien faire', 0),
(48, 12, 'Lui donner un faux mot de passe', 0);

-- Q13: Authentification multifacteur (MFA)
INSERT INTO `RESPONSE` (`idRESPONSE`, `idResponseFromQuestion`, `responseText`, `isCorrect`) VALUES
(49, 13, 'Un systeme qui demande plusieurs mots de passe differents', 0),
(50, 13, 'Une protection qui necessite plusieurs preuves d''identite (mot de passe + code SMS par exemple)', 1),
(51, 13, 'Un type de virus informatique', 0),
(52, 13, 'Un logiciel pour faire plusieurs taches en meme temps', 0);

-- =====================================================
-- 10. BADGES
-- =====================================================

INSERT INTO `BADGES` (`idBADGES`, `name`, `image`, `idQuiz`) VALUES
(1, 'Cyber Debutant', NULL, 1);

INSERT INTO `BADGES` (`idBADGES`, `name`, `image`, `idQuiz`) VALUES
(2, 'Anti-Ingenierie Sociale', NULL, 3);

-- =====================================================
-- INFORMATIONS DE CONNEXION POUR LES TESTS
-- =====================================================
--
-- | Username     | Email                    | Mot de passe   | Roles          |
-- |--------------|--------------------------|----------------|----------------|
-- | AdminHoot    | admin@cyberhoot.local    | Adm!nP@ss450   | admin, creator |
-- | TestCreator  | creator@cyberhoot.local  | testCre@t0r!   | creator        |
-- | TestPlayer   | player@cyberhoot.local   | Player123!     | player         |
-- =====================================================
