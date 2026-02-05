import pymysql
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def create_users_table():
    try:
        # DB 연결 (이미 생성된 ybigta_db에 접속)
        conn = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            db=os.getenv("MYSQL_DB"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            # 1. 기존에 혹시나 있을지 모를 테이블 삭제 (선택 사항)
            # cursor.execute("DROP TABLE IF EXISTS users")
            
            # 2. users 테이블 생성 (에러 로그에 나온 email, password, username 필드 기준)
            sql = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(sql)
            print("✅ 'users' 테이블이 성공적으로 생성되었습니다.")
            
        conn.commit()
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_users_table()