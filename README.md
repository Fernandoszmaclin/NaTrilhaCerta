# NaTrilhaCerta - Plataforma de Ecoturismo

![Logo da NaTrilhaCerta](https://raw.githubusercontent.com/placeholder-logo.png) <!-- Substituir pela URL real da logo se houver -->

Bem-vindo ao **NaTrilhaCerta**, uma plataforma completa desenvolvida em Django para gestão e reserva de expedições de ecoturismo, trilhas e viagens de aventura.

## 📖 Sobre o Projeto

O site permite que entusiastas de aventura explorem pacotes de viagens, consultem detalhes sobre destinos, verifiquem a dificuldade de cada trilha e realizem reservas online. 

### Principais Funcionalidades:
- **Catálogo de Expedições:** Lista dinâmica de viagens com filtros por preço, data e local.
- **Sistema de Reservas:** Registro de interesse em expedições diretamente pelo site.
- **Área Administrativa:** Gestão completa de pacotes, imagens, usuários e reservas via Django Admin.
- **Autenticação:** Sistema de login e cadastro para usuários.
- **Filtros Avançados:** Busca por nível de dificuldade, datas mais próximas e valores.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.14+
- **Framework Web:** [Django 6.0](https://www.djangoproject.com/)
- **Banco de Dados:** PostgreSQL (Configurado para produção/desenvolvimento)
- **Frontend:** HTML5, CSS3, JavaScript e Bootstrap 5
- **Gestão de Formulários:** Django Crispy Forms
- **Processamento de Imagens:** Pillow

---

## 🚀 Como Rodar o Projeto

Siga os passos abaixo para configurar o ambiente de desenvolvimento localmente.

### 1. Pré-requisitos
Certifique-se de ter instalado em sua máquina:
- Python (Versão 3.14 recomendada)
- PostgreSQL
- Git

### 2. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/Turismo.git
cd NaTrilhaCerta
```

### 3. Configurar o Ambiente Virtual
```bash
# Criar o ambiente virtual
python -m venv .venv

# Ativar o ambiente (Windows)
.venv\Scripts\activate

# Ativar o ambiente (Linux/Mac)
source .venv/bin/activate
```

### 4. Instalar as Dependências
Como o projeto utiliza `Pipfile`, você pode instalar via `pipenv` ou usar o `pip`:
```bash
pip install django django-crispy-forms crispy-bootstrap5 psycopg2-binary pillow
```

### 5. Configurar o Banco de Dados
O projeto está configurado para utilizar **PostgreSQL**. Certifique-se de configurar seu banco de dados local ou ambiente e atualizar as configurações no arquivo `TrilhaCerta/settings.py` (ou utilize variáveis de ambiente).

Os parâmetros necessários incluem:
- Nome do Banco de Dados
- Usuário
- Senha
- Host e Porta


### 6. Executar Migrações
Com o banco configurado e ativo, execute:
```bash
cd TrilhaCerta
python manage.py migrate
```

### 7. Criar um Superusuário (Admin)
Para acessar o painel de controle e cadastrar as expedições:
```bash
python manage.py createsuperuser
```

### 8. Iniciar o Servidor
```bash
python manage.py runserver
```
O site estará disponível em: `http://127.0.0.1:8000/`

---

## 📁 Estrutura do Projeto

- `core/`: Aplicativo principal contendo modelos, views e templates.
- `media/`: Diretório para upload das imagens das expedições.
- `static/`: Arquivos estáticos (CSS, JS, Imagens do layout).
- `TrilhaCerta/`: Configurações globais do projeto Django.

---

## 🤝 Contribuição

1. Faça um Fork do projeto.
2. Crie uma Branch para sua feature (`git checkout -b feature/NovaFeature`).
3. Comite suas mudanças (`git commit -m 'Adicionando nova feature'`).
4. Push para a Branch (`git push origin feature/NovaFeature`).
5. Abra um Pull Request.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
*Desenvolvido por Fernando Sozo Marcolin*