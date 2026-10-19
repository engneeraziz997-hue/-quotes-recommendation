🎯 BrainyQuote Scraper

مشروع لاستخراج الاقتباسات من موقع "BrainyQuote" (https://www.brainyquote.com) باستخدام Python، وتنظيمها وتخزينها في قاعدة بيانات SQLite.

📌 نظرة عامة

يعتمد المشروع على عملية كشط هرمي تبدأ بالحروف، ثم الموضوعات الرئيسية والفرعية، وصولًا إلى صفحات الاقتباسات والمؤلفين.

✨ المميزات

- استخراج الاقتباسات والمؤلفين والموضوعات.
- التنقل التلقائي بين صفحات النتائج.
- تخزين البيانات في قاعدة بيانات SQLite.
- منع تكرار البيانات.
- تسجيل الأخطاء وإعادة المحاولة.
- استئناف عملية الكشط بعد التوقف.
- تنظيم البيانات لتسهيل الاستعلام عنها.

🛠️ التقنيات المستخدمة

- Python
- Selenium
- Undetected ChromeDriver
- BeautifulSoup4
- SQLite

📁 بنية المشروع

brainyquote-scraper/
├── create_tables.py
├── new_browser_utils.py
├── new_scrape_indexed_topics.py
├── new_scrape_topics.py
├── new_scrape_pages.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md

⚙️ التثبيت

1. استنساخ المستودع

git clone https://github.com/YOUR_USERNAME/brainyquote-scraper.git
cd brainyquote-scraper

2. إنشاء بيئة افتراضية

python -m venv .venv

تفعيل البيئة على Windows:

.venv\Scripts\activate

3. تثبيت المكتبات

pip install -r requirements.txt

🚀 طريقة التشغيل

1. إنشاء قاعدة البيانات

python create_tables.py

2. تحديد الحرف المطلوب

افتح الملف "new_scrape_indexed_topics.py" وحدد الحرف الذي تريد البدء به.

3. تشغيل عملية الكشط

python new_scrape_indexed_topics.py

🗄️ قاعدة البيانات

الجدول| الوظيفة
"quotes"| تخزين الاقتباسات والمؤلفين والموضوعات
"topics"| تخزين الموضوعات وعدد صفحاتها
"indexed_topics"| ربط الموضوعات الرئيسية بالفرعية
"indexed_topics_info"| تخزين إحصائيات الموضوعات
"lett_of_ind_tops"| ربط الحروف بالموضوعات الرئيسية
"letter_info"| تخزين إحصائيات الحروف
"errors"| تسجيل الأخطاء ومعلومات إعادة المحاولة

💻 مثال على استعلام البيانات

import sqlite3

conn = sqlite3.connect("quotes.db")
cursor = conn.cursor()

cursor.execute(
    "SELECT topic, author, quote FROM quotes LIMIT 10"
)

for row in cursor.fetchall():
    print(row)

conn.close()

📋 المتطلبات

- Python 3.8 أو أحدث.
- متصفح Google Chrome.
- المكتبات المحددة في "requirements.txt".

🔮 التطوير المستقبلي

- إضافة واجهة سطر أوامر للتحكم في عملية الكشط.
- دعم استخراج البيانات من عدة حروف في جلسة واحدة.
- تصدير البيانات إلى CSV وJSON وExcel.
- إضافة اختبارات آلية والتحقق من جودة البيانات.
- دعم قواعد بيانات مثل PostgreSQL.

⚖️ الترخيص

المشروع مرخص بموجب MIT License، وفقًا لشروط ملف "LICENSE".

👨‍💻 المطور

اسم المطور: اكتب اسمك هنا

GitHub: https://github.com/YOUR_USERNAME

---

تم تطوير المشروع باستخدام Python لأتمتة استخراج البيانات وتنظيمها.
