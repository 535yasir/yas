# Market Alert Bot (NASDAQ + NYSE)

✅ مراقبة السوق الأمريكي (After + Pre + Regular)  
✅ تنبيه الزخم المفاجئ  
✅ كسر القمة / القاع  
✅ تنبيه سيولة استثنائية  
✅ تقرير Top 10 Momentum كل 15 دقيقة

---

### الملفات:

- `market_alert_bot.py` — سكربت البوت الرئيسي
- `symbol.py` — لتحديث قائمة الأسهم (NASDAQ + NYSE Common Stocks فقط)
- `all_us_stocks.txt` — يتم توليده من `symbol.py`
- `requirements.txt` — مكتبات البايثون المطلوبة

---

### طريقة التشغيل:

1️⃣ تحديث قائمة الأسهم:

```bash
python symbol.py
