"""Quick test of database connection."""
from graph.tools.liv_database import LIVDatabaseTool

db = LIVDatabaseTool()
print("Testing database connection...")
if db.test_connection():
    print("✓ Database connection successful!")

    # Test getting a state
    print("\nTesting state lookup...")
    state = db.get_state_by_code("CA")
    if state:
        print(f"✓ Found state: {state['name']} (ID: {state['id']})")

        # Test getting occupancy types
        print("\nTesting occupancy types lookup...")
        occupancy_types = db.get_occupancy_types_by_state("CA")
        print(f"✓ Found {len(occupancy_types)} occupancy types for CA")
        if occupancy_types:
            print(f"  Example: {occupancy_types[0]['occupancy_type_name']}")
    else:
        print("✗ No state found for CA")
else:
    print("✗ Database connection failed!")
