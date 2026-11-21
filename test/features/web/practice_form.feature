# language: es
@ID_WEB
Característica: Web - Practice Form de DemoQA
  Como QA
  Quiero diligenciar el formulario de registro de estudiantes
  Para validar el comportamiento del portal demoqa.com

  @practice_form
  Escenario: Enviar el formulario sin móvil muestra el campo como inválido
    Dado que abro el formulario de registro de estudiantes
    Cuando completo el formulario con los datos del json 'settings/data/practice_form.json'
    Y envío el formulario de registro
    Entonces el campo 'Mobile' se marca como inválido
    Y el formulario no se envía

  @practice_form_ok
  Escenario: Enviar el formulario completo muestra el modal de confirmación
    Dado que abro el formulario de registro de estudiantes
    Cuando completo el formulario con los datos del json 'settings/data/practice_form_ok.json'
    Y envío el formulario de registro
    Entonces el formulario se envía correctamente
