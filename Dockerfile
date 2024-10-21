FROM python:3.9
ENV PORT=8080
ENV MPLCONFIGDIR=/tmp/.matplotlib

# Install requirements
COPY visual-analytics-shiny/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Add user an change working directory and user
RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /home/app
RUN chown app:app -R /home/app
USER app

# Copy the app
COPY visual-analytics-shiny .

# Run app on port 8080
EXPOSE $PORT
CMD uvicorn app:app --host 0.0.0.0 --port $PORT
