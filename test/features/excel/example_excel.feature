# language: es
@ID_EXCEL
Característica: Excel - Ejemplo data-driven
  Como QA
  Quiero leer datos desde un archivo Excel
  Para alimentar escenarios data-driven

  # El archivo test/data/usuarios.xlsx se genera con openpyxl.
  # Puedes crearlo a mano o con:
  #   python -c "from openpyxl import Workbook; ..."
  Escenario: Validar estructura del Excel de usuarios
    Dado que cargo los datos del excel 'test/data/usuarios.xlsx' hoja 'usuarios'
    Entonces debo tener 3 filas de datos
    Y cada fila debe tener las claves 'usuario', 'clave', 'esperado'
