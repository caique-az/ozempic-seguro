"""Application entry point: load settings, wire the layers and start the UI."""

import logging
import sys

from .bootstrap import build_services
from .infrastructure.logs import configure_logging
from .infrastructure.settings import ConfigurationError, Settings


def main() -> int:
    try:
        settings = Settings.from_env()
    except ConfigurationError as error:
        print(f"Configuração inválida: {error}", file=sys.stderr)  # noqa: T201
        return 2

    logger = configure_logging(settings.logs_dir, settings.development)
    services = build_services(settings)

    # Imported here so that a configuration error is reported without loading Tk.
    from .presentation.app import MainApp

    try:
        MainApp(services).mainloop()
    except KeyboardInterrupt:
        pass
    except Exception:
        logger.exception("Fatal application error")
        return 1
    finally:
        services.close()
        logging.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
