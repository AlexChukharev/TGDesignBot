import psycopg2
from DBHandler.config import load_config


# Delete template by id.
def delete_template(template_id):
    sql = 'delete from templates where template_id = %s'
    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (template_id,))
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
