# projeto_final: Sistema de gerenciamento e cadastro de consultas médicas. Permite cadastro, login, logout e dashboard personalizado de acordo com o tipo de usuário (Médico, Atendente ou Paciente).

## Tecnologias utilizadas
- Python 3.11
- Django 5.2.6
- HTML, CSS (para templates modernos e responsivos)
- SQLite (banco de dados padrão do Django)

## Instalação

1. **Clonar o repositório**
- git clone https://github.com/hwtcp/projeto_final.git
- cd projeto_final
2. **Criar e ativar um ambiente virtual**
  No windows:
- python -m venv venv
- venv\Scripts\activate
  No Linux:
- python3 -m venv venv
- source venv/bin/activate
3. **Instalar dependências**
- pip install -r requirements.txt
4. **Configurar o projeto**
  Aplicar migrações:
- python manage.py makemigrations
- python manage.py migrate

## Execução

1. **Executar o projeto**
- python manage.py runserver
2. **Funcionalidades**
- Usuário customizado: modelo Usuario com campos adicionais: nome completo, CPF, data de nascimento, endereço, telefone e tipo de usuário.
- Cadastro interno: administradores podem cadastrar médicos, atendentes e pacientes.
- Auto-cadastro de pacientes: usuários não autenticados podem criar conta automaticamente.
- Login e Logout: autenticação segura usando username ou CPF.
- Dashboard dinâmico: menu e conteúdo adaptado ao tipo de usuário.
- Controle de acesso: restrições de acordo com perfil (admin, médico, atendente ou paciente).