import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, select, func
import json
from datetime import date, time
from decimal import Decimal

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (date, time)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError ("Type %s not serializable" % type(obj))

DATABASE_URL = "mysql+pymysql://root:0798628195Far@localhost/Supermarket"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

# Function to check counts of all tables
def check_counts():

    # get table counts
    print("TABLE COUNTS:")
    for table_name in sorted(metadata.tables.keys()):
        table = metadata.tables[table_name]
        count_query = select(func.count()).select_from(table)

        # Execute count query
        with engine.connect() as conn:
            count = conn.execute(count_query).scalar()
            print(f"  {table_name}: {count}")


# Function to check latest entries in all tables
def check_latest():
    
    # get the three latest entries
    for table_name in sorted(metadata.tables.keys()):
        print(f"\nLATEST 3 ENTRIES IN {table_name}:")
        table = metadata.tables[table_name]

        # Determine primary key or best column to sort by
        sort_col = None
        if 'id' in table.columns:
            sort_col = table.c.id
        elif 'transaction_id' in table.columns:
             sort_col = table.c.transaction_id

        # Get latest entries
        if sort_col is not None:
            query = select(table).order_by(sort_col.desc()).limit(3)
            with engine.connect() as conn:
                results = conn.execute(query).fetchall()
                if not results:
                    print("  (No records)")
                for row in results:
                    # Convert row to dict for better printing
                    row_dict = dict(row._mapping)
                    print(json.dumps(row_dict, default=json_serial, indent=2))
        else:
            print("  No sortable column (id or transaction_id) found.")

if __name__ == "__main__":
    try:
        check_counts()
        check_latest()
    except Exception as e:
        print(f"Error: {e}")
