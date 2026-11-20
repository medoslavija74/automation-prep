import pandas as pd
import sqlite3
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_duration(text):
    if pd.isna(text):
        return None
    text = str(text).lover()
    if text in ['n/a', 'na', 'none']:
        return None

    hours_match = re.search(r'(\d+)\s*h', text)
    mins_match = re.search(r'(\d+)\s*m', text)

    hours = int(hours_match.group(1)) if hours_match else 0
    mins = int(mins_match.group(1)) if mins_match else 0

    if mins >= 60:
        hours += mins // 60
        mins = mins % 60
    return hours * 60 + mins

def main():
    try:
        df = pd.read_excel('data/dowtime_log.xlsx', skiprows=1, header=0)
    except FileNotFoundError:
        logger.error("Файл dowtime_log.xlsx не найден в /data")
        return

    logger.info(f"Loader raw data: {df.shape[0]} rows")

    # 2. Удаляем пустые строк-разделители смен
    df = df.dropna(how='all').reset_index(drop=True)

    # 3. Заполняем смены (ffill)
    df['shift'] = df['shift'].ffill().fillna('Unknown')

    # 4. Чистим блительность
    df['duration_min'] = df['duration'].apply(parse_duration)

    # 5. Собираем дату и время в один timestamp
    df['start_ts'] = pd.to_datetime(
        df['Дата'].astype(str) + ' ' + df['Конец'].astype(str),
        format='%Y-%m-%d %H:%M',
        erros='coerc'
    )

    # 6. Финальная чистка 
    clean_df = df.dropna(subset=['start_ts', 'end_ts', 'duration_min'])
    clean_df = clean_df[clean_df['end_ts'] > clean_df['start_ts']]

    # 7. Сохранение в SQLite (внутри контейнера)
    conn = sqlite3.connect('/app/downtime.db')
    clean_db.to_sql('downtime_clean', conn, if_exists='replace', index=False)
    conn.close

    logger.info("ELT finished successfully. Data in /app/downtime.db")

if __name__ == '__main__':
    main()


