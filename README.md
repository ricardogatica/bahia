# Bahia - Monitor de Puertos macOS

Aplicación terminal minimalista para revisar puertos abiertos en macOS y terminar procesos.

## Instalación Rápida (una línea)

Igual que oh-my-zsh, con `curl`:

```sh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ricardogatica/bahia/main/install.sh)"
```

O con `wget`:

```sh
sh -c "$(wget -qO- https://raw.githubusercontent.com/ricardogatica/bahia/main/install.sh)"
```

El instalador descarga Bahia en `~/.bahia`, crea un entorno virtual aislado con las
dependencias, e instala el comando `bahia` en tu `PATH`. Luego abre una terminal nueva
y escribe:

```sh
bahia
```

### Desinstalar

```sh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ricardogatica/bahia/main/uninstall.sh)"
```

## Instalación Alternativa (desarrollo)

```bash
# Desde la carpeta del proyecto
pip install -e .

# Luego ejecutar desde cualquier lugar
bahia
```

## Uso

Ejecuta la app:
```bash
bahia
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
