# language: es
@ID_APP
Característica: Mobile - Ejemplo con Appium (UFT Digital Lab / local)
  Como QA
  Quiero validar una app Android en un POS por Appium
  Para automatizar con selectores UiAutomator2

  # Configurar APPIUM_SERVER_URL en .env:
  #   - local:        http://127.0.0.1:4723/wd/hub
  #   - UFT Digital Lab: https://<lab-host>:8443/wd/hub + credenciales dl|
  @mobile_appium @pos_pax
  Escenario: Abrir app en POS PAX
    Dado que la sesión móvil está lista en el dispositivo 'POS_PAX_1'
    Cuando abro la aplicación en el dispositivo 'POS_PAX_1'
    Entonces el elemento 'accessibility id' con valor 'menu' debe estar presente
