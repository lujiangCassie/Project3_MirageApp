import logging

import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def main(msg: func.ServiceBusMessage):
    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s', notification_id)
    
    conn = psycopg2.connect(dbname = 'techconfdb', user='udacity@migrateapppostgre', \
                            password='Headway2023', host='migrateapppostgre.postgres.database.azure.com')
    cursor = conn.cursor()

    

    try:
        
        notification_query = cursor.execute("select message, subject from notification where id = {};".format(notification_id))

        
        cursor.execute("select first_name, last_name, email from attendee;")
        attendees = cursor.fetchall()

        for attendee in attendees:
            Mail('{},{},{}'.format({'user@techconf.com'},{attendee[2]},{notification_query}))

        notification_completed_date = datetime.utcnow()
        notification_status = 'Notified {} attendees'.format(len(attendees))
        

       
        update_query = cursor.execute("update notification set status = '{}', completed_date = '{}' where id = {};".format(notification_status, notification_completed_date, notification_id))
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        conn.rollback()
    finally:
       
        cursor.close()
        conn.close()
