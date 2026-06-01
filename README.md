# Ports App - Monitor de Puertos macOS

Aplicación terminal minimalista para revisar puertos abiertos en macOS y terminar procesos.

## Instalación Rápida

### Opción 1: Ejecutar Directamente

```bash
# Instalar dependencias
pip install textual

# Ejecutar
python3 ports_app.py
```

### Opción 2: Instalar como Comando Global

```bash
# Desde la carpeta del proyecto
pip install -e .

# Luego ejecutar desde cualquier lugar
ports-app
```

### Opción 3: Homebrew (Próximamente)

```bash
brew install ricardogatica/ports-app/ports-app
ports-app
```

## Uso

Ejecuta la app:
```bash
ports-app
```

### Controles

| Tecla | Acción |
|-------|--------|
| `↑` `↓` | Navegar entre puertos |
| `k` | Matar el proceso seleccionado |
| `r` | Refrescar la lista |
| `q` | Salir |

## Características

✅ Lista puertos TCP abiertos en el sistema
✅ Muestra proceso, PID y usuario propietario
✅ Termina procesos desde la interfaz
✅ Interfaz sobria y minimalista
✅ Actualización rápida

## Requisitos

- macOS
- Python 3.8+
- `lsof` (incluido en macOS)

## Estructura

```
.
├── ports_app.py       # App principal
├── ports-app          # Wrapper ejecutable
├── setup.py           # Setup para instalación
├── requirements.txt   # Dependencias
└── README.md          # Este archivo
```

## Desarrollo

Para modificar la app:

```bash
# Editar ports_app.py
vim ports_app.py

# Probar cambios
python3 ports_app.py
```

## Notas

- La app requiere acceso a `lsof` (comando del sistema)
- Para terminar procesos de otros usuarios, pueden ser necesarios permisos de administrador
- Usa `kill -9` para terminar procesos (SIGKILL)

## Autor

Ricardo - ricardogatica@mine-class.cl
