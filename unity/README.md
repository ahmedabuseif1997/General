# نسخة Unity 3D — بيت الرعب

نسخة 3D (Whitebox) من نفس لعبة الهروب النصية، لنفس المحتوى بالظبط
(10 غرف، نفس الأكواد والأدلة والفخاخ) — لكن دلوقتي بتتلعب بحركة أول
شخص (WASD + ماوس) وكيباد فعلي على الشاشة.

**كل حاجة هنا سكريبتات C# بس + ملف بيانات JSON.** مفيش مشاهد (`.unity`)
متعملة مسبقًا، ومفيش موديلات 3D أو تكستشرز — الأوض بتتبني بالكود وقت
التشغيل (مكعبات وألوان بسيطة، أسلوب Whitebox زي ما اتفقنا).

## ليه مفيش مشروع Unity كامل جاهز؟

عمداً. ملفات مشروع Unity الكاملة (`.unity` scenes، `.meta` files، إعدادات
الـ Render Pipeline) مرتبطة بنسخة الـ Editor المثبتة عندك، ولو اتعملت
من غير Unity Editor فعلي ممكن تتعطل لما تفتحها. بدل كده، كل حاجة بتتبني
تلقائيًا وقت التشغيل من كود C# عادي — يشتغل على أي مشروع Unity حديث
(2021 LTS فما فوق) من غير أي تجهيز يدوي في الـ Editor غير خطوة واحدة.

## خطوات التشغيل

1. افتح Unity Hub، اعمل **New Project** → قالب **3D (Built-in Render
   Pipeline)** (أسهل اختيار، أو URP لو عندك خبرة بيه).
2. من الـ repo، انسخ الفولدرين دول جوه `Assets/` بتاع المشروع الجديد:
   - `unity/Assets/Scripts/`
   - `unity/Assets/Resources/`
3. سيب Unity يعمل compile للسكريبتات (بيحصل أوتوماتيك).
4. في الـ Hierarchy، اعمل **Create Empty** — سمّيه أي اسم (مثلاً
   `Bootstrap`).
5. اسحب سكريبت `GameBootstrapper.cs` عليه من الـ Project window (أو
   Add Component → اكتب GameBootstrapper).
6. دوس **Play**. كده اللاعب، الكاميرا، الأوضة الأولى، والواجهة كلها
   بتتبني لوحدها.

## أزرار اللعب

| الزرار | الفعل |
|---|---|
| WASD | حركة |
| الماوس | نظرة |
| E | فحص غرض / فتح الكيباد لو واقف قدام الباب |
| Tab | فتح/قفل قائمة الجرد |
| H | تلميح للغرفة الحالية |
| Esc | تفكيك قفل الماوس (أو قفل شاشة الكيباد) |

## حدود معروفة (Known Limitations)

- **النص العربي في الواجهة**: uGUI Text في Unity مش بيعمل "shaping"
  للعربي بشكل تلقائي (يعني ممكن الحروف تتعرض منفصلة أو معكوسة). لو
  محتاج عرض عربي سليم 100%، الحل المعتاد هو مكتبة
  [Arabic Support for Unity](https://github.com/Konash/arabic-support-unity)
  (مجانية، بتعمل reshape للنص قبل ما يتعرض) مع TextMeshPro. مش مدمجة
  هنا عشان تفادي إضافة Package خارجي بدون موافقتك.
- **الشكل البصري**: مكعبات وألوان بسيطة فقط (Whitebox) — زي ما اتفقنا،
  مفيش موديلات أو إضاءة سينمائية.
- **مفيش صوت**: مفيش أي ملفات صوتية متضافة. `RoomLight` بيعمل فليكر
  بصري بس مبني على مستوى التوتر.
- **الشيدر**: الكود بيدوّر تلقائيًا على أنسب شيدر متاح (URP Lit، أو
  Standard، أو Legacy Diffuse) — لو المواد ظهرت وردي/بنفسجي (Missing
  Shader)، يبقى الـ Render Pipeline بتاعك محتاج شيدر تاني مش من اللي
  بيدوّر عليهم الكود.
- الكود ده اتكتب ومتفحصش (brace-balance check بس) — مقدرش أفتح Unity
  Editor فعليًا من هنا عشان أختبره بصريًا. لو طلعت أي أخطاء compile،
  ابعتهالي وأصلحها.

## البنية

```
unity/Assets/
  Scripts/
    Data/            RoomData.cs, RoomLoader.cs — تحميل rooms.json
    Core/            GameState, KeypadLogic, TensionSystem,
                      GameManager, GameBootstrapper
    Player/          FirstPersonController
    Interaction/      Interactable, PlayerInteractor
    Doors/           KeypadDoor
    UI/              HUDController (بيبني الـ Canvas كله بالكود)
    LevelGeneration/  RoomBuilder (بيبني الأوضة whitebox + الأغراض)
  Resources/Data/
    rooms.json        نفس محتوى game/data/rooms.yaml، بس بصيغة JSON
```
