# ⚽ Bolão Copa 2026

Sistema completo de bolão para a Copa do Mundo 2026, com backend Python/Flask, banco SQLite e frontend HTML puro.

---

## 📦 Requisitos

- Python 3.8+
- pip

---

## 🚀 Instalação e Execução

### 1. Instale as dependências

```bash
pip install flask flask-cors pyjwt
```

### 2. Configure (opcional)

Edite as variáveis de ambiente antes de iniciar ou exporte-as:

```bash
export ADMIN_PASSWORD="minha-senha-segura"
export SECRET_KEY="chave-secreta-longa-e-aleatoria"
export PORT=5000
```

> ⚠️ **Importante:** Troque `ADMIN_PASSWORD` e `SECRET_KEY` antes de colocar em produção!

### 3. Inicie o servidor

```bash
bash start.sh
```

Ou diretamente:

```bash
cd backend
python3 app.py
```

---

## 🌐 Endereços

| Página | URL |
|--------|-----|
| Participantes | `http://localhost:5000` |
| Admin | `http://localhost:5000/admin` |

---

## 🔑 Como funciona

### Para o Administrador
1. Acesse `/admin` e faça login com a senha configurada
2. Na aba **Participantes**: cadastre cada pessoa — um código único é gerado automaticamente (ex: `JOA4821`)
3. Clique em **"Copiar mensagem para WhatsApp"** para enviar o código a cada participante
4. Na aba **Resultados**: insira o placar oficial de cada jogo após o apito final
5. Para jogos do mata-mata, você pode digitar o nome dos times
6. Na aba **Ranking**: acompanhe a classificação em tempo real

### Para os Participantes
1. Acesse o link do site (ex: `http://seu-servidor.com`)
2. Digite o código recebido (ex: `JOA4821`)
3. Na aba **Jogos**: clique em "Palpitar" para cada jogo
4. Palpites são **travados automaticamente** no horário de cada partida
5. Após o admin inserir o resultado, os pontos aparecem automaticamente

---

## 🏆 Pontuação

| Acerto | Pontos |
|--------|--------|
| Placar exato (ex: 2×1 e era 2×1) | **10 pts** |
| Vencedor certo (ex: palpitou 3×1, foi 1×0) | **5 pts** |
| Errou o vencedor | **0 pts** |
| Empate: acertou que seria empate | **5 pts** |
| Empate: placar exato do empate | **10 pts** |

---

## ☁️ Deploy em Produção

### Opção A — VPS simples (Render, Railway, Fly.io)

Adicione um `Procfile`:
```
web: python backend/app.py
```

### Opção B — Servidor próprio com Nginx

```nginx
server {
    listen 80;
    server_name bolao.seusite.com;
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
    }
}
```

Inicie com:
```bash
PORT=5000 ADMIN_PASSWORD=sua-senha bash start.sh
```

---

## 📁 Estrutura

```
bolao/
├── backend/
│   └── app.py          # API Flask + lógica
├── frontend/
│   ├── index.html      # Página dos participantes
│   └── admin.html      # Painel do administrador
├── start.sh            # Script de inicialização
└── README.md
```

O banco de dados `bolao.db` é criado automaticamente em `backend/` na primeira execução.

---

## 🔒 Segurança

- Senhas nunca são armazenadas no banco (só JWT)
- Palpites são bloqueados via verificação de horário no servidor (não só no frontend)
- Para produção: use HTTPS e troque `SECRET_KEY`
