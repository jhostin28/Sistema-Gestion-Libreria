from src.data.database_mgr import get_connection


def login(username: str, password: str):
    """Retorna el usuario si las credenciales son correctas, None si no."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM usuario WHERE username = ? AND password = ?",
        (username, password)
    )
    user = c.fetchone()
    conn.close()
    return user
