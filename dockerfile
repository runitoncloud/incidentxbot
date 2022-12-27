FROM node:16-bullseye as frontend

WORKDIR /app
COPY ./frontend/public/ ./public
COPY ./frontend/src/ ./src
COPY ./frontend/package.json .
COPY ./frontend/package-lock.json .
COPY ./frontend/.eslintrc.json .
COPY ./frontend/.prettierrc .

RUN npm install &&\
  npm run build

FROM python:3.11 as base

# Copy only the relevant Python files into the container.
COPY --from=frontend /app/build /incidentxbot/app
COPY ./backend/bot /incidentxbot/bot
COPY ./backend/requirements.txt /incidentxbot
COPY ./backend/config.py /incidentxbot
COPY ./backend/variables.py /incidentxbot
COPY ./backend/main.py /incidentxbot
COPY ./backend/templates /incidentxbot/templates
COPY ./scripts/wait-for-it.sh /incidentxbot/wait-for-it.sh

# Set the work directory to the app folder.
WORKDIR /incidentxbot

# Install Python dependencies.
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 3000

CMD ["python3", "main.py"]

FROM base as production
