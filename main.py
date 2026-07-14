# -*- coding: utf-8 -*-
"""
main.py
-------
نقطة تشغيل البوت. هنا يتم بناء التطبيق وتسجيل كل الهاندلرز بالترتيب الصحيح.

للتشغيل على Pydroid 3:
1. تأكد من تثبيت المكتبة عبر: pip install python-telegram-bot --upgrade
2. شغّل هذا الملف مباشرة (main.py) عبر زر التشغيل ▶️ في Pydroid 3.
3. تأكد من وجود اتصال إنترنت فعّال على الجهاز.
"""

import logging

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import (
    BOT_TOKEN, DEV_SECRET_ENABLED, DEV_SECRET_CODE,
    BTN_SHOP, BTN_EARN, BTN_DAILY, BTN_PROFILE, BTN_HELP,
)

from handlers import user as user_handlers
from handlers import admin as admin_handlers
from handlers import dev_secret as dev_secret_handlers


# إعداد تسجيل الأحداث (Logging) لمتابعة عمل البوت وتشخيص أي مشاكل
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context) -> None:
    """التقاط أي خطأ غير متوقع وتسجيله بدل أن يتوقف البوت بالكامل."""
    logger.error("حدث خطأ أثناء معالجة تحديث: %s", context.error, exc_info=context.error)


def build_application() -> Application:
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # -----------------------------------------------------------------
    # المجموعة 0 (أولوية عالية): مفتاح تجربة المطور
    # يجب أن يُفحص قبل أي هاندلر آخر للنصوص، وفقط عندما تطابق الرسالة الكود تماماً
    # -----------------------------------------------------------------
    if DEV_SECRET_ENABLED:
        application.add_handler(
            MessageHandler(
                filters.Regex(f"^{DEV_SECRET_CODE}$"),
                dev_secret_handlers.dev_secret_handler,
            ),
            group=0,
        )

    # -----------------------------------------------------------------
    # أوامر عامة
    # -----------------------------------------------------------------
    application.add_handler(CommandHandler("start", user_handlers.start_command), group=1)
    application.add_handler(CommandHandler("help", user_handlers.help_command), group=1)

    # -----------------------------------------------------------------
    # أوامر الأدمن
    # -----------------------------------------------------------------
    application.add_handler(CommandHandler("adminhelp", admin_handlers.admin_help_command), group=1)
    application.add_handler(CommandHandler("addproduct", admin_handlers.add_product_command), group=1)
    application.add_handler(CommandHandler("delproduct", admin_handlers.delete_product_command), group=1)
    application.add_handler(CommandHandler("editprice", admin_handlers.edit_price_command), group=1)
    application.add_handler(CommandHandler("editcontent", admin_handlers.edit_content_command), group=1)
    application.add_handler(CommandHandler("allowrebuy", admin_handlers.toggle_repurchase_command), group=1)
    application.add_handler(CommandHandler("listproducts", admin_handlers.list_products_command), group=1)
    application.add_handler(CommandHandler("addpoints", admin_handlers.add_points_command), group=1)
    application.add_handler(CommandHandler("delpoints", admin_handlers.remove_points_command), group=1)
    application.add_handler(CommandHandler("listusers", admin_handlers.list_users_command), group=1)
    application.add_handler(CommandHandler("stats", admin_handlers.stats_command), group=1)

    # -----------------------------------------------------------------
    # أزرار القائمة الرئيسية (Reply Keyboard) - نصوص ثابتة
    # -----------------------------------------------------------------
    application.add_handler(
        MessageHandler(filters.Regex(f"^{BTN_SHOP}$"), user_handlers.shop_handler), group=1
    )
    application.add_handler(
        MessageHandler(filters.Regex(f"^{BTN_EARN}$"), user_handlers.earn_points_handler), group=1
    )
    application.add_handler(
        MessageHandler(filters.Regex(f"^{BTN_DAILY}$"), user_handlers.daily_gift_message_handler), group=1
    )
    application.add_handler(
        MessageHandler(filters.Regex(f"^{BTN_PROFILE}$"), user_handlers.profile_handler), group=1
    )
    application.add_handler(
        MessageHandler(filters.Regex(f"^{BTN_HELP}$"), user_handlers.help_command), group=1
    )

    # -----------------------------------------------------------------
    # أزرار Inline (Callback Query)
    # -----------------------------------------------------------------
    application.add_handler(
        CallbackQueryHandler(user_handlers.shop_back_callback, pattern="^shop_back$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(user_handlers.product_view_callback, pattern="^shop_view:"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(user_handlers.buy_callback, pattern="^buy:"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(user_handlers.buy_confirm_callback, pattern="^buy_confirm:"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(user_handlers.buy_cancel_callback, pattern="^buy_cancel:"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(user_handlers.earn_points_callback, pattern="^earn_"), group=1
    )

    # معالج الأخطاء العام
    application.add_error_handler(error_handler)

    return application


def main():
    application = build_application()
    logger.info("🚀 البوت يعمل الآن...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
