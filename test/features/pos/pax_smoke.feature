# language: es
@ID_POS_PAX
Característica: POS - Ejemplo con ADB (PAX)
  Como QA
  Quiero validar una terminal POS PAX por ADB
  Para automatizar flujos del terminal sin Appium

  # Requiere: dispositivo conectado por USB/WiFi con depuración habilitada.
  # Configurar POS_PAX_1_ADB_SERIAL en .env o config.py.
  @pos_pax
  Escenario: Smoke test terminal PAX
    Dado que conecto con el POS 'POS_PAX_1'
    Cuando desbloqueo el dispositivo con el PIN '1234'
    Y ingreso el texto 'test'
    Y presiono enter
    Entonces la pantalla del POS debe mostrar el texto 'test'
    Y la app 'com.getnet.getnetapp' está en ejecución
    Y tomo una captura de pantalla del POS
