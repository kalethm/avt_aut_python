# language: es
@ID_JSON
Característica: JSON - Ejemplo data-driven
  Como QA
  Quiero leer datos desde archivos JSON
  Para alimentar escenarios data-driven

  # Los archivos de datos viven en test/data/ (listas de objetos u objetos
  # con clave "rows").
  Escenario: Validar estructura del JSON de usuarios
    Dado que cargo las filas del json 'test/data/usuarios.json'
    Entonces debo tener 3 filas de datos en el json
    Y cada fila del json debe tener las claves 'usuario', 'clave', 'esperado'
