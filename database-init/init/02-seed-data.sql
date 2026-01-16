-- Donnees initiales pour Cyber-hoot

USE `cyberhoot`;

--
-- Roles de base (obligatoires pour le fonctionnement de l'application)
--
INSERT INTO `ROLES` (`nameRoles`) VALUES
('admin'),
('player'),
('creator');

--
-- Note: Pour creer un utilisateur admin, utilisez le formulaire d'inscription
-- puis executez les commandes SQL suivantes pour lui attribuer les roles:
--
-- INSERT INTO userToRoles (idUser, idROLES)
-- SELECT u.idUSER, r.idROLES FROM USER u, ROLES r WHERE u.username = 'VotreUsername' AND r.nameRoles = 'admin';
--
-- INSERT INTO userToRoles (idUser, idROLES)
-- SELECT u.idUSER, r.idROLES FROM USER u, ROLES r WHERE u.username = 'VotreUsername' AND r.nameRoles = 'creator';
