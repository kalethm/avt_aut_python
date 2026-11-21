# language: es
@ID_API
Característica: API - Ejemplo con requests
  Como QA
  Quiero validar un endpoint REST público
  Para comprobar el flujo BDD de API

  @api_example
  Escenario: Consultar un pokemon en PokeAPI
    Dado que preparo la petición URI 'https://pokeapi.co/api/v2' con path 'pokemon/pikachu'
    Y preparo el método de la petición 'GET'
    Cuando envío la petición
    Entonces el código de estado debe ser '200'
    Y la respuesta JSON debe contener la clave 'name'
    Y el valor JSON de la clave 'name' debe ser de tipo 'str'
    Y la respuesta debe contener el valor 'pikachu'
