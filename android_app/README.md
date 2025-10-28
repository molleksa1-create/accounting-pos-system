# تطبيق نقطة البيع (POS) للأندرويد

## نظرة عامة

تطبيق أندرويد متكامل لإدارة نقطة البيع (POS) مع دعم:
- ✅ المزامنة مع الخادم
- ✅ العمل الأوفلاين
- ✅ قارئ الباركود
- ✅ الطباعة
- ✅ التقارير

## المتطلبات

- Android Studio 2023.1+
- Android SDK 28+
- Java 11+
- Kotlin 1.9+

## المكتبات المستخدمة

```gradle
// Networking
implementation 'com.squareup.retrofit2:retrofit:2.9.0'
implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
implementation 'com.squareup.okhttp3:okhttp:4.10.0'

// Database
implementation 'androidx.room:room-runtime:2.5.2'
implementation 'androidx.room:room-ktx:2.5.2'

// UI
implementation 'androidx.appcompat:appcompat:1.6.1'
implementation 'com.google.android.material:material:1.9.0'
implementation 'androidx.constraintlayout:constraintlayout:2.1.4'

// Barcode Scanner
implementation 'com.journeyapps:zxing-android-embedded:4.3.0'

// JSON
implementation 'com.google.code.gson:gson:2.10.1'

// Coroutines
implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.4'

// LiveData & ViewModel
implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.1'
implementation 'androidx.lifecycle:lifecycle-livedata-ktx:2.6.1'
```

## البنية الأساسية

```
android_app/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/molle/pos/
│   │   │   │   ├── ui/
│   │   │   │   │   ├── activities/
│   │   │   │   │   │   ├── MainActivity.kt
│   │   │   │   │   │   ├── LoginActivity.kt
│   │   │   │   │   │   ├── POSActivity.kt
│   │   │   │   │   │   ├── ProductsActivity.kt
│   │   │   │   │   │   └── ReportsActivity.kt
│   │   │   │   │   ├── fragments/
│   │   │   │   │   │   ├── CartFragment.kt
│   │   │   │   │   │   ├── ProductsFragment.kt
│   │   │   │   │   │   └── ReportsFragment.kt
│   │   │   │   │   └── adapters/
│   │   │   │   │       ├── ProductsAdapter.kt
│   │   │   │   │       └── CartAdapter.kt
│   │   │   │   ├── data/
│   │   │   │   │   ├── api/
│   │   │   │   │   │   ├── ApiService.kt
│   │   │   │   │   │   └── ApiClient.kt
│   │   │   │   │   ├── db/
│   │   │   │   │   │   ├── AppDatabase.kt
│   │   │   │   │   │   ├── entities/
│   │   │   │   │   │   └── daos/
│   │   │   │   │   └── repository/
│   │   │   │   │       ├── ProductRepository.kt
│   │   │   │   │       ├── SalesRepository.kt
│   │   │   │   │       └── SyncRepository.kt
│   │   │   │   ├── viewmodel/
│   │   │   │   │   ├── POSViewModel.kt
│   │   │   │   │   ├── ProductsViewModel.kt
│   │   │   │   │   └── ReportsViewModel.kt
│   │   │   │   ├── utils/
│   │   │   │   │   ├── Constants.kt
│   │   │   │   │   ├── PreferenceManager.kt
│   │   │   │   │   └── SyncManager.kt
│   │   │   │   └── models/
│   │   │   │       ├── Product.kt
│   │   │   │       ├── SalesInvoice.kt
│   │   │   │       └── CartItem.kt
│   │   │   └── res/
│   │   │       ├── layout/
│   │   │       ├── drawable/
│   │   │       ├── values/
│   │   │       └── menu/
│   │   └── test/
│   ├── build.gradle
│   └── proguard-rules.pro
├── build.gradle
├── settings.gradle
└── gradle.properties
```

## الميزات الرئيسية

### 1. واجهة الكاشير
- عرض المنتجات
- إضافة المنتجات للسلة
- حساب الإجمالي
- طرق الدفع المختلفة

### 2. قارئ الباركود
- قراءة باركود المنتجات
- إضافة سريعة للسلة
- البحث عن المنتجات

### 3. المزامنة
- تحميل المنتجات من الخادم
- حفظ الفواتير محلياً
- إرسال الفواتير عند الاتصال

### 4. العمل الأوفلاين
- قاعدة بيانات محلية
- المزامنة التلقائية
- إشعارات الحالة

### 5. التقارير
- تقارير المبيعات اليومية
- إحصائيات الأداء
- تقارير المخزون

## التثبيت والتشغيل

### 1. فتح المشروع في Android Studio

```bash
cd android_app
```

### 2. تحديث gradle.properties

```properties
sdk.dir=/path/to/android/sdk
```

### 3. بناء المشروع

```bash
./gradlew build
```

### 4. تشغيل التطبيق

```bash
./gradlew installDebug
```

## إعدادات الخادم

تحديث `Constants.kt`:

```kotlin
object Constants {
    const val API_BASE_URL = "http://your-server.com/api/v1/"
    const val SYNC_INTERVAL = 5 * 60 * 1000 // 5 دقائق
    const val OFFLINE_MODE_ENABLED = true
}
```

## الاختبار

```bash
./gradlew test
```

## النشر

### 1. إنشاء keystore

```bash
keytool -genkey -v -keystore app.keystore -keyalg RSA -keysize 2048 -validity 10000
```

### 2. بناء APK

```bash
./gradlew assembleRelease
```

### 3. توقيع APK

```bash
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore app.keystore app-release-unsigned.apk alias_name
```

## الدعم والمساعدة

للمزيد من المعلومات، راجع التوثيق الكاملة.
