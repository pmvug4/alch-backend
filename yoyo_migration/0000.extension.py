"""
Add old DBMATE form migration
"""

from yoyo import step

steps = [
    step("""
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS address_standardizer;
CREATE EXTENSION IF NOT EXISTS address_standardizer_data_us;
""",
         """
DROP EXTENSION postgis;
DROP EXTENSION address_standardizer;
DROP EXTENSION address_standardizer_data_us;
"""),  # rollback command
]
