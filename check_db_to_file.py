'''
Write entries into a txt file
'''

import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, select, func
import json
from datetime import date, time
from decimal import Decimal

def json_serial(obj):
    if isinstance(obj, (date, time)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError ("Type %s not serializable" % type(obj))

DATABASE_URL = "mysql+pymysql://root:0798628195Far@localhost/Supermarket"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

with open("db_report.txt", "w", encoding="utf-8") as f:
    f.write("TABLE COUNTS:\n")
    for table_name in sorted(metadata.tables.keys()):
        table = metadata.tables[table_name]
        count_query = select(func.count()).select_from(table)
        with engine.connect() as conn:
            count = conn.execute(count_query).scalar()
            f.write(f"  {table_name}: {count}\n")

    for table_name in sorted(metadata.tables.keys()):
        f.write(f"\nLATEST 3 ENTRIES IN {table_name}:\n")
        table = metadata.tables[table_name]
        
        sort_col = None
        if 'id' in table.columns:
            sort_col = table.c.id
        elif 'transaction_id' in table.columns:
             sort_col = table.c.transaction_id
             
        if sort_col is not None:
            query = select(table).order_by(sort_col.desc()).limit(3)
            with engine.connect() as conn:
                results = conn.execute(query).fetchall()
                if not results:
                    f.write("  (No records)\n")
                for row in results:
                    row_dict = dict(row._mapping)
                    f.write(json.dumps(row_dict, default=json_serial, indent=2) + "\n")
        else:
            f.write("  No sortable column (id or transaction_id) found.\n")
