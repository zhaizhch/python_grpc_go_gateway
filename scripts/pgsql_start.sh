source ./scripts/.env
docker run --name postgres-prod \
  -e POSTGRES_USER=${DB_USER:-postgres} \
  -e POSTGRES_PASSWORD=${DB_PASSWORD} \
  -e POSTGRES_DB=${DB_NAME:-mydatabase} \
  -p ${DB_PORT:-5432}:5432 \
  --restart unless-stopped \
  -d postgres:15

sleep 1
cat ./scripts/construction_progress.sql | docker exec -i postgres-prod psql -U "$DB_USER" -d "$DB_NAME"