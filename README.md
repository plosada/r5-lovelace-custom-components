# Home Assistant Lovelace Custom Components

Repositorio unificado que combina múltiples componentes personalizados de Lovelace para Home Assistant, facilitando la gestión centralizada de actualizaciones.

## Componentes Incluidos

### 1. Card-Mod
- **Fuente original**: https://github.com/thomasloven/lovelace-card-mod
- **Descripción**: Permite aplicar estilos CSS a prácticamente cualquier tarjeta de Lovelace
- **Archivos**: `card-mod/`

### 2. Fold Entity Row
- **Fuente original**: https://github.com/thomasloven/lovelace-fold-entity-row
- **Descripción**: Fila plegable para tarjetas de entidades que contiene otras filas
- **Archivos**: `fold-entity-row/`

## Estructura del Repositorio

```
ha-lovelace-custom-components/
├── README.md
├── update_components.py
├── components_config.json
├── .github/
│   └── workflows/
│       └── update-components.yml
├── card-mod/
│   ├── card-mod.js
│   ├── README.md
│   └── version.json
├── fold-entity-row/
│   ├── fold-entity-row.js
│   ├── README.md
│   └── version.json
└── docs/
    ├── installation.md
    ├── card-mod-usage.md
    └── fold-entity-row-usage.md
```

## Instalación

### Opción 1: Instalación Manual

1. Clona este repositorio en tu directorio `config/www/` de Home Assistant:
   ```bash
   cd /config/www/
   git clone https://github.com/tu-usuario/ha-lovelace-custom-components.git
   ```

2. Agrega los recursos a tu configuración de Lovelace:
   ```yaml
   # configuration.yaml
   frontend:
     extra_module_url:
       - /local/ha-lovelace-custom-components/card-mod/card-mod.js
       - /local/ha-lovelace-custom-components/fold-entity-row/fold-entity-row.js
   ```

### Opción 2: Instalación vía HACS (Repositorio Personalizado)

1. Ve a HACS → Frontend → Menú (tres puntos) → Repositorios personalizados
2. Agrega la URL: `https://github.com/tu-usuario/ha-lovelace-custom-components`
3. Categoría: Lovelace
4. Instala desde HACS

## Gestión de Actualizaciones

### Actualización Manual
```bash
python update_components.py
```

### Actualización Automática
El repositorio incluye un workflow de GitHub Actions que verifica actualizaciones semanalmente y crea PRs automáticamente.

## Configuración de Componentes

### Card-Mod
```yaml
# Ejemplo básico
card_mod:
  style: |
    ha-card {
      border-radius: 15px;
      box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
```

### Fold Entity Row
```yaml
# Ejemplo básico
type: entities
entities:
  - type: custom:fold-entity-row
    head: light.living_room
    entities:
      - light.lamp_1
      - light.lamp_2
      - light.lamp_3
```

## Versionado

Cada componente mantiene su propia versión en `version.json`:
```json
{
  "version": "3.2.0",
  "source_url": "https://github.com/thomasloven/lovelace-card-mod",
  "last_updated": "2025-06-22T10:00:00Z",
  "commit_hash": "abc123def456"
}
```

## Contribuir

1. Fork del repositorio
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit tus cambios: `git commit -am 'Agrega nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crea un Pull Request

## Licencia

Este repositorio combina múltiples proyectos con sus respectivas licencias:
- Card-Mod: MIT License
- Fold Entity Row: MIT License

Ver los archivos LICENSE en cada directorio de componente para más detalles.

## Soporte

Para problemas específicos de cada componente, consulta primero la documentación original:
- [Card-Mod Issues](https://github.com/thomasloven/lovelace-card-mod/issues)
- [Fold Entity Row Issues](https://github.com/thomasloven/lovelace-fold-entity-row/issues)

Para problemas relacionados con este repositorio unificado, abre un issue aquí.