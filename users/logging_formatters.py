from datetime import datetime

from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

        if not log_record.get('module'):
            log_record['module'] = record.module

            # Добавляем filename, если его нет
        #if not log_record.get('filename'):
        #    log_record['filename'] = record.pathname.split('//')[-1]  # Получение только имени файла
        #    print(record.pathname.split('users')[-1])
        log_record['message'] = record.getMessage()

#formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(module) s%(name)s %(message)s')
#"{levelname} - {asctime} - {module} - {filename} - {message}"

