-- Données de test pour Cyber-hoot
-- Ce fichier contient des données d'exemple pour le développement

USE `cyberhoot`;

--
-- Données pour la table `USER`
--
INSERT INTO `USER` VALUES
(1,'Admin','admin','hashed_password_123','admin@cyberhoot.com'),
(2,'Redactor','redactor1','hashed_password_456','redactor@cyberhoot.com'),
(3,'Player','player1','hashed_password_789','player1@cyberhoot.com'),
(4,'Player','player2','hashed_password_abc','player2@cyberhoot.com'),
(5,'Player','player3','hashed_password_def','player3@cyberhoot.com');

--
-- Données pour la table `QUIZ`
--
INSERT INTO `QUIZ` VALUES
(1,2,'EASY','Introduction à la Cybersécurité','PUBLISHED','2025-01-15'),
(2,2,'MEDIUM','Phishing et Social Engineering','PUBLISHED','2025-02-01'),
(3,2,'HARD','Cryptographie Avancée','DRAFT','2025-02-10'),
(4,2,'MEDIUM','Sécurité des Réseaux','MODIFIED','2025-02-15');

--
-- Données pour la table `BADGES`
--
INSERT INTO `BADGES` VALUES
(1,'Débutant en Cybersécurité',NULL,1),
(2,'Expert en Phishing',NULL,2),
(3,'Maître de la Cryptographie',NULL,3);

--
-- Données pour la table `QUESTION`
--
INSERT INTO `QUESTION` VALUES
(1,1,'Qu\'est-ce qu\'un pare-feu ?'),
(2,1,'Que signifie HTTPS ?'),
(3,2,'Qu\'est-ce que le phishing ?'),
(4,2,'Comment reconnaître un email suspect ?'),
(5,3,'Qu\'est-ce que le chiffrement AES ?');

--
-- Données pour la table `RESPONSE`
--
INSERT INTO `RESPONSE` VALUES
(1,1,'Un mur de protection réseau',1),
(2,1,'Un type de virus',0),
(3,1,'Un logiciel antivirus',0),
(4,2,'HyperText Transfer Protocol Secure',1),
(5,2,'High Tech Transfer Protocol',0),
(6,3,'Une technique d\'arnaque par email',1),
(7,3,'Un type de malware',0),
(8,4,'Vérifier l\'adresse de l\'expéditeur',1),
(9,4,'Ouvrir toutes les pièces jointes',0);

--
-- Données pour la table `CONNEXION_LOG`
--
INSERT INTO `CONNEXION_LOG` VALUES
(1,1),
(2,2),
(3,3),
(4,4),
(5,5);

--
-- Données pour la table `NOTIFICATIONS`
--
INSERT INTO `NOTIFICATIONS` VALUES
(1,3,'badge_earned','Vous avez gagné un badge !','2025-01-20','player1@cyberhoot.com'),
(2,4,'new_quiz','Nouveau quiz disponible','2025-02-01','player2@cyberhoot.com'),
(3,3,'badge_earned','Expert en Phishing débloqué !','2025-02-05','player1@cyberhoot.com');

--
-- Données pour la table `RESULT`
--
INSERT INTO `RESULT` VALUES
(1,1,3,'2025-01-20',NULL),
(2,1,4,'2025-01-22',NULL),
(3,2,3,'2025-02-05',NULL),
(4,2,5,'2025-02-08',NULL);

--
-- Données pour la table `TROPHY`
--
INSERT INTO `TROPHY` VALUES
(1,3,'2025-01-20',1),
(1,4,'2025-01-22',2),
(2,3,'2025-02-05',3);
