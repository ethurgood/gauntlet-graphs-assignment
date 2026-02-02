"""
LIV Database Tool for querying premises and occupancy types.
"""
import os
import pymysql
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

load_dotenv()


class LIVDatabaseTool:
    """
    Tool for querying the LIV MySQL database.
    Provides read-only access to premises, states, and occupancy type tables.
    """

    def __init__(self):
        """Initialize database connection parameters from environment."""
        self.config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT')),
            'user': os.getenv('DB_USERNAME'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_DATABASE'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

    def _get_connection(self):
        """Create a new database connection."""
        return pymysql.connect(**self.config)

    def query_premises_by_location(
        self,
        latitude: float,
        longitude: float,
        state_id: Optional[int] = None,
        radius_degrees: float = 0.001
    ) -> List[Dict[str, Any]]:
        """
        Query premises by latitude/longitude within a radius.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            state_id: Optional state ID to filter by
            radius_degrees: Search radius in degrees (~0.001 = ~100m)

        Returns:
            List of matching premises records
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                # Build query with bounding box search, ordered by distance
                query = """
                    SELECT
                        id,
                        premise_name,
                        address_line_1,
                        address_line_2,
                        latitude,
                        longitude,
                        postal_code,
                        state_id,
                        city_id,
                        ahj_id,
                        formatted_address,
                        reference_number,
                        SQRT(
                            POW(CAST(latitude AS DECIMAL(10,7)) - %s, 2) +
                            POW(CAST(longitude AS DECIMAL(10,7)) - %s, 2)
                        ) as distance
                    FROM premises
                    WHERE deleted_at IS NULL
                        AND latitude IS NOT NULL
                        AND longitude IS NOT NULL
                        AND ABS(CAST(latitude AS DECIMAL(10,7)) - %s) < %s
                        AND ABS(CAST(longitude AS DECIMAL(10,7)) - %s) < %s
                """
                params = [latitude, longitude, latitude, radius_degrees, longitude, radius_degrees]

                if state_id:
                    query += " AND state_id = %s"
                    params.append(state_id)

                query += " ORDER BY distance LIMIT 10"

                cursor.execute(query, params)
                results = cursor.fetchall()

                return results
        finally:
            connection.close()

    def get_state_by_code(self, state_code: str) -> Optional[Dict[str, Any]]:
        """
        Get state information by state code.

        Args:
            state_code: Two-letter state code (e.g., "CA")

        Returns:
            State record or None if not found
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT id, name, state_code, status
                    FROM states
                    WHERE state_code = %s
                        AND status = 1
                        AND deleted_at IS NULL
                    LIMIT 1
                """
                cursor.execute(query, [state_code])
                result = cursor.fetchone()
                return result
        finally:
            connection.close()

    def get_state_by_name(self, state_name: str) -> Optional[Dict[str, Any]]:
        """
        Get state information by state name.

        Args:
            state_name: Full state name (e.g., "California")

        Returns:
            State record or None if not found
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT id, name, state_code, status
                    FROM states
                    WHERE name = %s
                        AND status = 1
                        AND deleted_at IS NULL
                    LIMIT 1
                """
                cursor.execute(query, [state_name])
                result = cursor.fetchone()
                return result
        finally:
            connection.close()

    def get_occupancy_types_by_state(self, state_code: str) -> List[Dict[str, Any]]:
        """
        Get all valid occupancy types for a given state.

        Args:
            state_code: Two-letter state code (e.g., "CA")

        Returns:
            List of occupancy type records
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT DISTINCT
                        ot.id as occupancy_type_id,
                        ot.name as occupancy_type_name,
                        aot.ahj_id
                    FROM ahj_occupancy_type aot
                    INNER JOIN ahj_lists a ON aot.ahj_id = a.id
                    INNER JOIN states s ON a.state_id = s.id
                    INNER JOIN occupancy_type ot ON aot.occupancy_type_id = ot.id
                    WHERE s.state_code = %s
                        AND aot.status = 1
                        AND a.deleted_at IS NULL
                    ORDER BY ot.name
                """
                cursor.execute(query, [state_code])
                results = cursor.fetchall()
                return results
        finally:
            connection.close()

    def get_premise_by_id(self, premise_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a single premise by ID.

        Args:
            premise_id: Premise ID

        Returns:
            Premise record or None if not found
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT
                        id,
                        premise_name,
                        address_line_1,
                        address_line_2,
                        latitude,
                        longitude,
                        postal_code,
                        state_id,
                        city_id,
                        ahj_id,
                        formatted_address,
                        reference_number,
                        created_at,
                        updated_at
                    FROM premises
                    WHERE id = %s
                        AND deleted_at IS NULL
                    LIMIT 1
                """
                cursor.execute(query, [premise_id])
                result = cursor.fetchone()
                return result
        finally:
            connection.close()

    def test_connection(self) -> bool:
        """
        Test database connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            connection = self._get_connection()
            connection.close()
            return True
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False
