docker compose build
IF "%1"=="prod" (
    docker build -f Dockerfile --tag trading-simulator:prod .
) ELSE (
    docker build -f Dockerfile-dev --tag trading-simulator:dev .
)