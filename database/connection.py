import paramiko

# PATCH: tambahin DSSKey palsu biar sshtunnel ga error
if not hasattr(paramiko, "DSSKey"):
    paramiko.DSSKey = paramiko.RSAKey
import os

import mysql.connector as sql
import sshtunnel
from dotenv import load_dotenv

load_dotenv()  # LOAD ENV


def get_db_connection():
    # CONENCTION VIA SSH TUNNEL
    tunnel = sshtunnel.SSHTunnelForwarder(
        (os.getenv("SSH_HOST"), int(os.getenv("SSH_PORT"))),
        ssh_username=os.getenv("SSH_USERNAME"),
        ssh_password=os.getenv("SSH_PASSWORD"),
        remote_bind_address=(os.getenv("DB_HOST"), int(os.getenv("DB_PORT"))),
    )
    tunnel.start()
    conn = sql.connect(
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=tunnel.local_bind_port,
        database=os.getenv("DB_NAME"),
        autocommit=True,
    )

    return conn, tunnel
