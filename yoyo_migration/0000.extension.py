"""
Add old DBMATE form migration
"""

from yoyo import step

steps = [
    step(
        """
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        """
    ),  # rollback command
]
