#!/bin/bash
echo "🧹 Limpiando Docker..."
docker compose down -v
docker system prune -a --volumes -f
docker system df
echo "✅ Limpio!"
