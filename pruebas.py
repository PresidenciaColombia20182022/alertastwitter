import psycopg2

try:
    con = psycopg2.connect(
        database="TW_tendencias",
        user="postgres",
        password="Postgres21.",
        host="192.168.80.60",
        port="5432"
    )
    cur = con.cursor()
    postgres_insert_query = """ INSERT INTO TENDENCIA (TREND, TWEETVOLUME, FECHA) VALUES (%s,%s,%s)"""
            #record_to_insert = (list(data_final['trend']), list(data_final['tweet_volume']), list(data_final['date']))
    #record_to_insert = data_final
    record_to_insert = ("Fajardo",  154671.0, "2022-05-10")
    cur.execute(postgres_insert_query,record_to_insert)
    con.commit()
    count = cur.rowcount
    print(count, "Record inserted successfully into mobile table")
except (Exception, psycopg2.Error) as error:
    print("Failed to insert record into twiter table", error)




finally:
    # closing database connection.
    if con:
        cur.close()
        con.close()
        print("PostgreSQL connection is closed")