from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List

app = FastAPI(title="PokéDex API de David Morales")

pokedex = {
    1: {
        "nombre": "Bulbasaur",
        "tipo": ["Planta", "Veneno"],
        "habilidad": "Látigo Cepa Supremo",
        "nivel": 5,
        "movimientos": [
            "Látigo Cepa",
            "Drenadoras",
            "Hoja Afilada",
            "Bomba Germen"
        ],
        "ataque": 49,
        "defensa": 49
    },
    4: {
        "nombre": "Charmander",
        "tipo": ["Fuego"],
        "habilidad": "Infierno Dragón",
        "nivel": 5,
        "movimientos": [
            "Ascuas",
            "Lanzallamas",
            "Garra Dragón",
            "Giro Fuego"
        ],
        "ataque": 52,
        "defensa": 43
    },
    7: {
        "nombre": "Squirtle",
        "tipo": ["Agua"],
        "habilidad": "Tsunami Destructor",
        "nivel": 5,
        "movimientos": [
            "Pistola Agua",
            "Hidrobomba",
            "Burbuja",
            "Acua Cola"
        ],
        "ataque": 48,
        "defensa": 65
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


# Obtener todos los Pokémon
@app.get("/pokemons")
def obtener_todos():
    return pokedex


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
@app.get("/pokemons/")
def obtener_todos_los_pokemon(
        tipo: str = None,
        habilidad: str = None):

    if tipo is None and habilidad is None:
        return pokedex

    pokemon_filtrados = {}

    for pokemon_id, datos in pokedex.items():

        cumple_tipo = True
        cumple_habilidad = True

        if tipo is not None:
            cumple_tipo = tipo.capitalize() in datos["tipo"]

        if habilidad is not None:
            cumple_habilidad = habilidad.lower() in datos["habilidad"].lower()

        if cumple_tipo and cumple_habilidad:
            pokemon_filtrados[pokemon_id] = datos

    if len(pokemon_filtrados) > 0:
        return pokemon_filtrados

    if tipo is not None and habilidad is None:
        raise HTTPException(
            status_code=404,
            detail=f"No existe ningún Pokémon del tipo {tipo} en la PokéDex."
        )

    if tipo is None and habilidad is not None:
        raise HTTPException(
            status_code=404,
            detail=f"No existe ningún Pokémon con la habilidad {habilidad} en la PokéDex."
        )

    raise HTTPException(
        status_code=404,
        detail=f"No existe ningún Pokémon de tipo {tipo} con la habilidad {habilidad} en la PokéDex."
    )


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
