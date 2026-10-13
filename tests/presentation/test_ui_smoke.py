"""Render every screen of the real UI. Skipped where no display is available (e.g. Linux CI)."""

import tkinter

import pytest

from ozempic_seguro.bootstrap import build_services
from ozempic_seguro.domain.users import Role
from ozempic_seguro.infrastructure.settings import Settings

pytestmark = pytest.mark.ui


@pytest.fixture(scope="module")
def app(tmp_path_factory):
    # One Tk root for the whole module: creating a second root in the same process is
    # unreliable on Windows virtualenvs ("Can't find a usable init.tcl").
    from ozempic_seguro.presentation.app import MainApp

    services = build_services(
        Settings(
            database_path=tmp_path_factory.mktemp("ui") / "ui.db",
            bcrypt_rounds=10,
            admin_password="1111",
            technician_password="2222",
        )
    )
    try:
        main = MainApp(services)
    except tkinter.TclError:
        services.close()
        pytest.skip("no display available")
    errors = []
    main.report_callback_exception = lambda *exc: errors.append(exc)
    yield main
    main.close()
    assert errors == []


def test_every_screen_renders(app):
    from ozempic_seguro.presentation.screens.admin.audit import AuditScreen
    from ozempic_seguro.presentation.screens.admin.history import HistoryScreen
    from ozempic_seguro.presentation.screens.admin.panel import AdminDrawersScreen
    from ozempic_seguro.presentation.screens.admin.register_user import RegisterUserScreen
    from ozempic_seguro.presentation.screens.admin.users import UsersScreen
    from ozempic_seguro.presentation.screens.diagnostics import DiagnosticsScreen
    from ozempic_seguro.presentation.screens.timer_control import TimerControlScreen

    nav, services = app.navigator, app.services
    nav.show_start_session()
    nav.show_login()
    login = nav._current
    login.username_entry.insert(0, "00")
    login.password_entry.insert(0, "1111")
    login._submit()
    assert type(nav._current).__name__ == "AdminPanelScreen"

    services.users.register("Maria", "10", "1234", Role.SELLER)
    for screen in (
        UsersScreen,
        AdminDrawersScreen,
        RegisterUserScreen,
        AuditScreen,
        HistoryScreen,
        TimerControlScreen,
        DiagnosticsScreen,
    ):
        nav.show(lambda parent, s=screen: s(parent, nav))
        app.update()

    services.auth.logout()
    services.auth.login("10", "1234")
    nav.show_home()
    app.update()
    assert type(nav._current).__name__ == "OperatorScreen"

    nav.end_session()
    app.update()
    assert services.auth.current_user is None


def test_idle_session_returns_to_start(app, monkeypatch):
    app.services.auth.login("00", "1111")
    app.navigator.show_home()
    monkeypatch.setattr(app.services.auth, "expire_if_idle", lambda: True)

    app._check_idle()
    app.update()

    assert type(app.navigator._current).__name__ == "StartSessionScreen"
