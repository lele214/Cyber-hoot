-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `cyberhoot` DEFAULT CHARACTER SET utf8mb4 ;
USE `cyberhoot` ;

-- -----------------------------------------------------
-- Table `cyberhoot`.`USER`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cyberhoot`.`USER` (
  `idUSER` INT NOT NULL AUTO_INCREMENT,
  `typeUser` ENUM('Admin', 'Redactor', 'Player') NULL,
  `username` VARCHAR(45) NULL,
  `hashpassword` VARCHAR(60) NULL,
  `emailUser` VARCHAR(45) NULL,
  PRIMARY KEY (`idUSER`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cyberhoot`.`QUIZ`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cyberhoot`.`QUIZ` (
  `idQUIZ` INT NOT NULL AUTO_INCREMENT,
  `idCreatedByUser` INT NOT NULL,
  `difficulty` ENUM('HARD', 'MEDIUM', 'EASY') NULL,
  `title` VARCHAR(45) NULL,
  `statut` ENUM('MODIFIED', 'PUBLISHED', 'DRAFT') NULL,
  `createdAt` DATE NULL,
  PRIMARY KEY (`idQUIZ`),
  INDEX `idCreatedByUser_idx` (`idCreatedByUser` ASC) VISIBLE,
  CONSTRAINT `idCreatedByUser`
    FOREIGN KEY (`idCreatedByUser`)
    REFERENCES `cyberhoot`.`USER` (`idUSER`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cyberhoot`.`BADGES`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cyberhoot`.`BADGES` (
  `idBADGES` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NULL,
  `image` BLOB NULL,
  `idQuiz` INT NOT NULL,
  PRIMARY KEY (`idBADGES`),
  INDEX `idQuiz_idx` (`idQuiz` ASC) VISIBLE,
  CONSTRAINT `idQuiz`
    FOREIGN KEY (`idQuiz`)
    REFERENCES `cyberhoot`.`QUIZ` (`idQUIZ`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cyberhoot`.`NOTIFICATIONS`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cyberhoot`.`NOTIFICATIONS` (
  `idNOTIFICATIONS` INT NOT NULL AUTO_INCREMENT,
  `idUser` INT NOT NULL,
  `type` ENUM('new_quiz', 'badge_earned', 'reminder') NULL,
  `message` VARCHAR(45) NULL,
  `sentAt` DATE NULL,
  `emailNotif` VARCHAR(45) NULL,
  PRIMARY KEY (`idNOTIFICATIONS`),
  INDEX `idUser_idx` (`idUser` ASC) VISIBLE,
  CONSTRAINT `idUser`
    FOREIGN KEY (`idUser`)
    REFERENCES `cyberhoot`.`USER` (`idUSER`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cyberhoot`.`TROPHY`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cyberhoot`.`TROPHY` (
  `idBadge` INT NOT NULL,
  `idUser` INT NOT NULL,
  `obtainedAt` DATE NULL,
  `idTrophy` INT NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`idTrophy`),
  INDEX `idBadges_idx` (`idBadge` ASC) VISIBLE,
  INDEX `idUser_idx` (`idUser` ASC) VISIBLE,
  CONSTRAINT `fk_trophy_badges`
    FOREIGN KEY (`idBadge`)
    REFERENCES `cyberhoot`.`BADGES` (`idBADGES`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_trophy_user`
    FOREIGN KEY (`idUser`)
    REFERENCES `cyberhoot`.`USER` (`idUSER`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cyberhoot`.`QUESTION`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cyberhoot`.`QUESTION` (
  `idQUESTION` INT NOT NULL AUTO_INCREMENT,
  `idQuestionFromQuiz` INT NOT NULL,
  `QuestionText` VARCHAR(45) NULL,
  PRIMARY KEY (`idQUESTION`),
  INDEX `idQuestionFromQuiz_idx` (`idQuestionFromQuiz` ASC) VISIBLE,
  CONSTRAINT `idQuestionFromQuiz`
    FOREIGN KEY (`idQuestionFromQuiz`)
    REFERENCES `cyberhoot`.`QUIZ` (`idQUIZ`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cyberhoot`.`RESPONSE`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cyberhoot`.`RESPONSE` (
  `idRESPONSE` INT NOT NULL AUTO_INCREMENT,
  `idResponseFromQuestion` INT NOT NULL,
  `responseText` VARCHAR(45) NULL,
  `isCorrect` TINYINT(1) NULL,
  PRIMARY KEY (`idRESPONSE`),
  INDEX `idResponseFromQuestion_idx` (`idResponseFromQuestion` ASC) VISIBLE,
  CONSTRAINT `idResponseFromQuestion`
    FOREIGN KEY (`idResponseFromQuestion`)
    REFERENCES `cyberhoot`.`QUESTION` (`idQUESTION`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cyberhoot`.`MEDIA`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cyberhoot`.`MEDIA` (
  `idMEDIA` INT NOT NULL AUTO_INCREMENT,
  `idMediaFromQuestion` INT NULL,
  `idMediaFromResponse` INT NULL,
  `mediaUrl` VARCHAR(255) NULL,
  `mediaType` VARCHAR(50) NULL,
  PRIMARY KEY (`idMEDIA`),
  INDEX `idMediaFromQuestion_idx` (`idMediaFromQuestion` ASC) VISIBLE,
  INDEX `idMediaFromResponse_idx` (`idMediaFromResponse` ASC) VISIBLE,
  CONSTRAINT `chk_media_source` CHECK (
    ((`idMediaFromQuestion` IS NOT NULL AND `idMediaFromResponse` IS NULL) OR
     (`idMediaFromQuestion` IS NULL AND `idMediaFromResponse` IS NOT NULL))
  ),
  CONSTRAINT `idMediaFromQuestion`
    FOREIGN KEY (`idMediaFromQuestion`)
    REFERENCES `cyberhoot`.`QUESTION` (`idQUESTION`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `idMediaFromResponse`
    FOREIGN KEY (`idMediaFromResponse`)
    REFERENCES `cyberhoot`.`RESPONSE` (`idRESPONSE`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cyberhoot`.`RESULT`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cyberhoot`.`RESULT` (
  `idRESULT` INT NOT NULL AUTO_INCREMENT,
  `idQUIZinResult` INT NOT NULL,
  `idUSERinResult` INT NOT NULL,
  `date` DATE NULL,
  `resultHistory` VARCHAR(45) NULL COMMENT 'ici prévoir un champ pour garder en mémoire les réponses à chaque question qu\'un utilisateur a donné pour un quiz',
  PRIMARY KEY (`idRESULT`, `idQUIZinResult`, `idUSERinResult`),
  INDEX `idQUIZ_idx` (`idQUIZinResult` ASC) VISIBLE,
  INDEX `idUSERinResult_idx` (`idUSERinResult` ASC) VISIBLE,
  CONSTRAINT `idQUIZinResult`
    FOREIGN KEY (`idQUIZinResult`)
    REFERENCES `cyberhoot`.`QUIZ` (`idQUIZ`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `idUSERinResult`
    FOREIGN KEY (`idUSERinResult`)
    REFERENCES `cyberhoot`.`USER` (`idUSER`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cyberhoot`.`CONNEXION_LOG`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cyberhoot`.`CONNEXION_LOG` (
  `idCONNEXION_LOG` INT NOT NULL AUTO_INCREMENT,
  `idUSERforConnexion` INT NOT NULL,
  PRIMARY KEY (`idCONNEXION_LOG`, `idUSERforConnexion`),
  INDEX `idUSERforConnexion_idx` (`idUSERforConnexion` ASC) VISIBLE,
  CONSTRAINT `idUSERforConnexion`
    FOREIGN KEY (`idUSERforConnexion`)
    REFERENCES `cyberhoot`.`USER` (`idUSER`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
