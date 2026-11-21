# language: es
@ID_WEB
Característica: Web - Ejemplo con Selenium
  Como QA
  Quiero validar una página web
  Para comprobar el flujo BDD web con Selenium y webdriver-manager

  @web_example
  Escenario: Validar example.com con Selenium
    Dado que ingreso a la aplicación web y navego a la url 'https://example.com'
    Entonces el título de la página debe ser 'Example Domain'
    Y la URL actual debe ser 'example.com'
    Y el elemento con 'xpath' igual a '//p[@lang="en"]' debe contener el texto 'documentation examples'
    Y el elemento con 'tag name' igual a 'a' debe contener el texto 'Learn more'
    Y el elemento con 'tag name' igual a 'a' debe estar visible

  @web_example @playwright
  Escenario: Validar example.com con Playwright
    Dado que ingreso a la aplicación web con playwright y navego a la url 'https://example.com'
    Entonces el título de la página con playwright debe ser 'Example Domain'
    Y con playwright el elemento 'p[lang="en"]' debe contener el texto 'documentation examples'
