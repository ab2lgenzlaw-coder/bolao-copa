from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, os, uuid, json, jwt
from datetime import datetime, timezone
from functools import wraps

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

SECRET = os.environ.get('SECRET_KEY', 'bolao-copa-2026-secret')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin2026')
DB_PATH = os.path.join(os.path.dirname(__file__), 'bolao.db')

# ─── JOGOS ────────────────────────────────────────────────────────────────────
JOGOS = [
  # Fase de Grupos
  {"id":1,"fase":"Grupo A","data":"2026-06-11","hora":"16:00","time1":"México","flag1":"🇲🇽","time2":"África do Sul","flag2":"🇿🇦"},
  {"id":2,"fase":"Grupo A","data":"2026-06-11","hora":"23:00","time1":"Coreia do Sul","flag1":"🇰🇷","time2":"Tchéquia","flag2":"🇨🇿"},
  {"id":3,"fase":"Grupo A","data":"2026-06-18","hora":"13:00","time1":"Tchéquia","flag1":"🇨🇿","time2":"África do Sul","flag2":"🇿🇦"},
  {"id":4,"fase":"Grupo A","data":"2026-06-18","hora":"22:00","time1":"México","flag1":"🇲🇽","time2":"Coreia do Sul","flag2":"🇰🇷"},
  {"id":5,"fase":"Grupo A","data":"2026-06-24","hora":"22:00","time1":"Tchéquia","flag1":"🇨🇿","time2":"México","flag2":"🇲🇽"},
  {"id":6,"fase":"Grupo A","data":"2026-06-24","hora":"22:00","time1":"África do Sul","flag1":"🇿🇦","time2":"Coreia do Sul","flag2":"🇰🇷"},
  {"id":7,"fase":"Grupo B","data":"2026-06-12","hora":"16:00","time1":"Canadá","flag1":"🇨🇦","time2":"Bósnia","flag2":"🇧🇦"},
  {"id":8,"fase":"Grupo B","data":"2026-06-13","hora":"16:00","time1":"Catar","flag1":"🇶🇦","time2":"Suíça","flag2":"🇨🇭"},
  {"id":9,"fase":"Grupo B","data":"2026-06-18","hora":"16:00","time1":"Suíça","flag1":"🇨🇭","time2":"Bósnia","flag2":"🇧🇦"},
  {"id":10,"fase":"Grupo B","data":"2026-06-18","hora":"19:00","time1":"Canadá","flag1":"🇨🇦","time2":"Catar","flag2":"🇶🇦"},
  {"id":11,"fase":"Grupo B","data":"2026-06-24","hora":"16:00","time1":"Suíça","flag1":"🇨🇭","time2":"Canadá","flag2":"🇨🇦"},
  {"id":12,"fase":"Grupo B","data":"2026-06-24","hora":"16:00","time1":"Bósnia","flag1":"🇧🇦","time2":"Catar","flag2":"🇶🇦"},
  {"id":13,"fase":"Grupo C","data":"2026-06-13","hora":"19:00","time1":"Brasil","flag1":"🇧🇷","time2":"Marrocos","flag2":"🇲🇦"},
  {"id":14,"fase":"Grupo C","data":"2026-06-13","hora":"22:00","time1":"Haiti","flag1":"🇭🇹","time2":"Escócia","flag2":"🏴󠁧󠁢󠁳󠁣󠁴󠁿"},
  {"id":15,"fase":"Grupo C","data":"2026-06-19","hora":"19:00","time1":"Escócia","flag1":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","time2":"Marrocos","flag2":"🇲🇦"},
  {"id":16,"fase":"Grupo C","data":"2026-06-19","hora":"21:30","time1":"Brasil","flag1":"🇧🇷","time2":"Haiti","flag2":"🇭🇹"},
  {"id":17,"fase":"Grupo C","data":"2026-06-24","hora":"19:00","time1":"Escócia","flag1":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","time2":"Brasil","flag2":"🇧🇷"},
  {"id":18,"fase":"Grupo C","data":"2026-06-24","hora":"19:00","time1":"Marrocos","flag1":"🇲🇦","time2":"Haiti","flag2":"🇭🇹"},
  {"id":19,"fase":"Grupo D","data":"2026-06-12","hora":"22:00","time1":"Estados Unidos","flag1":"🇺🇸","time2":"Paraguai","flag2":"🇵🇾"},
  {"id":20,"fase":"Grupo D","data":"2026-06-14","hora":"01:00","time1":"Austrália","flag1":"🇦🇺","time2":"Turquia","flag2":"🇹🇷"},
  {"id":21,"fase":"Grupo D","data":"2026-06-19","hora":"16:00","time1":"Estados Unidos","flag1":"🇺🇸","time2":"Austrália","flag2":"🇦🇺"},
  {"id":22,"fase":"Grupo D","data":"2026-06-20","hora":"00:00","time1":"Turquia","flag1":"🇹🇷","time2":"Paraguai","flag2":"🇵🇾"},
  {"id":23,"fase":"Grupo D","data":"2026-06-25","hora":"23:00","time1":"Turquia","flag1":"🇹🇷","time2":"Estados Unidos","flag2":"🇺🇸"},
  {"id":24,"fase":"Grupo D","data":"2026-06-25","hora":"23:00","time1":"Paraguai","flag1":"🇵🇾","time2":"Austrália","flag2":"🇦🇺"},
  {"id":25,"fase":"Grupo E","data":"2026-06-14","hora":"14:00","time1":"Alemanha","flag1":"🇩🇪","time2":"Curaçao","flag2":"🇨🇼"},
  {"id":26,"fase":"Grupo E","data":"2026-06-14","hora":"20:00","time1":"Costa do Marfim","flag1":"🇨🇮","time2":"Equador","flag2":"🇪🇨"},
  {"id":27,"fase":"Grupo E","data":"2026-06-20","hora":"17:00","time1":"Alemanha","flag1":"🇩🇪","time2":"Costa do Marfim","flag2":"🇨🇮"},
  {"id":28,"fase":"Grupo E","data":"2026-06-20","hora":"21:00","time1":"Equador","flag1":"🇪🇨","time2":"Curaçao","flag2":"🇨🇼"},
  {"id":29,"fase":"Grupo E","data":"2026-06-25","hora":"17:00","time1":"Curaçao","flag1":"🇨🇼","time2":"Costa do Marfim","flag2":"🇨🇮"},
  {"id":30,"fase":"Grupo E","data":"2026-06-25","hora":"17:00","time1":"Equador","flag1":"🇪🇨","time2":"Alemanha","flag2":"🇩🇪"},
  {"id":31,"fase":"Grupo F","data":"2026-06-14","hora":"17:00","time1":"Holanda","flag1":"🇳🇱","time2":"Japão","flag2":"🇯🇵"},
  {"id":32,"fase":"Grupo F","data":"2026-06-14","hora":"23:00","time1":"Suécia","flag1":"🇸🇪","time2":"Tunísia","flag2":"🇹🇳"},
  {"id":33,"fase":"Grupo F","data":"2026-06-20","hora":"14:00","time1":"Holanda","flag1":"🇳🇱","time2":"Suécia","flag2":"🇸🇪"},
  {"id":34,"fase":"Grupo F","data":"2026-06-21","hora":"01:00","time1":"Tunísia","flag1":"🇹🇳","time2":"Japão","flag2":"🇯🇵"},
  {"id":35,"fase":"Grupo F","data":"2026-06-25","hora":"20:00","time1":"Japão","flag1":"🇯🇵","time2":"Suécia","flag2":"🇸🇪"},
  {"id":36,"fase":"Grupo F","data":"2026-06-25","hora":"20:00","time1":"Tunísia","flag1":"🇹🇳","time2":"Holanda","flag2":"🇳🇱"},
  {"id":37,"fase":"Grupo G","data":"2026-06-15","hora":"16:00","time1":"Bélgica","flag1":"🇧🇪","time2":"Egito","flag2":"🇪🇬"},
  {"id":38,"fase":"Grupo G","data":"2026-06-15","hora":"22:00","time1":"Irã","flag1":"🇮🇷","time2":"Nova Zelândia","flag2":"🇳🇿"},
  {"id":39,"fase":"Grupo G","data":"2026-06-21","hora":"16:00","time1":"Bélgica","flag1":"🇧🇪","time2":"Irã","flag2":"🇮🇷"},
  {"id":40,"fase":"Grupo G","data":"2026-06-21","hora":"22:00","time1":"Nova Zelândia","flag1":"🇳🇿","time2":"Egito","flag2":"🇪🇬"},
  {"id":41,"fase":"Grupo G","data":"2026-06-27","hora":"00:00","time1":"Egito","flag1":"🇪🇬","time2":"Irã","flag2":"🇮🇷"},
  {"id":42,"fase":"Grupo G","data":"2026-06-27","hora":"00:00","time1":"Nova Zelândia","flag1":"🇳🇿","time2":"Bélgica","flag2":"🇧🇪"},
  {"id":43,"fase":"Grupo H","data":"2026-06-15","hora":"13:00","time1":"Espanha","flag1":"🇪🇸","time2":"Cabo Verde","flag2":"🇨🇻"},
  {"id":44,"fase":"Grupo H","data":"2026-06-15","hora":"19:00","time1":"Arábia Saudita","flag1":"🇸🇦","time2":"Uruguai","flag2":"🇺🇾"},
  {"id":45,"fase":"Grupo H","data":"2026-06-21","hora":"13:00","time1":"Espanha","flag1":"🇪🇸","time2":"Arábia Saudita","flag2":"🇸🇦"},
  {"id":46,"fase":"Grupo H","data":"2026-06-21","hora":"19:00","time1":"Uruguai","flag1":"🇺🇾","time2":"Cabo Verde","flag2":"🇨🇻"},
  {"id":47,"fase":"Grupo H","data":"2026-06-26","hora":"21:00","time1":"Cabo Verde","flag1":"🇨🇻","time2":"Arábia Saudita","flag2":"🇸🇦"},
  {"id":48,"fase":"Grupo H","data":"2026-06-26","hora":"21:00","time1":"Uruguai","flag1":"🇺🇾","time2":"Espanha","flag2":"🇪🇸"},
  {"id":49,"fase":"Grupo I","data":"2026-06-16","hora":"16:00","time1":"França","flag1":"🇫🇷","time2":"Senegal","flag2":"🇸🇳"},
  {"id":50,"fase":"Grupo I","data":"2026-06-16","hora":"19:00","time1":"Iraque","flag1":"🇮🇶","time2":"Noruega","flag2":"🇳🇴"},
  {"id":51,"fase":"Grupo I","data":"2026-06-22","hora":"18:00","time1":"França","flag1":"🇫🇷","time2":"Iraque","flag2":"🇮🇶"},
  {"id":52,"fase":"Grupo I","data":"2026-06-22","hora":"21:00","time1":"Noruega","flag1":"🇳🇴","time2":"Senegal","flag2":"🇸🇳"},
  {"id":53,"fase":"Grupo I","data":"2026-06-26","hora":"16:00","time1":"Noruega","flag1":"🇳🇴","time2":"França","flag2":"🇫🇷"},
  {"id":54,"fase":"Grupo I","data":"2026-06-26","hora":"16:00","time1":"Senegal","flag1":"🇸🇳","time2":"Iraque","flag2":"🇮🇶"},
  {"id":55,"fase":"Grupo J","data":"2026-06-16","hora":"22:00","time1":"Argentina","flag1":"🇦🇷","time2":"Argélia","flag2":"🇩🇿"},
  {"id":56,"fase":"Grupo J","data":"2026-06-17","hora":"01:00","time1":"Áustria","flag1":"🇦🇹","time2":"Jordânia","flag2":"🇯🇴"},
  {"id":57,"fase":"Grupo J","data":"2026-06-22","hora":"14:00","time1":"Argentina","flag1":"🇦🇷","time2":"Áustria","flag2":"🇦🇹"},
  {"id":58,"fase":"Grupo J","data":"2026-06-23","hora":"00:00","time1":"Jordânia","flag1":"🇯🇴","time2":"Argélia","flag2":"🇩🇿"},
  {"id":59,"fase":"Grupo J","data":"2026-06-27","hora":"23:00","time1":"Argélia","flag1":"🇩🇿","time2":"Áustria","flag2":"🇦🇹"},
  {"id":60,"fase":"Grupo J","data":"2026-06-27","hora":"23:00","time1":"Jordânia","flag1":"🇯🇴","time2":"Argentina","flag2":"🇦🇷"},
  {"id":61,"fase":"Grupo K","data":"2026-06-17","hora":"14:00","time1":"Portugal","flag1":"🇵🇹","time2":"RD Congo","flag2":"🇨🇩"},
  {"id":62,"fase":"Grupo K","data":"2026-06-17","hora":"23:00","time1":"Uzbequistão","flag1":"🇺🇿","time2":"Colômbia","flag2":"🇨🇴"},
  {"id":63,"fase":"Grupo K","data":"2026-06-23","hora":"14:00","time1":"Portugal","flag1":"🇵🇹","time2":"Uzbequistão","flag2":"🇺🇿"},
  {"id":64,"fase":"Grupo K","data":"2026-06-23","hora":"23:00","time1":"Colômbia","flag1":"🇨🇴","time2":"RD Congo","flag2":"🇨🇩"},
  {"id":65,"fase":"Grupo K","data":"2026-06-27","hora":"20:30","time1":"Colômbia","flag1":"🇨🇴","time2":"Portugal","flag2":"🇵🇹"},
  {"id":66,"fase":"Grupo K","data":"2026-06-27","hora":"20:30","time1":"RD Congo","flag1":"🇨🇩","time2":"Uzbequistão","flag2":"🇺🇿"},
  {"id":67,"fase":"Grupo L","data":"2026-06-17","hora":"17:00","time1":"Inglaterra","flag1":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","time2":"Croácia","flag2":"🇭🇷"},
  {"id":68,"fase":"Grupo L","data":"2026-06-17","hora":"20:00","time1":"Gana","flag1":"🇬🇭","time2":"Panamá","flag2":"🇵🇦"},
  {"id":69,"fase":"Grupo L","data":"2026-06-23","hora":"17:00","time1":"Inglaterra","flag1":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","time2":"Gana","flag2":"🇬🇭"},
  {"id":70,"fase":"Grupo L","data":"2026-06-23","hora":"20:00","time1":"Panamá","flag1":"🇵🇦","time2":"Croácia","flag2":"🇭🇷"},
  {"id":71,"fase":"Grupo L","data":"2026-06-27","hora":"18:00","time1":"Panamá","flag1":"🇵🇦","time2":"Inglaterra","flag2":"🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
  {"id":72,"fase":"Grupo L","data":"2026-06-27","hora":"18:00","time1":"Croácia","flag1":"🇭🇷","time2":"Gana","flag2":"🇬🇭"},
  # 16 avos
  {"id":73,"fase":"16 Avos","data":"2026-06-28","hora":"16:00","time1":"2º A","flag1":"🏳️","time2":"2º B","flag2":"🏳️"},
  {"id":74,"fase":"16 Avos","data":"2026-06-29","hora":"14:00","time1":"1º C","flag1":"🏳️","time2":"2º F","flag2":"🏳️"},
  {"id":75,"fase":"16 Avos","data":"2026-06-29","hora":"17:30","time1":"1º E","flag1":"🏳️","time2":"3º ABCDF","flag2":"🏳️"},
  {"id":76,"fase":"16 Avos","data":"2026-06-29","hora":"22:00","time1":"1º F","flag1":"🏳️","time2":"2º C","flag2":"🏳️"},
  {"id":77,"fase":"16 Avos","data":"2026-06-30","hora":"14:00","time1":"2º E","flag1":"🏳️","time2":"2º I","flag2":"🏳️"},
  {"id":78,"fase":"16 Avos","data":"2026-06-30","hora":"18:00","time1":"1º I","flag1":"🏳️","time2":"3º CDFGH","flag2":"🏳️"},
  {"id":79,"fase":"16 Avos","data":"2026-06-30","hora":"22:00","time1":"1º A","flag1":"🏳️","time2":"3º CEFHI","flag2":"🏳️"},
  {"id":80,"fase":"16 Avos","data":"2026-07-01","hora":"13:00","time1":"1º L","flag1":"🏳️","time2":"3º EHIJK","flag2":"🏳️"},
  {"id":81,"fase":"16 Avos","data":"2026-07-01","hora":"17:00","time1":"1º G","flag1":"🏳️","time2":"3º AEHIJ","flag2":"🏳️"},
  {"id":82,"fase":"16 Avos","data":"2026-07-01","hora":"21:00","time1":"1º D","flag1":"🏳️","time2":"3º BEFIJ","flag2":"🏳️"},
  {"id":83,"fase":"16 Avos","data":"2026-07-02","hora":"16:00","time1":"1º H","flag1":"🏳️","time2":"2º J","flag2":"🏳️"},
  {"id":84,"fase":"16 Avos","data":"2026-07-02","hora":"20:00","time1":"2º K","flag1":"🏳️","time2":"2º L","flag2":"🏳️"},
  {"id":85,"fase":"16 Avos","data":"2026-07-03","hora":"00:00","time1":"1º B","flag1":"🏳️","time2":"3º EFGIJ","flag2":"🏳️"},
  {"id":86,"fase":"16 Avos","data":"2026-07-03","hora":"15:00","time1":"2º D","flag1":"🏳️","time2":"2º G","flag2":"🏳️"},
  {"id":87,"fase":"16 Avos","data":"2026-07-03","hora":"19:00","time1":"1º J","flag1":"🏳️","time2":"2º H","flag2":"🏳️"},
  {"id":88,"fase":"16 Avos","data":"2026-07-03","hora":"22:30","time1":"1º K","flag1":"🏳️","time2":"3º DEIJL","flag2":"🏳️"},
  # Oitavas
  {"id":89,"fase":"Oitavas","data":"2026-07-04","hora":"14:00","time1":"Venc. Jogo 73","flag1":"🏳️","time2":"Venc. Jogo 74","flag2":"🏳️"},
  {"id":90,"fase":"Oitavas","data":"2026-07-04","hora":"18:00","time1":"Venc. Jogo 75","flag1":"🏳️","time2":"Venc. Jogo 76","flag2":"🏳️"},
  {"id":91,"fase":"Oitavas","data":"2026-07-05","hora":"17:00","time1":"Venc. Jogo 77","flag1":"🏳️","time2":"Venc. Jogo 78","flag2":"🏳️"},
  {"id":92,"fase":"Oitavas","data":"2026-07-05","hora":"21:00","time1":"Venc. Jogo 79","flag1":"🏳️","time2":"Venc. Jogo 80","flag2":"🏳️"},
  {"id":93,"fase":"Oitavas","data":"2026-07-06","hora":"16:00","time1":"Venc. Jogo 81","flag1":"🏳️","time2":"Venc. Jogo 82","flag2":"🏳️"},
  {"id":94,"fase":"Oitavas","data":"2026-07-06","hora":"21:00","time1":"Venc. Jogo 83","flag1":"🏳️","time2":"Venc. Jogo 84","flag2":"🏳️"},
  {"id":95,"fase":"Oitavas","data":"2026-07-07","hora":"13:00","time1":"Venc. Jogo 85","flag1":"🏳️","time2":"Venc. Jogo 86","flag2":"🏳️"},
  {"id":96,"fase":"Oitavas","data":"2026-07-07","hora":"17:00","time1":"Venc. Jogo 87","flag1":"🏳️","time2":"Venc. Jogo 88","flag2":"🏳️"},
  # Quartas
  {"id":97,"fase":"Quartas","data":"2026-07-09","hora":"17:00","time1":"Venc. Oitavas 89","flag1":"🏳️","time2":"Venc. Oitavas 90","flag2":"🏳️"},
  {"id":98,"fase":"Quartas","data":"2026-07-10","hora":"16:00","time1":"Venc. Oitavas 91","flag1":"🏳️","time2":"Venc. Oitavas 92","flag2":"🏳️"},
  {"id":99,"fase":"Quartas","data":"2026-07-11","hora":"18:00","time1":"Venc. Oitavas 93","flag1":"🏳️","time2":"Venc. Oitavas 94","flag2":"🏳️"},
  {"id":100,"fase":"Quartas","data":"2026-07-11","hora":"22:00","time1":"Venc. Oitavas 95","flag1":"🏳️","time2":"Venc. Oitavas 96","flag2":"🏳️"},
  # Semis
  {"id":101,"fase":"Semifinais","data":"2026-07-14","hora":"16:00","time1":"Venc. Quartas 97","flag1":"🏳️","time2":"Venc. Quartas 98","flag2":"🏳️"},
  {"id":102,"fase":"Semifinais","data":"2026-07-15","hora":"16:00","time1":"Venc. Quartas 99","flag1":"🏳️","time2":"Venc. Quartas 100","flag2":"🏳️"},
  # 3º lugar e Final
  {"id":103,"fase":"3º Lugar","data":"2026-07-18","hora":"18:00","time1":"Perd. Semi 101","flag1":"🏳️","time2":"Perd. Semi 102","flag2":"🏳️"},
  {"id":104,"fase":"Final","data":"2026-07-19","hora":"16:00","time1":"Venc. Semi 101","flag1":"🏳️","time2":"Venc. Semi 102","flag2":"🏳️"},
]

JOGOS_MAP = {j['id']: j for j in JOGOS}

# ─── DB ──────────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS participantes (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            codigo TEXT UNIQUE NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS palpites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participante_id TEXT NOT NULL,
            jogo_id INTEGER NOT NULL,
            gols1 INTEGER NOT NULL,
            gols2 INTEGER NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(participante_id, jogo_id),
            FOREIGN KEY(participante_id) REFERENCES participantes(id)
        );
        CREATE TABLE IF NOT EXISTS resultados (
            jogo_id INTEGER PRIMARY KEY,
            gols1 INTEGER NOT NULL,
            gols2 INTEGER NOT NULL,
            time1_nome TEXT,
            time2_nome TEXT,
            atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

init_db()

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def jogo_bloqueado(jogo):
    """Retorna True se o horário do jogo já passou (UTC-3 Brasília)"""
    try:
        from datetime import timedelta
        dt_str = f"{jogo['data']} {jogo['hora']}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        # Horários no arquivo são horário de Brasília (UTC-3)
        # Converter para UTC para comparar
        dt_utc = dt + timedelta(hours=3)
        now_utc = datetime.utcnow()
        return now_utc >= dt_utc
    except:
        return False

def calc_pontos(jogo_id, g1, g2):
    conn = get_db()
    r = conn.execute('SELECT * FROM resultados WHERE jogo_id=?', (jogo_id,)).fetchone()
    conn.close()
    if not r:
        return None
    if r['gols1'] == g1 and r['gols2'] == g2:
        return 10
    rv = 1 if r['gols1'] > r['gols2'] else (2 if r['gols1'] < r['gols2'] else 0)
    pv = 1 if g1 > g2 else (2 if g1 < g2 else 0)
    return 5 if rv == pv else 0

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization','').replace('Bearer ','')
        try:
            data = jwt.decode(token, SECRET, algorithms=['HS256'])
            if data.get('role') != 'admin':
                return jsonify({'error':'Acesso negado'}), 403
        except:
            return jsonify({'error':'Token inválido'}), 401
        return f(*args, **kwargs)
    return decorated

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization','').replace('Bearer ','')
        try:
            data = jwt.decode(token, SECRET, algorithms=['HS256'])
            request.user_id = data.get('id')
            request.user_role = data.get('role')
        except:
            return jsonify({'error':'Token inválido'}), 401
        return f(*args, **kwargs)
    return decorated

# ─── ROTAS PÚBLICAS ──────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/admin')
def admin_page():
    return send_from_directory('frontend', 'admin.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    codigo = (data.get('codigo') or '').strip().upper()
    conn = get_db()
    p = conn.execute('SELECT * FROM participantes WHERE codigo=?', (codigo,)).fetchone()
    conn.close()
    if not p:
        return jsonify({'error': 'Código inválido'}), 401
    token = jwt.encode({'id': p['id'], 'nome': p['nome'], 'role': 'participante'}, SECRET, algorithm='HS256')
    return jsonify({'token': token, 'nome': p['nome'], 'id': p['id']})

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if data.get('senha') != ADMIN_PASSWORD:
        return jsonify({'error': 'Senha incorreta'}), 401
    token = jwt.encode({'role': 'admin'}, SECRET, algorithm='HS256')
    return jsonify({'token': token})

@app.route('/api/jogos')
def get_jogos():
    conn = get_db()
    resultados = {r['jogo_id']: dict(r) for r in conn.execute('SELECT * FROM resultados').fetchall()}
    conn.close()
    jogos_out = []
    for j in JOGOS:
        jo = dict(j)
        jo['bloqueado'] = jogo_bloqueado(j)
        if j['id'] in resultados:
            r = resultados[j['id']]
            jo['resultado'] = {'gols1': r['gols1'], 'gols2': r['gols2'],
                               'time1_nome': r['time1_nome'], 'time2_nome': r['time2_nome']}
        jogos_out.append(jo)
    return jsonify(jogos_out)

@app.route('/api/ranking')
def get_ranking():
    conn = get_db()
    participantes = conn.execute('SELECT * FROM participantes ORDER BY nome').fetchall()
    resultados = {r['jogo_id']: dict(r) for r in conn.execute('SELECT * FROM resultados').fetchall()}
    palpites_all = conn.execute('SELECT * FROM palpites').fetchall()
    conn.close()

    palpites_map = {}
    for p in palpites_all:
        palpites_map[(p['participante_id'], p['jogo_id'])] = p

    ranking = []
    for p in participantes:
        pts = 0; exatos = 0; vencedores = 0; np = 0
        for jid, r in resultados.items():
            pal = palpites_map.get((p['id'], jid))
            if pal:
                np += 1
                pontos = calc_pontos(jid, pal['gols1'], pal['gols2'])
                if pontos == 10: exatos += 1
                elif pontos == 5: vencedores += 1
                pts += pontos or 0
        ranking.append({'id': p['id'], 'nome': p['nome'], 'pontos': pts,
                        'exatos': exatos, 'vencedores': vencedores, 'palpites': np})
    ranking.sort(key=lambda x: (-x['pontos'], -x['exatos'], -x['vencedores']))
    return jsonify(ranking)

# ─── ROTAS PARTICIPANTE ──────────────────────────────────────────────────────
@app.route('/api/palpites', methods=['GET'])
@require_auth
def get_palpites():
    conn = get_db()
    rows = conn.execute('SELECT * FROM palpites WHERE participante_id=?', (request.user_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/palpites', methods=['POST'])
@require_auth
def salvar_palpite():
    data = request.json
    jogo_id = int(data.get('jogo_id'))
    gols1 = int(data.get('gols1'))
    gols2 = int(data.get('gols2'))
    jogo = JOGOS_MAP.get(jogo_id)
    if not jogo:
        return jsonify({'error': 'Jogo não encontrado'}), 404
    if jogo_bloqueado(jogo):
        return jsonify({'error': 'Prazo encerrado para este jogo'}), 400
    if gols1 < 0 or gols2 < 0:
        return jsonify({'error': 'Placar inválido'}), 400
    conn = get_db()
    conn.execute('''INSERT INTO palpites (participante_id, jogo_id, gols1, gols2)
                    VALUES (?,?,?,?)
                    ON CONFLICT(participante_id, jogo_id)
                    DO UPDATE SET gols1=excluded.gols1, gols2=excluded.gols2,
                    criado_em=CURRENT_TIMESTAMP''',
                 (request.user_id, jogo_id, gols1, gols2))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ─── ROTAS ADMIN ─────────────────────────────────────────────────────────────
@app.route('/api/admin/participantes', methods=['GET'])
@require_admin
def admin_get_participantes():
    conn = get_db()
    rows = conn.execute('SELECT p.*, COUNT(pal.id) as total_palpites FROM participantes p LEFT JOIN palpites pal ON p.id=pal.participante_id GROUP BY p.id ORDER BY p.nome').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/participantes', methods=['POST'])
@require_admin
def admin_criar_participante():
    data = request.json
    nome = data.get('nome','').strip()
    if not nome:
        return jsonify({'error': 'Nome obrigatório'}), 400
    pid = str(uuid.uuid4())
    # Gera código: 3 letras do nome + 4 dígitos aleatórios
    import random, string
    letras = ''.join(c for c in nome.upper() if c.isalpha())[:3].ljust(3,'X')
    digitos = ''.join(random.choices(string.digits, k=4))
    codigo = letras + digitos
    # Garante unicidade
    conn = get_db()
    tentativas = 0
    while conn.execute('SELECT 1 FROM participantes WHERE codigo=?', (codigo,)).fetchone():
        digitos = ''.join(random.choices(string.digits, k=4))
        codigo = letras + digitos
        tentativas += 1
        if tentativas > 20:
            codigo = str(uuid.uuid4())[:8].upper()
            break
    try:
        conn.execute('INSERT INTO participantes (id, nome, codigo) VALUES (?,?,?)', (pid, nome, codigo))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({'error': str(e)}), 400
    conn.close()
    return jsonify({'id': pid, 'nome': nome, 'codigo': codigo})

@app.route('/api/admin/participantes/<pid>', methods=['DELETE'])
@require_admin
def admin_deletar_participante(pid):
    conn = get_db()
    conn.execute('DELETE FROM palpites WHERE participante_id=?', (pid,))
    conn.execute('DELETE FROM participantes WHERE id=?', (pid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/admin/resultados', methods=['POST'])
@require_admin
def admin_salvar_resultado():
    data = request.json
    jogo_id = int(data.get('jogo_id'))
    gols1 = int(data.get('gols1'))
    gols2 = int(data.get('gols2'))
    time1_nome = data.get('time1_nome', '')
    time2_nome = data.get('time2_nome', '')
    if gols1 < 0 or gols2 < 0:
        return jsonify({'error': 'Placar inválido'}), 400
    conn = get_db()
    conn.execute('''INSERT INTO resultados (jogo_id, gols1, gols2, time1_nome, time2_nome, atualizado_em)
                    VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)
                    ON CONFLICT(jogo_id) DO UPDATE SET
                    gols1=excluded.gols1, gols2=excluded.gols2,
                    time1_nome=excluded.time1_nome, time2_nome=excluded.time2_nome,
                    atualizado_em=CURRENT_TIMESTAMP''',
                 (jogo_id, gols1, gols2, time1_nome, time2_nome))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/admin/resultados/<int:jogo_id>', methods=['DELETE'])
@require_admin
def admin_deletar_resultado(jogo_id):
    conn = get_db()
    conn.execute('DELETE FROM resultados WHERE jogo_id=?', (jogo_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/admin/palpites/<int:jogo_id>')
@require_admin
def admin_ver_palpites(jogo_id):
    conn = get_db()
    rows = conn.execute('''SELECT p.nome, pal.gols1, pal.gols2, pal.criado_em
                           FROM palpites pal JOIN participantes p ON pal.participante_id=p.id
                           WHERE pal.jogo_id=? ORDER BY p.nome''', (jogo_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Bolão Copa 2026 rodando em http://localhost:{port}")
    print(f"   Admin: http://localhost:{port}/admin")
    print(f"   Senha admin: {ADMIN_PASSWORD}")
    app.run(host='0.0.0.0', port=port, debug=False)
