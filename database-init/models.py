from database import db
from datetime import date

class User(db.Model):
    __tablename__ = 'USER'

    idUSER = db.Column(db.Integer, primary_key=True, autoincrement=True)
    typeUser = db.Column(db.Enum('Admin', 'Redactor', 'Player'), nullable=True)
    username = db.Column(db.String(45), nullable=True)
    hashpassword = db.Column(db.String(60), nullable=True)
    emailUser = db.Column(db.String(45), nullable=True)

    # Relations
    quizzes = db.relationship('Quiz', back_populates='creator', foreign_keys='Quiz.idCreatedByUser')
    notifications = db.relationship('Notification', back_populates='user')
    trophies = db.relationship('Trophy', back_populates='user')
    results = db.relationship('Result', back_populates='user')
    connexion_logs = db.relationship('ConnexionLog', back_populates='user')

    def __repr__(self):
        return f'<User {self.username}>'


class Quiz(db.Model):
    __tablename__ = 'QUIZ'

    idQUIZ = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idCreatedByUser = db.Column(db.Integer, db.ForeignKey('USER.idUSER'), nullable=False)
    difficulty = db.Column(db.Enum('HARD', 'MEDIUM', 'EASY'), nullable=True)
    title = db.Column(db.String(45), nullable=True)
    statut = db.Column(db.Enum('MODIFIED', 'PUBLISHED', 'DRAFT'), nullable=True)
    createdAt = db.Column(db.Date, nullable=True)

    # Relations
    creator = db.relationship('User', back_populates='quizzes', foreign_keys=[idCreatedByUser])
    badges = db.relationship('Badge', back_populates='quiz')
    questions = db.relationship('Question', back_populates='quiz')
    results = db.relationship('Result', back_populates='quiz')

    def __repr__(self):
        return f'<Quiz {self.title}>'


class Badge(db.Model):
    __tablename__ = 'BADGES'

    idBADGES = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45), nullable=True)
    image = db.Column(db.LargeBinary, nullable=True)
    idQuiz = db.Column(db.Integer, db.ForeignKey('QUIZ.idQUIZ'), nullable=False)

    # Relations
    quiz = db.relationship('Quiz', back_populates='badges')
    trophies = db.relationship('Trophy', back_populates='badge')

    def __repr__(self):
        return f'<Badge {self.name}>'


class Notification(db.Model):
    __tablename__ = 'NOTIFICATIONS'

    idNOTIFICATIONS = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idUser = db.Column(db.Integer, db.ForeignKey('USER.idUSER'), nullable=False)
    type = db.Column(db.Enum('new_quiz', 'badge_earned', 'reminder'), nullable=True)
    message = db.Column(db.String(45), nullable=True)
    sentAt = db.Column(db.Date, nullable=True)
    emailNotif = db.Column(db.String(45), nullable=True)

    # Relations
    user = db.relationship('User', back_populates='notifications')

    def __repr__(self):
        return f'<Notification {self.type} for User {self.idUser}>'


class Trophy(db.Model):
    __tablename__ = 'TROPHY'

    idTrophy = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idBadge = db.Column(db.Integer, db.ForeignKey('BADGES.idBADGES'), nullable=False)
    idUser = db.Column(db.Integer, db.ForeignKey('USER.idUSER'), nullable=False)
    obtainedAt = db.Column(db.Date, nullable=True)

    # Relations
    badge = db.relationship('Badge', back_populates='trophies')
    user = db.relationship('User', back_populates='trophies')

    def __repr__(self):
        return f'<Trophy {self.idTrophy}>'


class Question(db.Model):
    __tablename__ = 'QUESTION'

    idQUESTION = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idQuestionFromQuiz = db.Column(db.Integer, db.ForeignKey('QUIZ.idQUIZ'), nullable=False)
    QuestionText = db.Column(db.String(45), nullable=True)

    # Relations
    quiz = db.relationship('Quiz', back_populates='questions')
    responses = db.relationship('Response', back_populates='question')
    medias = db.relationship('Media', back_populates='question', foreign_keys='Media.idMediaFromQuestion')

    def __repr__(self):
        return f'<Question {self.idQUESTION}>'


class Response(db.Model):
    __tablename__ = 'RESPONSE'

    idRESPONSE = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idResponseFromQuestion = db.Column(db.Integer, db.ForeignKey('QUESTION.idQUESTION'), nullable=False)
    responseText = db.Column(db.String(45), nullable=True)
    isCorrect = db.Column(db.Boolean, nullable=True)

    # Relations
    question = db.relationship('Question', back_populates='responses')
    medias = db.relationship('Media', back_populates='response', foreign_keys='Media.idMediaFromResponse')

    def __repr__(self):
        return f'<Response {self.idRESPONSE}>'


class Media(db.Model):
    __tablename__ = 'MEDIA'

    idMEDIA = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idMediaFromQuestion = db.Column(db.Integer, db.ForeignKey('QUESTION.idQUESTION'), nullable=True)
    idMediaFromResponse = db.Column(db.Integer, db.ForeignKey('RESPONSE.idRESPONSE'), nullable=True)
    mediaUrl = db.Column(db.String(255), nullable=True)
    mediaType = db.Column(db.String(50), nullable=True)

    # Relations
    question = db.relationship('Question', back_populates='medias', foreign_keys=[idMediaFromQuestion])
    response = db.relationship('Response', back_populates='medias', foreign_keys=[idMediaFromResponse])

    def __repr__(self):
        return f'<Media {self.idMEDIA}>'


class Result(db.Model):
    __tablename__ = 'RESULT'

    idRESULT = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idQUIZinResult = db.Column(db.Integer, db.ForeignKey('QUIZ.idQUIZ'), nullable=False)
    idUSERinResult = db.Column(db.Integer, db.ForeignKey('USER.idUSER'), nullable=False)
    date = db.Column(db.Date, nullable=True)
    resultHistory = db.Column(db.String(45), nullable=True, comment='Champ pour garder en mémoire les réponses à chaque question')

    # Relations
    quiz = db.relationship('Quiz', back_populates='results')
    user = db.relationship('User', back_populates='results')

    def __repr__(self):
        return f'<Result {self.idRESULT}>'


class ConnexionLog(db.Model):
    __tablename__ = 'CONNEXION_LOG'

    idCONNEXION_LOG = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idUSERforConnexion = db.Column(db.Integer, db.ForeignKey('USER.idUSER'), nullable=False)

    # Relations
    user = db.relationship('User', back_populates='connexion_logs')

    def __repr__(self):
        return f'<ConnexionLog {self.idCONNEXION_LOG}>'
