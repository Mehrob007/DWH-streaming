FROM apache/superset:latest
USER root
RUN (uv pip install clickhouse-connect) || (pip install clickhouse-connect)
USER superset

