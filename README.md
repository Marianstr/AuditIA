# AuditIA 🔍

Sistema inteligente de auditoría de presencia digital y captación de clientes para agencias web.

## ¿Qué hace?

AuditIA analiza la presencia digital de negocios y los clasifica según su potencial como clientes:
- **Caliente** (70+ puntos): presencia digital sólida
- **Tibio** (40-69 puntos): presencia parcial, oportunidad de mejora
- **Frío** (0-39 puntos): poca o nula presencia digital — cliente ideal para una agencia web

## Módulos

- `scoring/` — Lógica de puntuación de leads
- `tests/` — Pruebas unitarias y funcionales

## Cómo ejecutar las pruebas

```bash
python3 -m pytest tests/ -v
```

## Cobertura de código

```bash
python3 -m coverage run -m pytest tests/ && python3 -m coverage report --include="scoring/*,tests/*"
```

## Herramientas utilizadas

- Python 3.9
- pytest
- coverage.py
- GitHub Actions (CI/CD)
- Claude (asistencia con IA)

## Resultado de cobertura

| Archivo | Cobertura |
|---|---|
| scoring/lead_scorer.py | 100% |
| tests/ | 100% |
| **TOTAL** | **100%** |