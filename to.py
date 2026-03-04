import re
import os
import sqlite3
import argparse
from pathlib import Path

def clean_mysql_sql(mysql_sql_content):
    """
    清理并转换 MySQL SQL 内容为 SQLite 兼容格式
    :param mysql_sql_content: 原始 MySQL SQL 字符串
    :return: 转换后的 SQLite 兼容 SQL 字符串
    """
    # 1. 移除 MySQL 特有配置（引擎、字符集、注释等）
    mysql_specific_patterns = [
        r'ENGINE=InnoDB\s*',
        r'ENGINE=MyISAM\s*',
        r'DEFAULT CHARSET=utf8mb4\s*',
        r'DEFAULT CHARSET=utf8\s*',
        r'COLLATE=[\w_]*\s*',
        r'AUTO_INCREMENT=\d+\s*',
        r'UNSIGNED\s*',  # 移除 UNSIGNED 修饰符
        r'ZEROFILL\s*',   # 移除 ZEROFILL 修饰符
    ]
    for pattern in mysql_specific_patterns:
        mysql_sql_content = re.sub(pattern, '', mysql_sql_content, flags=re.IGNORECASE)

    # 2. 转换自增字段：AUTO_INCREMENT → AUTOINCREMENT（仅主键 INTEGER 列）
    # 先匹配 PRIMARY KEY 前的 AUTO_INCREMENT，替换为 AUTOINCREMENT
    mysql_sql_content = re.sub(
        r'(\s+)AUTO_INCREMENT(\s+)PRIMARY KEY',
        r'\1AUTOINCREMENT\2PRIMARY KEY',
        mysql_sql_content,
        flags=re.IGNORECASE
    )
    # 处理单独的 AUTO_INCREMENT（非主键场景，SQLite 不支持，直接移除）
    mysql_sql_content = re.sub(
        r',?\s*AUTO_INCREMENT\s*',
        '',
        mysql_sql_content,
        flags=re.IGNORECASE
    )

    # 3. 转换数据类型
    type_mapping = {
        r'INT\s*': 'INTEGER',
        r'BIGINT\s*': 'INTEGER',
        r'SMALLINT\s*': 'INTEGER',
        r'TINYINT\s*': 'INTEGER',
        r'VARCHAR\(\d+\)': 'TEXT',
        r'CHAR\(\d+\)': 'TEXT',
        r'TEXT\(\d+\)': 'TEXT',
        r'DATETIME\s*': 'TEXT',
        r'DATE\s*': 'TEXT',
        r'TIME\s*': 'TEXT',
        r'DECIMAL\([^)]*\)': 'REAL',
        r'FLOAT\s*': 'REAL',
        r'DOUBLE\s*': 'REAL',
        r'BOOLEAN\s*': 'INTEGER',
    }
    for mysql_type, sqlite_type in type_mapping.items():
        mysql_sql_content = re.sub(mysql_type, sqlite_type, mysql_sql_content, flags=re.IGNORECASE)

    # 4. 转换 MySQL 函数
    # NOW() → datetime('now')
    mysql_sql_content = re.sub(r'NOW\(\)', "datetime('now')", mysql_sql_content, flags=re.IGNORECASE)
    # CONCAT(a,b) → a || b（简单场景，复杂嵌套需手动处理）
    mysql_sql_content = re.sub(r'CONCAT\(([^,]+),([^)]+)\)', r'\1 || \2', mysql_sql_content, flags=re.IGNORECASE)

    # 5. 移除 MySQL 注释中多余的内容（保留 -- 和 /* */ 注释）
    # 移除 /*! ... */ 这种 MySQL 特有注释
    mysql_sql_content = re.sub(r'/\*![^*/]*\*/', '', mysql_sql_content)

    # 6. 拆分 SQL 语句（按 ; 拆分，处理换行）
    sql_statements = []
    for stmt in mysql_sql_content.split(';'):
        # 清理空行和注释行，只保留有效语句
        cleaned_stmt = '\n'.join([
            line.strip() for line in stmt.split('\n')
            if line.strip() and not line.strip().startswith('--')
        ])
        if cleaned_stmt:
            sql_statements.append(cleaned_stmt + ';')

    return '\n'.join(sql_statements)

def import_to_sqlite(sql_content, sqlite_db_path):
    """
    将转换后的 SQL 内容导入 SQLite 数据库
    :param sql_content: 转换后的 SQLite 兼容 SQL 字符串
    :param sqlite_db_path: SQLite 数据库文件路径（如 ./mydb.sqlite）
    """
    try:
        # 连接 SQLite 数据库（不存在则自动创建）
        conn = sqlite3.connect(sqlite_db_path)
        cursor = conn.cursor()

        # 拆分 SQL 语句并执行（逐行执行避免批量错误）
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        success_count = 0
        fail_count = 0
        failed_stmts = []

        for idx, stmt in enumerate(sql_statements):
            if not stmt:
                continue
            try:
                cursor.execute(stmt)
                success_count += 1
            except sqlite3.Error as e:
                fail_count += 1
                failed_stmts.append((idx + 1, stmt, str(e)))
                # 非致命错误继续执行，最后汇总
                continue

        # 提交事务
        conn.commit()
        print(f"\n✅ 导入完成！")
        print(f"   成功执行语句数：{success_count}")
        print(f"   失败语句数：{fail_count}")

        if failed_stmts:
            print("\n❌ 失败的语句详情：")
            for idx, stmt, err in failed_stmts:
                print(f"   语句 {idx}：{stmt[:100]}...")
                print(f"   错误原因：{err}\n")

    except sqlite3.Error as e:
        print(f"\n💥 数据库连接/执行失败：{e}")
    finally:
        if conn:
            conn.close()

def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='MySQL SQL 转 SQLite 并导入工具')
    parser.add_argument('--mysql-sql', required=True, help='MySQL 备份的 SQL 文件路径（如 ./backup.sql）')
    parser.add_argument('--sqlite-db', required=True, help='SQLite 数据库文件路径（如 ./target.db）')
    parser.add_argument('--output-sql', default='./sqlite_converted.sql', help='转换后的 SQL 文件保存路径（默认 ./sqlite_converted.sql）')
    args = parser.parse_args()

    # 检查输入文件是否存在
    mysql_sql_path = Path(args.mysql_sql)
    if not mysql_sql_path.exists():
        print(f"❌ 错误：MySQL SQL 文件 {mysql_sql_path} 不存在！")
        return

    # 读取 MySQL SQL 文件
    print(f"📖 正在读取 MySQL SQL 文件：{mysql_sql_path}")
    try:
        with open(mysql_sql_path, 'r', encoding='utf-8') as f:
            mysql_sql_content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败：{e}")
        return

    # 转换 SQL 内容
    print("🔧 正在转换 MySQL SQL 为 SQLite 兼容格式...")
    sqlite_sql_content = clean_mysql_sql(mysql_sql_content)

    # 保存转换后的 SQL 文件
    output_sql_path = Path(args.output_sql)
    try:
        with open(output_sql_path, 'w', encoding='utf-8') as f:
            f.write(sqlite_sql_content)
        print(f"💾 转换后的 SQL 文件已保存：{output_sql_path}")
    except Exception as e:
        print(f"❌ 保存转换文件失败：{e}")
        return

    # 导入到 SQLite 数据库
    print(f"📤 正在将转换后的 SQL 导入 SQLite 数据库：{args.sqlite_db}")
    import_to_sqlite(sqlite_sql_content, args.sqlite_db)

if __name__ == '__main__':
    main()
