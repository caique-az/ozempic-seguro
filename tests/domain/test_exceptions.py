from ozempic_seguro.domain.exceptions import (
    AccountLockedError,
    DomainError,
    InvalidCredentialsError,
    SystemLockedError,
    UsernameTakenError,
    ValidationError,
)


def test_validation_error_keeps_every_message():
    error = ValidationError(["a", "b"])
    assert error.errors == ["a", "b"]
    assert error.message == "a; b"
    assert isinstance(error, DomainError)


def test_invalid_credentials_mentions_remaining_attempts():
    assert "2 tentativa(s) restante(s)" in InvalidCredentialsError(2).message
    assert InvalidCredentialsError(0).message == "Usuário ou senha inválidos"


def test_lock_errors_format_remaining_time():
    assert AccountLockedError(125).message.endswith("2:05")
    assert "4:59" in SystemLockedError(299).message
    assert SystemLockedError(299).remaining_seconds == 299


def test_username_taken_mentions_the_username():
    assert "'1234'" in UsernameTakenError("1234").message
