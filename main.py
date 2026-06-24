from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List

app = FastAPI(title="PokéDex API de David Morales")

pokedex = {
    1: {
        "nombre": "Bulbasaur",
        "tipo": ["Planta", "Veneno"],
        "nivel": 5,
        "habilidad": "Látigo Cepa Supremo",
        "movimientos": ["Placaje", "Drenadoras", "Látigo Cepa", "Hoja Afilada"],
        "ataque": 49,
        "defensa": 49
    },
    2: {
        "nombre": "Ivysaur",
        "tipo": ["Planta", "Veneno"],
        "nivel": 16,
        "habilidad": "Bosque Viviente",
        "movimientos": ["Hoja Afilada", "Drenadoras", "Síntesis", "Placaje"],
        "ataque": 62,
        "defensa": 63
    },
    3: {
        "nombre": "Venusaur",
        "tipo": ["Planta", "Veneno"],
        "nivel": 32,
        "habilidad": "Furia Floral",
        "movimientos": ["Rayo Solar", "Gigadrenado", "Terremoto", "Bomba Germen"],
        "ataque": 82,
        "defensa": 83
    },
    4: {
        "nombre": "Charmander",
        "tipo": ["Fuego"],
        "nivel": 5,
        "habilidad": "Infierno Dragón",
        "movimientos": ["Ascuas", "Arañazo", "Gruñido", "Giro Fuego"],
        "ataque": 52,
        "defensa": 43
    },
    5: {
        "nombre": "Charmeleon",
        "tipo": ["Fuego"],
        "nivel": 16,
        "habilidad": "Llama Carmesí",
        "movimientos": ["Lanzallamas", "Arañazo", "Colmillo Ígneo", "Garra Metal"],
        "ataque": 64,
        "defensa": 58
    },
    6: {
        "nombre": "Charizard",
        "tipo": ["Fuego", "Volador"],
        "nivel": 32,
        "habilidad": "Tormenta Ígnea",
        "movimientos": ["Lanzallamas", "Vuelo", "Garra Dragón", "Anillo Ígneo"],
        "ataque": 84,
        "defensa": 78
    },
    7: {
        "nombre": "Squirtle",
        "tipo": ["Agua"],
        "nivel": 5,
        "habilidad": "Tsunami Destructor",
        "movimientos": ["Pistola Agua", "Burbuja", "Placaje", "Acua Cola"],
        "ataque": 48,
        "defensa": 65
    },
    8: {
        "nombre": "Wartortle",
        "tipo": ["Agua"],
        "nivel": 16,
        "habilidad": "Marea Ancestral",
        "movimientos": ["Hidrobomba", "Acua Cola", "Protección", "Burbuja"],
        "ataque": 63,
        "defensa": 80
    },
    9: {
        "nombre": "Blastoise",
        "tipo": ["Agua"],
        "nivel": 32,
        "habilidad": "Cañón Oceánico",
        "movimientos": ["Hidrobomba", "Surf", "Rayo Hielo", "Acua Cola"],
        "ataque": 83,
        "defensa": 100
    }
}


class Pokemon(BaseModel):
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


# Endpoint raíz
@app.get("/")
def leer_raiz():
    return {
        "mensaje": "¡Bienvenido a la PokéDex API de David Morales! Soy estudiante de Desarrollo de Software y mi Pokémon favorito es Charizard."
    }

# Buscar Pokémon por ID (Path Parameter)
@app.get("/pokemons/{pokemon_id}")
def obtener_por_id(pokemon_id: int):

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

    # Verificar si ya existe
    if pokemon_id in pokedex:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un Pokémon con el ID #{pokemon_id}. Se trata de {pokedex[pokemon_id]['nombre']}"
        )

    # Registrar Pokémon nuevo
    pokedex[pokemon_id] = nuevo_pokemon.model_dump()

    return {
        "mensaje": f"¡Ya está! Nuevo Pokémon registrado: {nuevo_pokemon.nombre} con el ID #{pokemon_id}",
        "datos": pokedex[pokemon_id]
    }


# Endpoint para actualizar un Pokemon por Completo (Reemplazo total)
@app.put("/pokemon/{pokemon_id}")
def actualizar_pokemon_completo(pokemon_id: int, pokemon_actualizado: Pokemon):

    # Validar que el pokemon existe en la Pokedex
    if pokemon_id not in pokedex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"¡No existe ningún Pokémon con el ID #{pokemon_id}!"
        )

    # 2. Reemplazar los datos viejos con el JSON nuevo completo
    pokedex[pokemon_id] = pokemon_actualizado.model_dump()

    # 3. Devolver mensaje de actualizacion.
    return {
        "mensaje": "Reemplazo total exitoso",
        "datos": pokedex[pokemon_id]
    }


# Endpoint para actualizar un Pokemon PARCIALMENTE
@app.patch("/pokemon/{pokemon_id}")
def actualizar_pokemon_parcial(pokemon_id: int, pokemon_parcial: PokemonParcial):

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

    return {
        "mensaje": "Actualizacion parcial completada",
        "datos": pokedex[pokemon_id]
    }


# Edpoint para LIBERAR (eliminar) un Pokemon de la Pokedex
@app.delete("/pokemons/{pokemon_id}")
def liberar_pokemon(pokemon_id: int):

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

    nombre = pokemon_liberado["nombre"]

    return {
        "mensaje": f"¡Adiós, {nombre}! Pokémon liberado exitosamente."
    }
