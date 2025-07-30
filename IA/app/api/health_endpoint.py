from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import time
import os
from datetime import datetime

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, Any]
    uptime_seconds: float

class ServiceStatus(BaseModel):
    status: str
    response_time_ms: float
    details: Dict[str, Any] = {}

# Variable global para tracking de uptime
start_time = time.time()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint completo de health check que verifica todos los servicios
    """
    services = {}
    overall_status = "healthy"

    # Check DynamoDB
    try:
        dynamo_start = time.time()
        from app.core.aws_clients import get_dynamodb_client
        client = get_dynamodb_client()
        # Test simple: listar tablas
        response = client.list_tables()
        dynamo_time = (time.time() - dynamo_start) * 1000

        services["dynamodb"] = ServiceStatus(
            status="healthy",
            response_time_ms=dynamo_time,
            details={"table_count": len(response.get("TableNames", []))}
        )
    except Exception as e:
        services["dynamodb"] = ServiceStatus(
            status="unhealthy",
            response_time_ms=0,
            details={"error": str(e)}
        )
        overall_status = "degraded"

    # Check OpenSearch
    try:
        opensearch_start = time.time()
        from app.core.aws_clients import get_opensearch_client
        client = get_opensearch_client()
        # Test simple: cluster health
        health = client.cluster.health()
        opensearch_time = (time.time() - opensearch_start) * 1000

        services["opensearch"] = ServiceStatus(
            status="healthy" if health.get("status") in ["green", "yellow"] else "unhealthy",
            response_time_ms=opensearch_time,
            details={
                "cluster_status": health.get("status"),
                "number_of_nodes": health.get("number_of_nodes")
            }
        )
    except Exception as e:
        services["opensearch"] = ServiceStatus(
            status="unhealthy",
            response_time_ms=0,
            details={"error": str(e)}
        )
        overall_status = "degraded"

    # Check Bedrock
    try:
        bedrock_start = time.time()
        from app.core.aws_clients import get_bedrock_client
        client = get_bedrock_client()
        # Test simple: listar modelos disponibles
        models = client.list_foundation_models()
        bedrock_time = (time.time() - bedrock_start) * 1000

        services["bedrock"] = ServiceStatus(
            status="healthy",
            response_time_ms=bedrock_time,
            details={"available_models": len(models.get("modelSummaries", []))}
        )
    except Exception as e:
        services["bedrock"] = ServiceStatus(
            status="unhealthy",
            response_time_ms=0,
            details={"error": str(e)}
        )
        overall_status = "degraded"

    # Check PostgreSQL
    try:
        postgres_start = time.time()
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM properties;")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        postgres_time = (time.time() - postgres_start) * 1000

        services["postgresql"] = ServiceStatus(
            status="healthy",
            response_time_ms=postgres_time,
            details={"properties_count": count}
        )
    except Exception as e:
        services["postgresql"] = ServiceStatus(
            status="unhealthy",
           response_time_ms=0,
            details={"error": str(e)}
        )
        overall_status = "degraded"

    uptime = time.time() - start_time

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version=os.getenv("APP_VERSION", "1.0.0"),
        services={k: v.dict() for k, v in services.items()},
        uptime_seconds=uptime
    )

@router.get("/health/simple")
async def simple_health_check():
    """
    Health check simple para load balancers
    """
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@router.get("/metrics")
async def get_metrics():
    """
    Endpoint básico de métricas para monitoreo
    """
    uptime = time.time() - start_time

    return {
        "uptime_seconds": uptime,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENV", "unknown"),
        "region": os.getenv("AWS_REGION", "unknown")
    }
