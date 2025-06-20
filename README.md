# 📊 Market Alert Bot (NASDAQ + NYSE)

### 🛠️ الوظيفة:

- 🔍 مراقبة السوق (After + Pre + Regular)
- 🚨 تنبيهات لحظية:
    - زخم عالي ( +3% )
    - سيولة استثنائية
    - فوليوم عالي
    - السعر الحالي عند الكسر

---

### الملفات:

- `market_alert_bot.py` → سكربت المراقبة الرئيسي
- `all_us_stocks.txt` → قائمة الأسهم (NASDAQ + NYSE)
- `symbol.py` → تحديث قائمة الأسهم
- `requirements.txt` → مكتبات بايثون

---

### طريقة التشغيل:

```bash
# تحديث قائمة الأسهم
python symbol.py

# تشغيل البوت
python market_alert_bot.py
