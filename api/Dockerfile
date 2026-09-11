FROM python:3.10.4

WORKDIR /app 

ENV FLASK_APP=glygen_ai_api
ENV FLASK_ENV=production

COPY ./requirements.txt .
RUN pip install -r requirements.txt 

# copy wheel distribution and install it 
COPY ./dist/glygen_ai_api-1.0-py3-none-any.whl .
RUN pip install glygen_ai_api-1.0-py3-none-any.whl

COPY . .

ENTRYPOINT FLASK_APP=glygen_ai_api gunicorn -b :80 'glygen_llm_api:create_app()' --timeout 120 --graceful-timeout 60
