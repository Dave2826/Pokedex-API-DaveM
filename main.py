import os
import json

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List

app = FastAPI(title="PokéDex API de David Morales")

ARCHIVO_DB = "pokedex.json"


# Función 1: Leer el archivo JSON y cargarlo a la RAM
def cargar_pokedex() -> dict:
    """Devuelve la PokéDex completa en un diccionario de Python"""

    # Si el archivo no existe, devolvemos un diccionario vacío
    if not os.path.exists(ARCHIVO_DB):
        return {}

    # Guardián y Portal para abrir un archivo del disco duro
    with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
        datos_texto = json.load(f)

        # Conversión de seguridad:
        # JSON convierte los IDs a str ("1", "2"...)
        # Los regresamos a int (1,2...) para mantener compatibilidad
        return {int(k): v for k, v in datos_texto.items()}


# Función 2: Tomar los cambios de la RAM y guardarlos en el JSON del disco duro
def guardar_pokedex(pokedex_actualizada: dict):
    """Almacena el diccionario de Python en un archivo JSON"""

    # Guardián y Portal para abrir un archivo en el disco duro
    with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
        json.dump(
            pokedex_actualizada,
            f,
            ensure_ascii=False,
            indent=4
        )


class Pokemon(BaseModel):
    id: int
    nombre: str
    tipo: List[str]
    nivel: int
    habilidad: str
    movimientos: List[str]
    ataque: int
    defensa: int


class PokemonParcial(BaseModel):
    nombre: str | None = None
    tipo: List[str] | None = None
    nivel: int | None = None
    habilidad: str | None = None
    movimientos: List[str] | None = None
    ataque: int | None = None
    defensa: int | None = None


# Cargar automáticamente la PokéDex desde el JSON
pokedex = cargar_pokedex()


# Endpoint raíz
@app.get("/")
def leer_raiz():
    return {
        "mensaje": "¡Bienvenido a la PokéDex API de David Morales! Soy estudiante de Desarrollo de Software y mi Pokémon favorito es Charizard."
    }


# Catálogo paginado de Pokémon (page y size)
@app.get("/pokemons/catalogo")
def catalogo_pokemon(page: int = 1, size: int = 5):

    # Validar parámetros de paginación
    if page <= 0:
        raise HTTPException(
            status_code=400,
            detail="El parámetro 'page' debe ser mayor a cero."
        )

    if size <= 0:
        raise HTTPException(
            status_code=400,
            detail="El parámetro 'size' debe ser mayor a cero."
        )

    pokedex = cargar_pokedex()

    pokedex_en_lista = list(pokedex.items())

    offset = (page - 1) * size

    resultados_paginados = dict(
        pokedex_en_lista[offset: offset + size]
    )

    return {
        "pagina_actual": page,
        "tamano_pagina": size,
        "resultado": resultados_paginados
    }


# Buscar Pokémon por ID (Path Parameter)
@app.get("/pokemons/{pokemon_id}")
def obtener_por_id(pokemon_id: int):

    pokedex = cargar_pokedex()

    if pokemon_id not in pokedex:
        raise HTTPException(
            status_code=404,
            detail=f"¡El Pokémon con el ID #{pokemon_id} no existe en la región!"
        )

    return pokedex[pokemon_id]


# Buscar Pokémon por tipo y/o habilidad (Query Parameters)
@app.get("/pokemons")
def obtener_todos_los_pokemon(
        tipo: str = None,
        habilidad: str = None,
        limit: int = 5,
        offset: int = 0):

    pokedex = cargar_pokedex()

    resultados = pokedex

    if tipo:
        tipo_existe = any(
            tipo.capitalize() in p["tipo"]
            for p in pokedex.values()
        )

        if not tipo_existe:
            raise HTTPException(
                status_code=404,
                detail=f"No existe ningún Pokémon de tipo {tipo.capitalize()} en la PokéDex..."
            )

        resultados = {
            pokemon_id: p
            for pokemon_id, p in resultados.items()
            if tipo.capitalize() in p["tipo"]
        }

    if habilidad:
        hab_existe = any(
            habilidad.lower() == p["habilidad"].lower()
            for p in pokedex.values()
        )

        if not hab_existe:
            raise HTTPException(
                status_code=404,
                detail=f"No existe ningún Pokémon con la habilidad '{habilidad}' en la PokéDex..."
            )

        resultados = {
            pokemon_id: p
            for pokemon_id, p in resultados.items()
            if habilidad.lower() == p["habilidad"].lower()
        }

    if not resultados:

        mensaje_error = "No se encontraron Pokémon"

        if tipo:
            mensaje_error += f" de tipo {tipo.capitalize()}"

        if habilidad:
            mensaje_error += f" con la habilidad '{habilidad}'"

        raise HTTPException(
            status_code=404,
            detail=f"{mensaje_error} en la PokéDex..."
        )

    # --- Capa 2: Paginación ---
    # Convertimos el diccionario en una lista para poder seccionarla.

    pokedex_en_lista = list(resultados.items())

    # Aplicar el Slicing y volvemos a empaquetar como diccionario
    resultados_paginados = dict(
        pokedex_en_lista[offset: offset + limit]
    )

    # Devolvemos los metadatos y la información final
    return {
        "total_coincidencias": len(resultados),
        "limite_pagina": limit,
        "desplazamiento": offset,
        "resultados": resultados_paginados
    }

# Endpoint para par REGISTRAR un nuevo pokemon
@app.post("/pokemon/{pokemon_id}", status_code=status.HTTP_201_CREATED)
def registrar_nuevo_pokemon(pokemon_id: int, nuevo_pokemon: Pokemon):

    pokedex = cargar_pokedex()

    # Verificar si ya existe
    if nuevo_pokemon.id in pokedex:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un Pokémon con el ID #{nuevo_pokemon.id}. Se trata de {pokedex[nuevo_pokemon.id]['nombre']}"
        )

    # Registrar Pokémon nuevo
    pokedex[nuevo_pokemon.id] = nuevo_pokemon.model_dump()

    guardar_pokedex(pokedex)

    return {
        "mensaje": f"¡Ya está! Nuevo Pokémon registrado: {nuevo_pokemon.nombre} con el ID #{nuevo_pokemon.id}",
        "datos": pokedex[nuevo_pokemon.id]
    }


# Endpoint para actualizar un Pokemon por Completo (Reemplazo total)
@app.put("/pokemon/{pokemon_id}")
def actualizar_pokemon_completo(pokemon_id: int, pokemon_actualizado: Pokemon):

    pokedex = cargar_pokedex()

    # Validar que el pokemon existe en la Pokedex
    if pokemon_id not in pokedex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"¡No existe ningún Pokémon con el ID #{pokemon_id}!"
        )

    # 2. Reemplazar los datos viejos con el JSON nuevo completo
    pokedex[pokemon_id] = pokemon_actualizado.model_dump()

    guardar_pokedex(pokedex)

    # 3. Devolver mensaje de actualizacion.
    return {
        "mensaje": "Reemplazo total exitoso",
        "datos": pokedex[pokemon_id]
    }


# Endpoint para actualizar un Pokemon PARCIALMENTE
@app.patch("/pokemon/{pokemon_id}")
def actualizar_pokemon_parcial(pokemon_id: int, pokemon_parcial: PokemonParcial):

    pokedex = cargar_pokedex()

    # 1.Validar que el Pokemon exista en la Pokedex
    if pokemon_id not in pokedex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"¡No existe ningún Pokémon con el ID #{pokemon_id}!"
        )

    # 2. Extraer unicamente los datos a actualizar
    # exclude_unset=True para ignorar los campos vacios
    datos_a_actualizar = pokemon_parcial.model_dump(exclude_unset=True)

    # 3. Actualizar solo las llaves que llegaron a actualizarse
    for llave, valor in datos_a_actualizar.items():
        pokedex[pokemon_id][llave] = valor

    guardar_pokedex(pokedex)

    return {
        "mensaje": "Actualizacion parcial completada",
        "datos": pokedex[pokemon_id]
    }


# Edpoint para LIBERAR (eliminar) un Pokemon de la Pokedex
@app.delete("/pokemons/{pokemon_id}")
def liberar_pokemon(pokemon_id: int):

    pokedex = cargar_pokedex()

    # 1. Validar que el Pokemon exista en la Pokedex
    if pokemon_id not in pokedex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"¡No existe ningún Pokémon con el ID #{pokemon_id}!"
        )

    # Regla de negocio:
    # Los Pokémon iniciales NO pueden ser liberados
    if pokemon_id in [1, 4, 7]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los Pokémon iniciales no pueden ser liberados."
        )

    # 2. Extraer y borrar el pokemon de la pokedex usando .pop()
    pokemon_liberado = pokedex.pop(pokemon_id)

    guardar_pokedex(pokedex)

    nombre = pokemon_liberado["nombre"]

    return {
        "mensaje": f"¡Adiós, {nombre}! Pokémon liberado exitosamente."
    }