# language: es
@ID_POS_INGENICO
Característica: POS - Ejemplo con ADB (Ingenico)
  Como QA
  Quiero validar una terminal POS Ingenico por ADB
  Para automatizar flujos del terminal sin Appium

  # Requiere: dispositivo conectado por USB/WiFi con depuración habilitada.
  # Configurar POS_INGENICO_1_ADB_SERIAL en .env o config.py.
  @pos_ingenico
  Escenario: Smoke test terminal Ingenico
    Dado que conecto con el POS 'POS_INGENICO_1'
    Cuando desbloqueo el dispositivo con el PIN '1234'
    Y hago tap en las coordenadas '540', '1200'
    Entonces la pantalla del POS debe mostrar el texto 'Ingenico'
    Y tomo una captura de pantalla del POS
