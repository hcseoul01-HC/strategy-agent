import sqlite3
import pandas as pd
import os

# 1. 데이터베이스 경로 확인
db_path = './.adk/session.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    
    # 2. 현재 DB에 어떤 서랍(테이블)이 있는지 목록 출력 (디버깅용)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"📊 시스템 내 발견된 테이블: {tables}")

    # 3. 'events' 테이블 추출 시도 (ADK 표준 규격)
    target_table = 'events'
    if target_table in tables:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {target_table}", conn)
            df.to_csv('alpha_hui_backup.csv', index=False, encoding='utf-8-sig')
            print(f"✅ 백업 성공! '{target_table}' 데이터를 'alpha_hui_backup.csv'로 저장했습니다.")
        except Exception as e:
            print(f"❌ 데이터 추출 중 오류 발생: {e}")
    else:
        print(f"❌ 에러: '{target_table}' 테이블을 찾을 수 없습니다. 목록을 확인해주세요.")
    
    conn.close()
else:
    print(f"❌ 에러: {db_path} 경로에 데이터베이스 파일이 없습니다.")