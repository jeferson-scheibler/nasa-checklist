# app.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# --- Configuração Inicial ---
app = Flask(__name__)
# Chave secreta para gerenciar sessões de login
app.config['SECRET_KEY'] = 'nasa-space-apps-lajeado-2025-tecnovates'
# Caminho do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
db = SQLAlchemy(app)

# --- Definição das Tabelas do Banco de Dados ---
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    # A senha será a mesma para todos no início
    password = db.Column(db.String(100), nullable=False)

class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)

class TeamProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('checklist_item.id'), nullable=False)
    is_complete = db.Column(db.Boolean, default=False)

# --- Rotas da Aplicação (As "Páginas") ---

# Página de Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        team_name = request.form['team_name']
        password = request.form['password']
        
        team = Team.query.filter_by(name=team_name).first()
        
        # Simples verificação de senha
        if team and team.password == password:
            session['team_id'] = team.id
            session['team_name'] = team.name
            return redirect(url_for('checklist'))
        else:
            return render_template('login.html', teams=Team.query.all(), error="Senha ou time incorreto.")

    teams = Team.query.all()
    return render_template('login.html', teams=teams)

# Página do Checklist (só para quem está logado)
@app.route('/checklist')
def checklist():
    if 'team_id' not in session:
        return redirect(url_for('login'))

    team_id = session['team_id']
    items = ChecklistItem.query.order_by(ChecklistItem.order).all()
    progress = TeamProgress.query.filter_by(team_id=team_id).all()
    
    # Mapeia o progresso para fácil acesso no HTML
    progress_map = {p.item_id: p.is_complete for p in progress}
    
    return render_template('checklist.html', items=items, progress_map=progress_map)

# Rota para atualizar um item do checklist (usada pelo JavaScript)
@app.route('/update_item', methods=['POST'])
def update_item():
    if 'team_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    data = request.json
    item_id = data.get('item_id')
    is_complete = data.get('is_complete')
    team_id = session['team_id']
    
    progress_item = TeamProgress.query.filter_by(team_id=team_id, item_id=item_id).first()
    if progress_item:
        progress_item.is_complete = is_complete
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Item not found'}), 404

# Painel do Admin
@app.route('/checklist')
def admin():
    teams = Team.query.all()
    total_items = ChecklistItem.query.count()
    
    ranking = []
    for team in teams:
        completed_count = TeamProgress.query.filter_by(team_id=team.id, is_complete=True).count()
        progress_percentage = (completed_count / total_items * 100) if total_items > 0 else 0
        ranking.append({
            'name': team.name,
            'progress': progress_percentage
        })
    
    # Ordena o ranking por progresso
    ranking.sort(key=lambda x: x['progress'], reverse=True)
    
    return render_template('admin.html', ranking=ranking)

# Rota de Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Função para Iniciar o Banco de Dados ---
def setup_database(app):
    with app.app_context():
        # Cria as tabelas se não existirem
        db.create_all()

        # Adiciona os itens do checklist (só na primeira vez)
        if ChecklistItem.query.count() == 0:
            items = [
                (1, "Resumo do Projeto (High-Level Summary) preenchido."),
                (2, "Link para o Demo (Vídeo de 30s ou 7 slides) adicionado."),
                (3, "Link para o Projeto Final (GitHub, Figma, etc.) adicionado."),
                (4, "Descrição detalhada do projeto preenchida."),
                (5, "Detalhes sobre o uso de dados da NASA preenchidos (Obrigatório!)."),
                (6, "Referências e uso de IA declarados."),
                (7, "Página do projeto e demo totalmente em INGLÊS."),
                (8, "Revisão final do projeto com a equipe.")
            ]
            for order, desc in items:
                db.session.add(ChecklistItem(order=order, description=desc))
            db.session.commit()

        # Adiciona os times (exemplo)
        if Team.query.count() == 0:
            teams_with_passwords = [
                ("André+5", "andre5@lajeado25"),
                ("Artync", "artync@lajeado25"),
                ("Astrobots", "astrobots@lajeado25"),
                ("Biocosmos", "biocosmos@lajeado25"),
                ("Boyband", "boyband@lajeado25"),
                ("Chicxulub", "chicxulub@lajeado25"),
                ("Chispas", "chispas@lajeado25"),
                ("Ctrl+Farroups", "ctrlfarroups@lajeado25"),
                ("Interstellar Engineers", "interstellarengineers@lajeado25"),
                ("Pangeia", "pangeia@lajeado25"),
                ("Papagaios do Espaço", "papagaiosdoespaco@lajeado25"),
                ("Peixonautas", "peixonautas@lajeado25"),
                ("Prado", "prado@lajeado25"),
                ("SATRAFFIC", "satraffic@lajeado25"),
                ("TellusOne", "tellusone@lajeado25"),
                ("Tropa do Booleano", "tropadobooleano@lajeado25"),
                ("Urban Health Tech", "urbanhealthtech@lajeado25")
            ] 
            for name, password in teams_with_passwords:
                db.session.add(Team(name=name, password=password))
            db.session.commit()

        # Inicializa o progresso para todos os times e itens
        teams = Team.query.all()
        items = ChecklistItem.query.all()
        for team in teams:
            for item in items:
                if TeamProgress.query.filter_by(team_id=team.id, item_id=item.id).count() == 0:
                    db.session.add(TeamProgress(team_id=team.id, item_id=item.id, is_complete=False))
        db.session.commit()

if __name__ == '__main__':
    setup_database(app)
    app.run(debug=False, host='0.0.0.0')