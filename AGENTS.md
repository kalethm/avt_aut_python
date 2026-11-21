# AGENTS.md — Estándar del framework de automatización

## Stack

behave (BDD, Gherkin en español) + Selenium POM + Appium + requests.
Entorno: `.venv` en la raíz. Ejecutar tests con `python run_tests.py <id|feature>`.

## Automatizar un flujo a partir de un video

Cuando el usuario comparta un video de un flujo manual:

1. Extraer fotogramas (OpenCV, ~1 fps) e identificar: URL, acciones en
   orden, valores ingresados y resultado final esperado.
2. Crear el feature en `test/features/web/` en Gherkin español
   (`# language: es`) con tag `@ID_WEB` y un tag de escenario.
3. Crear el page object en `test/pages/` (`snake_case.py`, clase
   `PascalCase`) heredando de `BasePage`.
4. Crear los datos en `settings/data/<nombre>.json` con un objeto para
   los datos de entrada y otro `resultado_esperado`. Nada de datos
   hardcodeados en el feature ni en los steps.
5. Crear los steps en `test/steps/` delegando SIEMPRE en el page object;
   los steps no contienen locators ni lógica Selenium.
6. Ejecutar el escenario con `run_tests.py` hasta que pase y reportar el
   resultado.

## Estrategia de locators (en orden de prioridad)

a) `id` fijo del DOM. Si el id parece dinámico (`ember123`, `:r4:`,
   sufijos numéricos), NO usarlo literal: usar `contains(@id,'prefijo')`
   o `starts-with`.
b) Atributos semánticos: `name`, `placeholder`, `type`, `aria-label`,
   `data-*` (ej: `input[placeholder='Email']`,
   `button[aria-label='Close']`).
c) CSS por estructura estable con clases no generadas.
d) Xpath con `contains()`/`normalize-space()` por texto visible o
   atributo parcial (ej: `//button[contains(.,'Enviar')]`,
   `//div[contains(@class,'option') and normalize-space()='Haryana']`).
   PROHIBIDO: rutas absolutas (`/html/body/div[3]/...`), `[n]`
   posicionales y `nth-child` salvo que no haya alternativa.
e) Componentes JS (react-select, datepicker, radios/checkboxes ocultos,
   toggles): interactuar con su `<label for>`, input interno o JS;
   nunca clicks al input oculto directamente.

## Reglas

- Waits explícitos (`WebDriverWait` del `BasePage`). Nunca `time.sleep`.
- Clicks que puedan ser interceptados por ads/overlays: `safe_click`.
- Si no se tiene el DOM real de la página, pedir la URL o el HTML antes
  de inventar locators.
- Verificar que cada locator devuelva exactamente 1 elemento antes de
  dar el test por bueno.
- Al terminar, reportar qué locators quedaron frágiles o dudosos.

## Convenciones del proyecto

- Config central en `config.py` + `settings/settings.json`; secretos
  solo en `.env` (ver `.env_template`).
- Drivers centralizados en `test/helpers/drivers.py`
  (`WebDriverManager`, `AppiumManager`, `ApiClient`); hooks de ciclo de
  vida y evidencias en `test/environment.py`.
- Datos de prueba: JSON en `settings/data/` cargados con
  `test/helpers/json_data.py::load_json` (rutas relativas al root).
- Comentarios de código en inglés; Gherkin y comunicación en español.
