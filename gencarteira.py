from flask import Flask, render_template, request, redirect, session, flash, url_for
import os
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from datetime import datetime

"""class Ativo:
    def __init__(self, nome, tipo, setor, descricao):
        self.nome = nome
        self.tipo = tipo
        self.setor = setor
        self.descricao = descricao"""

app = Flask(__name__)
app.secret_key = 'sjdaksjdaldjlasjdkajskldkl'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')

db = SQLAlchemy(app)

class Ativo(db.Model):
    __tablename__ = "ativos"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(10), unique=True, nullable=False)
    setor = db.Column(db.String(50), unique=False)
    tipo = db.Column(db.String(30), unique=False)
    descricao = db.Column(db.String(255), unique=False)
    data = db.Column(db.DateTime, default=db.func.now())
    user = db.relationship('User', backref='usuarios')
    user_id = db.Column(db.Integer, 
                        db.ForeignKey('usuarios.id'), nullable=False)

    def __init__(self, nome="", setor="", tipo="", descricao="", data=None, uid=0):
        self.nome = nome
        self.setor = setor
        self.tipo = tipo
        self.descricao = descricao
        self.data = data
        self.user_id = uid
    
    def __str__(self):
        return f"Nome: {self.nome}\n Setor: {self.setor}"

class User(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    socialname = db.Column(db.String(100))
    def __init__(self, username="", password="", socialname=""):
        self.username = username
        self.password = password
        self.socialname = socialname
    def __str__(self):
        return f"User: {self.socialname}"


@app.route("/")
def index():
    ativos = []
    if 'usuario_logado' in session and session['usuario_logado'] is not None:
        query = db.session.query(User).filter_by(username=session['usuario_logado'])
        if query.count() > 0:
            user = query.first()
            resultado = db.session.query(Ativo).filter_by(user_id=user.id)
            for ativo in resultado:
                ativos.append(ativo)
        else:
            flash("Usuário registrado!")
    return render_template('lista.html', 
                           colunas=['Nome', 'Tipo', 'Setor'], 
                           titulo='Lista de Ativos', ativos=ativos)

@app.route("/novo")
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for("novo")))
    return render_template("novo.html", titulo="Novo Ativo")

@app.route("/criar", methods=['POST', ])
def criar():
    if 'usuario_logado' in session and session['usuario_logado'] is not None:
        res = db.session.query(User).filter_by(username=session['usuario_logado'])
        if res.count() > 0:
            user = res.first()
            nome = request.form['nome']
            tipo = request.form['tipo']
            setor = request.form['setor']
            descricao = request.form['descricao']
            data = "2023-06-22"
            ativo = Ativo(nome, 
                            tipo, 
                            setor, 
                            descricao,
                            datetime.strptime(data, '%Y-%m-%d'), 
                            user.id)
            db.session.add(ativo)
            db.session.commit()
            flash("Ativo adicionado com sucesso!")
        else:
            flash("Usuário não registrado. Faça login novamente e tente outra vez!")
    else:
        flash("Usuário não autenticado!")
    return redirect(url_for("index"))

@app.route('/login')
def login():
    proxima = request.args.get("proxima")
    if proxima is None:
        proxima = "index"
    return render_template("login.html", proxima=proxima)

@app.route("/autenticar", methods=['POST',])
def autenticar():
    proxima = request.form['proxima']
    username = request.form['usuario']
    password = request.form['senha']
    query = db.session.query(User).filter_by(username=username)

    if query.count() > 0:
        user = query.first()
        if user.password == password:
            session['usuario_logado'] = username
            flash(f'{session["usuario_logado"]} logado com sucesso!')
            return redirect(proxima)
    flash(f'Credenciais inválidas! Tente novamente.')
    return redirect(url_for("login", proxima=proxima))

@app.route("/logout")
def logout():
    if 'usuario_logado' in session and session['usuario_logado'] is not None:
        flash("Logout efetuado com sucesso!")
    else:
        flash("Usuário não logado!", "error")
    session['usuario_logado'] = None
    return redirect(url_for("login"))
        
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        try:
            user = User('gilzamir', 'abcd', 'Gilzamir')
            db.session.add(user)
            db.session.commit()
        except:
            pass
    app.run(debug=True)
