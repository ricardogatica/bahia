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
| `k` | Liberar el puerto seleccionado (mata todos sus procesos) |
| `r` | Refrescar la lista |
| `q` | Salir |

### Comandos

| Comando | Acción |
|---------|--------|
| `bahia` | Abrir el monitor de puertos |
| `bahia --update` | Actualizar a la última versión |
| `bahia --version` | Ver la versión instalada |
| `bahia --help` | Ver la ayuda |

## Actualizaciones

Al abrir Bahia se comprueba en segundo plano (sin bloquear) si hay una versión
más nueva publicada. Si la hay, aparece un aviso arriba de la tabla. La
comprobación se cachea por 24 horas para no consultar la red en cada arranque.

Para actualizar:

```sh
bahia --update
```

Esto actualiza el código y las dependencias en `~/.bahia` vía `git`. Si tu
instalación no es un checkout de git, vuelve a ejecutar el instalador remoto
automáticamente.

## Características

✅ Lista puertos TCP abiertos en el sistema
✅ Muestra proceso, PID y usuario propietario
✅ Libera puertos terminando todos sus procesos (incluso si tiene varios PIDs)
✅ Interfaz sobria y minimalista
✅ Actualización rápida
✅ Aviso de nuevas versiones al arrancar y `bahia --update` para actualizar

## Requisitos

- macOS
- Python 3.8+
- `lsof` (incluido en macOS)

## Estructura

```
.
├── bahia.py           # App principal
├── bahia              # Wrapper ejecutable
├── setup.py           # Setup para instalación
├── requirements.txt   # Dependencias
└── README.md          # Este archivo
```

## Desarrollo

Para modificar la app:

```bash
# Editar bahia.py
vim bahia.py

# Probar cambios
python3 bahia.py
```

## Notas

- La app requiere acceso a `lsof` (comando del sistema)
- Para terminar procesos de otros usuarios, pueden ser necesarios permisos de administrador
- Usa `kill -9` para terminar procesos (SIGKILL)

## Autor

Ricardo Gatica - hola@ricardogatica.com
