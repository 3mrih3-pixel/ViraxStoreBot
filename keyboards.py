# -*- coding: utf-8 -*-
"""
keyboards.py
------------
كل لوحات المفاتيح (Reply / Inline) المستخدمة في البوت موجودة هنا
حتى يسهل التعديل عليها دون العبث بمنطق الهاندلرز.
"""

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from config import BTN_SHOP, BTN_EARN, BTN_DAILY, BTN_PROFILE, BTN_HELP


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """القائمة الرئيسية الثابتة أسفل الشاشة."""
    keyboard = [
        [BTN_SHOP, BTN_EARN],
        [BTN_DAILY, BTN_PROFILE],
        [BTN_HELP],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def shop_list_keyboard(products) -> InlineKeyboardMarkup:
    """قائمة المنتجات كأزرار Inline، كل منتج بزر منفصل."""
    buttons = []
    for p in products:
        text = f"{p['name']} - {p['price']} نقطة"
        buttons.append([InlineKeyboardButton(text, callback_data=f"shop_view:{p['product_id']}")])
    return InlineKeyboardMarkup(buttons)


def product_view_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """زر الشراء وزر الرجوع لصفحة عرض المنتج."""
    buttons = [
        [InlineKeyboardButton("🛒 شراء", callback_data=f"buy:{product_id}")],
        [InlineKeyboardButton("⬅️ رجوع للمتجر", callback_data="shop_back")],
    ]
    return InlineKeyboardMarkup(buttons)


def purchase_confirm_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """أزرار تأكيد أو إلغاء عملية الشراء."""
    buttons = [
        [
            InlineKeyboardButton("✅ تأكيد", callback_data=f"buy_confirm:{product_id}"),
            InlineKeyboardButton("❌ إلغاء", callback_data=f"buy_cancel:{product_id}"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def earn_points_keyboard() -> InlineKeyboardMarkup:
    """قائمة طرق ربح النقاط."""
    buttons = [
        [InlineKeyboardButton("🎁 الهدية اليومية", callback_data="earn_daily")],
        [InlineKeyboardButton("🔒 قريباً", callback_data="earn_soon_1")],
        [InlineKeyboardButton("🔒 قريباً", callback_data="earn_soon_2")],
        [InlineKeyboardButton("🔒 قريباً", callback_data="earn_soon_3")],
    ]
    return InlineKeyboardMarkup(buttons)
