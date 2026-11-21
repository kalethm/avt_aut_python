# Framework de Automatización BDD (behave + Selenium + Appium + Playwright + ADB)

Framework de pruebas de aceptación escrito en Python con [behave](https://behave.readthedocs.io/)
(Gherkin/Cucumber para Python). Cubre:

- **API** — `requests` con sesión compartida
- **Web** — Selenium (webdriver-manager auto-resuelve el driver) y Playwright
- **Mobile/POS** — Appium (UiAutomator2) contra servidor local o remoto (UFT Digital Lab)
- **POS por ADB** — `adb` directo (tap/swipe/text/keyevent + `uiautomator dump`) para
  terminales PAX e Ingenico sin necesidad de Appium
- **Excel** — tests data-driven leyendo `.xlsx` con openpyxl
- **Integraciones** — clientes REST para Jira y ALM (opcionales)
- **Reportes** — `behave.json`, `cucumber.json` y `report.html` al finalizar cada corrida

## Requirements

- Python 3.10+ (desarrollado con 3.12)
- `adb` en el PATH para los tests de POS (Android SDK Platform Tools)
- Appium server (local o remoto) solo para los tests `@mobile_appium`

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
python -m playwright install chromium   # navegadores de Playwright
```

Copia `.env_template` a `.env` y ajusta los valores que necesites
(dispositivos POS, PINs, URLs de Appium/Jira/ALM, etc.). Todas las variables
también pueden definirse en `config.py`.

## Estructura

```
.
├── config.py                  # Configuración central (API, WEB, APPIUM, ADB, POS_DEVICES, JIRA, ALM, REPORTS)
├── behave.ini                 # Config de behave
├── run_tests.py               # Entry point: python run_tests.py <id|args behave>
├── requirements.txt
├── .env_template
├── settings/
│   ├── settings.json          # Parámetros no sensibles (api, web, appium, jira, alm, reports)
│   └── integrations/
│       ├── jira.py            # Cliente Jira REST API v3
│       └── alm.py             # Cliente ALM genérico (estilo TestRail)
└── test/
    ├── environment.py         # Hooks de behave: before_all/after_scenario/after_all + evidencias
    ├── data/                  # Archivos de datos (ej: usuarios.xlsx, usuarios.json)
    ├── features/
    │   ├── api/               # @ID_API
    │   ├── web/               # @ID_WEB (Selenium + @playwright)
    │   ├── app/               # @ID_APP (Appium)
    │   ├── pos/               # @ID_POS_PAX / @ID_POS_INGENICO (ADB)
    │   ├── excel/             # @ID_EXCEL
    │   └── json/              # @ID_JSON
    ├── helpers/
    │   ├── drivers.py         # WebDriverManager, ApiClient, AppiumManager, AdbClient
    │   ├── adb_pos.py         # Wrapper de comandos adb para terminales POS
    │   ├── excel_data.py      # Lectura de .xlsx para tests data-driven
    │   ├── json_data.py       # Lectura de .json para tests data-driven
    │   └── report.py          # cucumber.json + resumen ejecutivo
    └── steps/                 # Step definitions por dominio
        ├── api_steps.py
        ├── web_steps.py           # Selenium
        ├── playwright_steps.py    # Playwright (opt-in)
        ├── appium_steps.py        # Appium / UiAutomator2
        ├── pos_steps.py           # ADB directo (PAX / Ingenico)
        ├── excel_steps.py         # Data-driven con Excel
        └── json_steps.py          # Data-driven con JSON
```

## IDs de ejecución

Cada feature tiene un tag único `@ID_*` a nivel de Feature. `run_tests.py`
lo mapea a un nombre corto:

```bash
python run_tests.py api            # @ID_API
python run_tests.py web            # @ID_WEB
python run_tests.py app            # @ID_APP
python run_tests.py pax            # @ID_POS_PAX
python run_tests.py ingenico       # @ID_POS_INGENICO
python run_tests.py excel          # @ID_EXCEL
python run_tests.py json           # @ID_JSON
python run_tests.py all            # todo
```

También acepta args de behave directo: `--tags`, `--name`, rutas, exclusiones.

## Reportes

Al finalizar cualquier corrida se generan en `output/reports/`:

- **`report.html`** — reporte HTML visual (pasos, estados, duraciones, evidencias)
- **`behave.json`** — salida nativa JSON de behave
- **`cucumber.json`** — formato Cucumber compatible con ReportPortal,
  cucumber-reporting y herramientas ALM externas

Además se imprime un resumen ejecutivo en consola con totales y steps fallidos.

## Excel / data-driven

```python
from test.helpers.excel_data import load_sheet
rows = load_sheet('test/data/usuarios.xlsx', sheet='usuarios')
# -> [{'usuario': 'admin', 'clave': 'admin123', 'esperado': 'Bienvenido'}, ...]
```

La primera fila de la hoja es el encabezado. Ver `test/features/excel/`
para el ejemplo funcional.

## JSON / data-driven

Los archivos de datos JSON viven en `test/data/`:

```python
from test.helpers.json_data import load_json, load_rows
rows = load_rows('test/data/usuarios.json')
# -> [{'usuario': 'admin', 'clave': 'admin123', 'esperado': 'Bienvenido'}, ...]
```

`load_rows` espera una lista de objetos (o un objeto con clave `"rows"`).
Ver `test/features/json/` para el ejemplo funcional.

## settings/settings.json

`settings/settings.json` centraliza los parámetros **no sensibles** del
framework (`api`, `web`, `appium`, `adb`, `jira`, `alm`, `reports`).
Precedencia: variable de entorno / `.env` > `settings.json` > default en
`config.py`. Los secretos (`JIRA_USER`, `JIRA_TOKEN`, `ALM_USER`, `ALM_TOKEN`,
PINs) solo se definen en `.env`, nunca en el JSON.

## Jira y ALM (opcional)

Parámetros en `settings/settings.json` (`jira.enabled`, `jira.base_url`,
`jira.project`, `alm.status_map`, ...) y credenciales en `.env`:
`JIRA_USER`, `JIRA_TOKEN` y/o `ALM_USER`, `ALM_TOKEN`.

```python
from settings.integrations.jira import JiraClient
jira = JiraClient()
key = jira.create_issue('PROJ', 'Bug en login', 'Descripción del fallo')
jira.add_comment(key, 'Falló el escenario @ID_WEB en el step X')

from settings.integrations.alm import AlmClient
alm = AlmClient()
alm.add_result(run_id=10, case_id=25, status_id=5, comment='Falló @ID_API')
```

Si no hay credenciales configuradas, los clientes lanzan `RuntimeError`
con instrucciones claras.

## Configuración de dispositivos POS

En `config.py` (o `.env`) se declaran los POS en `POS_DEVICES`:

```python
'POS_PAX_1': {
    'kind': 'both',            # 'appium' | 'adb' | 'both'
    'manufacturer': 'pax',     # 'pax' | 'ingenico' | 'generic'
    'adb_serial': 'R58N64558ZJ',          # serial adb (USB o ip:puerto)
    'udid': 'R58N64558ZJ',                # UDID para Appium
    'app_package': 'com.getnet.getnetapp',
    'app_activity': 'com.coasin.getnetapp.presenter.MainActivity',
    'unlock_pin': '1234',
}
```

- **ADB**: pasos como `conecto con el POS`, `hago tap en las coordenadas`,
  `ingreso el texto`, `la pantalla del POS debe mostrar el texto`,
  `tomo una captura de pantalla del POS`.
- **Appium**: `APPIUM_SERVER_URL` apunta a tu servidor (local
  `http://127.0.0.1:4723/wd/hub` o UFT Digital Lab `https://<lab>:8443/wd/hub`).
  Steps en `appium_steps.py` con selectores UiAutomator2.

## Evidencias

- Screenshot automático en `output/evidencias/` cuando un escenario falla
  (web driver, Appium y ADB según el dispositivo activo).

## Notas

- No commitear secretos: usa `.env` (git-ignored) para PINs, credenciales y seriales.
- webdriver-manager descarga el driver correcto automáticamente.
- Los features están en español (`# language: es`); los steps aceptan el
  "que" opcional después de "Dado/Y/Cuando/Entonces".
