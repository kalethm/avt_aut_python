# -*- coding: utf-8 -*-
"""
Entry point for the automation framework (behave + selenium + appium + adb).

Every feature has a unique @ID_* tag. Run by ID or pass behave args directly:

    python run_tests.py api            # @ID_API      -> API examples
    python run_tests.py web            # @ID_WEB      -> web (Selenium + Playwright)
    python run_tests.py app            # @ID_APP      -> Appium mobile/POS
    python run_tests.py pax            # @ID_POS_PAX  -> POS PAX via ADB
    python run_tests.py ingenico       # @ID_POS_INGENICO -> POS Ingenico via ADB
    python run_tests.py json           # @ID_JSON     -> data-driven con JSON
    python run_tests.py all            # everything

Behave arguments also work as-is:

    python run_tests.py --tags @ID_API
    python run_tests.py --tags ~@pos_ingenico
    python run_tests.py test/features/api
"""
import sys

from behave.__main__ import main as behave_main

IDS = {
    'api': '@ID_API',
    'web': '@ID_WEB',
    'app': '@ID_APP',
    'mobile': '@ID_APP',
    'pax': '@ID_POS_PAX',
    'ingenico': '@ID_POS_INGENICO',
    'excel': '@ID_EXCEL',
    'json': '@ID_JSON',
}


def main(argv):
    if argv and argv[0].lower() in IDS:
        args = ['--tags', IDS[argv[0].lower()]] + argv[1:]
    elif argv and argv[0].lower() == 'all':
        args = argv[1:]
    else:
        args = argv

    # Reportes: behave.json (para cucumber.json) + report.html
    import config
    reports = config.REPORTS['reports_dir']
    args = (['--format', 'pretty',
             '--format', 'json',
             '--format', 'behave_html_pretty_formatter:PrettyHTMLFormatter',
             '--outfile', '-',
             '--outfile', f'{reports}/behave.json',
             '--outfile', f'{reports}/report.html'] + args)

    status = behave_main(args)

    # Post-run reports (behave.json ya está escrito en este punto).
    try:
        import config
        from test.helpers import report
        if config.REPORTS.get('cucumber_report', True):
            report.generate_cucumber_report()
        report.print_summary()
    except Exception as exc:  # noqa: BLE001
        print(f'No se pudieron generar reportes: {exc}')
    return status


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
