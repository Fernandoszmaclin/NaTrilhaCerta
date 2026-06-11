# Na Trilha Certa 🏍️

> Plataforma web completa para reserva de expedições off-road pelo Brasil e América do Sul.

---

## Sobre o Projeto

A **Na Trilha Certa** é uma operadora profissional de turismo de aventura especializada em motocicletas off-road. Este repositório contém a plataforma digital desenvolvida para a empresa, que permite aos clientes visualizar o calendário de expedições, realizar reservas online, efetuar pagamentos via PIX e gerenciar toda a jornada pós-compra de forma autônoma.

O projeto nasceu da necessidade de digitalizar um negócio 100% presencial/WhatsApp, entregando ao cliente uma experiência moderna, segura e mobile-first.

---

## O Produto

As expedições da Na Trilha Certa combinam **adrenalina extrema** com **segurança profissional** em destinos como serras, chapadas, dunas e travessias fluviais pelo interior do Brasil.

### O que está incluso em cada expedição

| Item | Detalhe |
|---|---|
| **Segurança 100%** | Equipe de resgate e mecânicos experientes acompanhando toda a rota |
| **Trilhas Inéditas** | Roteiros mapeados exclusivamente para enduro e Big Trail |
| **Carro de Apoio** | Bagagem e peças sobressalentes transportadas com segurança |
| **Registro Épico** | Fotógrafo profissional capturando cada momento da aventura |

### Níveis de dificuldade

- Fácil — Iniciantes e passeios em família
- Moderado — Pilotos com experiência em terra batida
- Difícil — Enduro técnico, relevos e lama
- Extremo — Expedições de vários dias em terrenos adversos

---

## Funcionalidades da Plataforma

### Para o cliente
- **Catálogo de expedições** com galeria de fotos, datas, destino, dificuldade e vagas em tempo real
- **Checkout online** com geração de cobrança PIX (copia-e-cola + QR Code)
- **Área do cliente** — acompanhamento de reservas, status de pagamento e histórico
- **Ficha Médica digital** — preenchimento obrigatório pós-pagamento diretamente pelo painel
- **Lista de espera** automática quando uma expedição esgota
- **Cancelamento com estorno** processado automaticamente via webhook do gateway

### Para a operação
- **Painel administrativo** (Django Admin) para gestão de expedições, imagens, reservas e fichas médicas
- **Webhook seguro** (HMAC-SHA256) para receber confirmações do gateway de pagamento
- **Rate limiting** por IP em todos os endpoints críticos (login, cadastro, checkout)
- **Cache compartilhado** configurável: Redis (produção) → DatabaseCache (fallback multi-worker) → LocMem (dev)

---

## Stack Técnica

| Camada | Tecnologia |
|---|---|
| **Back-end** | Python · Django · Gunicorn |
| **Banco de dados** | PostgreSQL (produção) · SQLite (desenvolvimento) |
| **Cache / Rate limit** | Redis · Django Cache Framework |
| **Front-end** | Bootstrap 5 · Vanilla JS · CSS3 (glassmorphism + animações AOS) |
| **Pagamentos** | Integração via webhook (Pix) com validação HMAC |
| **Segurança** | CSRF · HSTS · Cookies seguros · `select_for_update` nas transações |
| **Infraestrutura** | Variáveis de ambiente via `.env` · Configuração pronta para deploy com proxy reverso |

---

## Rodando Localmente

### Pré-requisitos
- Python 3.11+
- Pipenv (`pip install pipenv`)

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/Fernandoszmaclin/NaTrilhaCerta.git
cd NaTrilhaCerta

# 2. Instale as dependências
pipenv install

# 3. Configure o ambiente
cp .env.example .env
# Edite o .env com suas variáveis (SECRET_KEY, banco de dados, etc.)

# 4. Rode as migrações
cd TrilhaCerta
pipenv run python manage.py migrate

# 5. Crie um superusuário para o Admin
pipenv run python manage.py createsuperuser

# 6. Inicie o servidor
pipenv run python manage.py runserver
```

Acesse `http://localhost:8000` — o Admin fica em `http://localhost:8000/admin/`.

> **Nota:** Para usar o cache compartilhado sem Redis (ambiente multi-worker), rode também:
> `pipenv run python manage.py createcachetable`

---

## Estrutura do Projeto

```
NaTrilhaCerta/
├── TrilhaCerta/
│   ├── core/
│   │   ├── models.py        # Expedição, Reserva, Pagamento, FichaMedica
│   │   ├── views.py         # Views finas — só parsing e tradução de erros
│   │   ├── services.py      # Regras de negócio (checkout, cancelamento, webhook)
│   │   ├── forms.py         # Validação de entrada
│   │   ├── urls.py          # Roteamento da aplicação e API v1
│   │   ├── admin.py         # Painel administrativo customizado
│   │   └── templates/       # HTML (Django Templates + Bootstrap 5)
│   ├── static/
│   │   ├── css/base.css     # Design system, glassmorphism, utilitários mobile
│   │   └── js/base.js       # Carrossel, lightbox, toasts, clipboard
│   └── TrilhaCerta/
│       └── settings.py      # Configuração por ambiente (dev/prod)
├── .env.example             # Variáveis de ambiente documentadas
└── Pipfile                  # Dependências do projeto
```

---

## Redes Sociais

- Instagram: [@trilhacertaturismo](https://www.instagram.com/trilhacertaturismo/)
- Facebook: [Na Trilha Certa Turismo](https://www.facebook.com/profile.php?id=61561486201708)

---

*Projeto desenvolvido como produto real para operadora de turismo de aventura. Repositório público para fins de portfólio.*
