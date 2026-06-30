# PokéDex API

API REST desarrollada con FastAPI como parte de la materia de Programación Aplicada.

El proyecto comenzó como una PokéDex en memoria y posteriormente evolucionó para incorporar persistencia mediante archivos JSON, paginación y operaciones CRUD completas.

## Tecnologías

- Python
- FastAPI
- Pydantic
- Uvicorn
- JSON

## Funcionalidades

- Consultar todos los Pokémon
- Buscar Pokémon por ID
- Buscar por tipo y habilidad
- Catálogo con paginación
- Registrar nuevos Pokémon
- Actualizar Pokémon (PUT)
- Actualización parcial (PATCH)
- Eliminar Pokémon (DELETE)
- Persistencia de datos utilizando archivos JSON
- Protección mediante API Key para operaciones sensibles

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | / | Mensaje de bienvenida |
| GET | /pokemons | Lista de Pokémon |
| GET | /pokemons/{pokemon_id} | Buscar por ID |
| GET | /pokemons/catalogo | Catálogo paginado |
| POST | /pokemon | Registrar Pokémon |
| PUT | /pokemon/{pokemon_id} | Reemplazo completo |
| PATCH | /pokemon/{pokemon_id} | Actualización parcial |
| DELETE | /pokemons/{pokemon_id} | Eliminar Pokémon |

## Persistencia

Toda la información se almacena en el archivo:

```
pokedex.json
```

Cada operación de escritura actualiza automáticamente el archivo para conservar los cambios incluso después de reiniciar la aplicación.

## Ejecutar

```bash
python -m uvicorn main:app --reload
```

Después abrir:

```
http://127.0.0.1:8000/docs
```

## Autor

David Morales