# NaTrilhaCerta 🌲

**Transformando trilhas em experiências inesquecíveis.**

O **NaTrilhaCerta** é uma plataforma de gestão de ecoturismo desenvolvida para facilitar o encontro entre aventureiros e expedições. O foco do sistema é oferecer uma experiência fluida de descoberta e reserva de viagens, enquanto fornece ferramentas robustas para o gerenciamento de pacotes turísticos.

---

## ✨ Funcionalidades Principais

O sistema é dividido em dois grandes eixos: a experiência do usuário (cliente) e o painel de controle (administrativo).

### 🖥️ Para o Viajante (Cliente)
- **Catálogo Inteligente:** Navegação por cards visuais que destacam o destino, a data e o valor da aventura.
- **Filtros Dinâmicos:** Busca personalizada por preço (maior/menor), destino (por estado) e proximidade de data.
- **Detalhes da Expedição:** Informações completas sobre o roteiro, nível de dificuldade (Fácil a Extremo), vagas disponíveis e galeria de fotos.
- **Sistema de Reservas:** Botão "Reservar Agora" que valida se o usuário está logado. Se estiver, direciona para o contato direto; se não, abre um fluxo rápido de login/cadastro.
- **Perfil do Usuário:** Área segura para cadastro e login, garantindo que cada aventureiro tenha seus dados salvos para futuras trilhas.

### ⚙️ Para a Gestão (Administrativo)
- **Painel de Controle:** Gestão completa via Django Admin para adicionar, editar ou remover expedições em tempo real.
- **Controle de Vagas:** Atualização automática da disponibilidade; expedições sem vagas são marcadas visualmente como "Esgotadas".
- **Gestão de Mídia:** Upload simplificado de múltiplas fotos para cada destino.
- **Acompanhamento de Reservas:** Lista organizada de todos os usuários que demonstraram interesse em cada pacote.

---

## 🛠️ Tecnologias de Base

O projeto utiliza tecnologias modernas para garantir estabilidade e performance:
- **Backend:** Python com o framework Django 6.
- **Banco de Dados:** PostgreSQL para armazenamento seguro e relacional.
- **Interface:** HTML5, CSS3 (Vanilla) e JavaScript, potencializados com Bootstrap 5 para total responsividade.

---

## 🚀 Como Preparar o Ambiente de Desenvolvimento

Caso precise rodar o projeto localmente para testes:

1. **Baixe o Código:** Clone o repositório em sua máquina.
2. **Ambiente Virtual:** Crie e ative um ambiente `.venv`.
3. **Dependências:** Instale os requisitos com `pip install django django-crispy-forms crispy-bootstrap5 psycopg2-binary pillow`.
4. **Banco de Dados:** Configure uma instância local do PostgreSQL e atualize o `settings.py`.
5. **Migrações e Admin:** Execute `python manage.py migrate` e crie seu acesso com `python manage.py createsuperuser`.
6. **Execução:** Rode `python manage.py runserver` e acesse `localhost:8000`.

---
*Este é um projeto proprietário desenvolvido por **Fernando Sozo Marcolin***.