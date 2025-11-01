# Colmeia API

API para o Quiz de Análise de Crédito da Colmeia.

Este projeto é um backend desenvolvido em FastAPI que serve um quiz sobre análise de crédito e fornece endpoints para visualização de um dashboard e histórico de resultados.

## Tecnologias Utilizadas

* Python 3
* FastAPI
* Uvicorn (para execução)

## Instalação e Execução Local

1.  **Clone o repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO]
    cd [NOME_DO_DIRETORIO]
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    (Assumindo que você tenha um arquivo `requirements.txt` com `fastapi`, `uvicorn`, etc.)
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação:**
    O servidor será iniciado em `http://127.0.0.1:8000`.
    ```bash
    uvicorn app.main:app --reload
    ```

## Endpoints da API

A API está documentada automaticamente e pode ser acessada via Swagger UI em `http://127.0.0.1:8000/docs` ou ReDoc em `http://127.0.0.1:8000/redoc` quando o servidor estiver em execução.

### Root

* `GET /`
    * Retorna uma mensagem de boas-vindas à API.
    * **Resposta:**
        ```json
        {
          "message": "Welcome to the Colmeia API!"
        }
        ```

### Quiz (Prefixo: `/api/quiz`)

* `GET /questions`
    * Retorna a lista de todas as perguntas do quiz.
    * Depende de `quiz_service.get_all_questions()`.

* `POST /result`
    * Recebe uma lista de respostas do usuário (`UserAnswer`).
    * Processa e calcula o resultado final do quiz (`FinalResult`).
    * Depende de `quiz_service.process_quiz_results(answers)`.

### Dashboard & History (Prefixo: `/api`)

* `GET /dashboard`
    * Carrega e retorna os dados atuais do dashboard (`DashboardState`).
    * Depende de `dashboard_service.load_dashboard_data()`.

* `GET /history`
    * Retorna os dados do histórico de quizzes.
    * Depende de `dashboard_service.get_history_data()`.

* `POST /reset`
    * Reseta os dados do dashboard para seu estado inicial.
    * Retorna o estado do dashboard após o reset.
    * Depende de `dashboard_service.reset_dashboard()`.