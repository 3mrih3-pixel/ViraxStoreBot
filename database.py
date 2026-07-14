# -*- coding: utf-8 -*-
"""
database.py
-----------
طبقة التعامل مع قاعدة بيانات SQLite.
كل الدوال هنا "متزامنة" (sync) عن قصد لتبسيط الكود وتفادي الأخطاء
على بيئات مثل Pydroid 3، ويتم استدعاؤها من داخل الهاندلرز غير المتزامنة
مباشرة (sqlite3 سريع بما يكفي لحجم استخدام بوت عادي).
"""

import sqlite3
import datetime
from contextlib import closing

from config import DB_PATH


class Database:
    """
    كلاس مسؤول عن كل عمليات القراءة والكتابة في قاعدة البيانات.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        # check_same_thread=False لأن مكتبة تيليجرام قد تستدعي من ثريدات مختلفة
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """إنشاء الجداول إذا لم تكن موجودة."""
        with closing(self._connect()) as conn:
            cur = conn.cursor()

            # جدول المستخدمين
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    points INTEGER NOT NULL DEFAULT 0,
                    last_daily TEXT,
                    purchases_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)

            # جدول المنتجات
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    product_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    allow_repurchase INTEGER NOT NULL DEFAULT 0
                )
            """)

            # جدول المشتريات
            cur.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    purchase_date TEXT NOT NULL
                )
            """)

            conn.commit()

    # ------------------------------------------------------------------
    # دوال المستخدمين
    # ------------------------------------------------------------------

    def get_or_create_user(self, user_id: int, username: str) -> sqlite3.Row:
        """إرجاع بيانات المستخدم، وإنشاء حساب جديد له إذا لم يكن موجوداً."""
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cur.fetchone()

            if row is None:
                now = datetime.datetime.utcnow().isoformat()
                cur.execute(
                    """INSERT INTO users (user_id, username, points, last_daily, purchases_count, created_at)
                       VALUES (?, ?, 0, NULL, 0, ?)""",
                    (user_id, username or "", now),
                )
                conn.commit()
                cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = cur.fetchone()
            else:
                # تحديث اليوزرنيم في حال تغيّر
                if username and row["username"] != username:
                    cur.execute(
                        "UPDATE users SET username = ? WHERE user_id = ?",
                        (username, user_id),
                    )
                    conn.commit()
            return row

    def get_user(self, user_id: int):
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return cur.fetchone()

    def add_points(self, user_id: int, amount: int):
        """إضافة نقاط (قد تكون سالبة للخصم) مع ضمان ألا يقل الرصيد عن صفر."""
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            if row is None:
                return False
            new_points = row["points"] + amount
            if new_points < 0:
                new_points = 0
            cur.execute(
                "UPDATE users SET points = ? WHERE user_id = ?",
                (new_points, user_id),
            )
            conn.commit()
            return True

    def set_points(self, user_id: int, amount: int):
        """تعيين رصيد محدد مباشرة (لا يقل عن صفر)."""
        amount = max(0, amount)
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET points = ? WHERE user_id = ?",
                (amount, user_id),
            )
            conn.commit()

    def update_last_daily(self, user_id: int, timestamp_iso: str):
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET last_daily = ? WHERE user_id = ?",
                (timestamp_iso, user_id),
            )
            conn.commit()

    def increment_purchases_count(self, user_id: int):
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET purchases_count = purchases_count + 1 WHERE user_id = ?",
                (user_id,),
            )
            conn.commit()

    def get_all_users(self):
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users ORDER BY points DESC")
            return cur.fetchall()

    # ------------------------------------------------------------------
    # دوال المنتجات
    # ------------------------------------------------------------------

    def add_product(self, name, description, price, product_type, content, allow_repurchase=0):
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO products (name, description, price, product_type, content, allow_repurchase)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (name, description, price, product_type, content, allow_repurchase),
            )
            conn.commit()
            return cur.lastrowid

    def delete_product(self, product_id: int) -> bool:
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            conn.commit()
            return cur.rowcount > 0

    def get_product(self, product_id: int):
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            return cur.fetchone()

    def get_all_products(self):
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM products ORDER BY product_id ASC")
            return cur.fetchall()

    def update_product_price(self, product_id: int, new_price: int) -> bool:
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE products SET price = ? WHERE product_id = ?",
                (new_price, product_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def update_product_content(self, product_id: int, new_content: str) -> bool:
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE products SET content = ? WHERE product_id = ?",
                (new_content, product_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def toggle_allow_repurchase(self, product_id: int):
        """تبديل خاصية السماح بإعادة الشراء لمنتج معين."""
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute("SELECT allow_repurchase FROM products WHERE product_id = ?", (product_id,))
            row = cur.fetchone()
            if row is None:
                return None
            new_value = 0 if row["allow_repurchase"] else 1
            cur.execute(
                "UPDATE products SET allow_repurchase = ? WHERE product_id = ?",
                (new_value, product_id),
            )
            conn.commit()
            return new_value

    # ------------------------------------------------------------------
    # دوال المشتريات
    # ------------------------------------------------------------------

    def has_purchased(self, user_id: int, product_id: int) -> bool:
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM purchases WHERE user_id = ? AND product_id = ? LIMIT 1",
                (user_id, product_id),
            )
            return cur.fetchone() is not None

    def record_purchase(self, user_id: int, product_id: int):
        now = datetime.datetime.utcnow().isoformat()
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO purchases (user_id, product_id, purchase_date) VALUES (?, ?, ?)",
                (user_id, product_id, now),
            )
            conn.commit()

    # ------------------------------------------------------------------
    # الإحصائيات
    # ------------------------------------------------------------------

    def get_stats(self):
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) AS c FROM users")
            users_count = cur.fetchone()["c"]

            cur.execute("SELECT COUNT(*) AS c FROM products")
            products_count = cur.fetchone()["c"]

            cur.execute("SELECT COUNT(*) AS c FROM purchases")
            purchases_count = cur.fetchone()["c"]

            cur.execute("SELECT COALESCE(SUM(points), 0) AS s FROM users")
            total_points = cur.fetchone()["s"]

            return {
                "users_count": users_count,
                "products_count": products_count,
                "purchases_count": purchases_count,
                "total_points": total_points,
            }


# نسخة واحدة مشتركة من قاعدة البيانات تُستخدم في كل ملفات المشروع
db = Database()
