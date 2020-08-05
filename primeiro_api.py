from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from functools import wraps
from socket import gethostname

app = Flask(__name__)

app.config['SECRET_KEY'] = 'segredo232'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db = SQLAlchemy(app)
db: SQLAlchemy


class Autor(db.Model):
    __tablename__ = "autor"
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagens = db.relationship('Postagem')


class Postagem(db.Model):
    __tablename__ = "postagem"
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))


def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verifica se foi incluído um token na requisição
        if 'x-acess-token' in request.headers:
            token = request.headers['x-acess-token']
        # Se não houver um token, retorna a requisição solicitando um token
        if not token:
            return jsonify({'mensagem': 'Token de autenticação precisa ser incluido nessa requisição!'})
        try:
            dados = jwt.decode(token, app.config['SECRET_KEY'])
            autor_atual = Autor.query.filter_by(
                id_autor=dados['id_autor']).first()
        except:
            return jsonify({'mensagem': 'Token é inválido'}, 401)

        return f(autor_atual, *args, **kwargs)
    # retornando decorador
    return decorated


@app.route('/postagens', methods=['GET'])
@token_obrigatorio
def obter_todas_postagem(ator_atual):
    postagens = Postagem.query.all()
    lista_de_postagens = []
    for postagem in postagens:
        dados_postagens = {}
        dados_postagens['titulo'] = postagem.titulo
        dados_postagens['id_autor'] = postagem.id_autor
        lista_de_postagens.append(dados_postagens)
    return jsonify({'Postagens': lista_de_postagens})


@app.route('/postagens/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem_id(ator_atual, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()

    if not postagem:
        return jsonify({'mensagem': 'Postagem não encontrada'})
    dados_postagem = {}
    dados_postagem['titulo'] = postagem.titulo
    dados_postagem['id_autor'] = postagem.id_autor

    return jsonify({'Postagem': dados_postagem})


@app.route('/postagens', methods=['POST'])
@token_obrigatorio
def nova_postagem(ator_atual):
    postagem = request.get_json()
    nova_postagem = Postagem(titulo=postagem['titulo'],
                             id_autor=postagem['id_autor'])
    db.session.add(nova_postagem)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem Criada Com Sucesso'})


@app.route('/postagens/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio
def atualizar_postagem(ator_atual, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    dados_postagem = request.get_json()

    postagem.titulo = dados_postagem['titulo']
    postagem.id_autor = dados_postagem['id_autor']

    db.session.commit()

    return jsonify({'mensagem', 'Postagem Alterada com sucesso!'})


@app.route('/postagens/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def deletar_postagem(ator_atual, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()

    if not postagem:
        return jsonify({'mensagem', 'Postagem não encontrada'})
    db.session.delete(postagem)
    db.session.commit()

    return jsonify({'mensagem', 'Postagem excluída com sucesso!'})


# criar uma api para criar novos autores


@app.route('/autores', methods=['GET'])
@token_obrigatorio
def obter_todas_autores(ator_atual):
    autores = Autor.query.all()
    lista_de_autores = []
    for autor in autores:
        dados_autores = {}
        dados_autores['id_autor'] = autor.id_autor
        dados_autores['nome'] = autor.nome
        dados_autores['email'] = autor.email
        lista_de_autores.append(dados_autores)
    return jsonify({'autores': lista_de_autores})


@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def obter_autores_id(ator_atual, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()

    if not autor:
        return jsonify({'mensagem': 'Autor não encontrado'})
    dados_autor = {}
    dados_autor['id_autor'] = autor.id_autor
    dados_autor['nome'] = autor.nome
    dados_autor['email'] = autor.email

    return jsonify({'autor': dados_autor})


@app.route('/autores', methods=['POST'])
@token_obrigatorio
def novo_autor(ator_atual):
    dados = request.get_json()
    novo_usuario = Autor(nome=dados['nome'],
                         senha=dados['senha'], email=dados['email'])
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({'mensagem': 'Novo usuario criado com sucesso'})


@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def atualizar_autor(ator_atual, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()

    dados_autor = request.get_json()

    print(autor)
    print(dados_autor['nome'])
    print(dados_autor['email'])
    autor.nome = dados_autor['nome']
    autor.email = dados_autor['email']

    db.session.commit()
    return jsonify({'mensagem': 'Autor Alterado com sucesso!'})


@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def deletar_autor(ator_atual, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()

    if not autor:
        return jsonify({'mensagem': 'Autor não encontrado'})
    db.session.delete(autor)
    db.session.commit()

    return jsonify({'mensagem': 'Autor excluído com sucesso!'})


@app.route('/login', methods=['GET'])
def login():
    dados_autenticacao = request.authorization
    if not dados_autenticacao or not dados_autenticacao.username or not dados_autenticacao.password:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório!"'})

    user = Autor.query.filter_by(nome=dados_autenticacao.username).first()
    if user.senha == dados_autenticacao.password:
        token = jwt.encode({'id_autor': user.id_autor, 'exp': datetime.datetime.utcnow(
        )+datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório!"'})


if __name__ == '__main__':
    db.create_all()
    db.create_all()
    autor = Autor(nome='matheus', email='matheus', senha='senha', admin=True,)
    db.session.add(autor)
    db.session.commit()

    if 'liveconsole' not in gethostname():
        app.run()
