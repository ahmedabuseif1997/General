namespace EscapeHouse.Core
{
    // نفس فكرة game/systems/tension.py
    public static class TensionSystem
    {
        private static readonly (int threshold, string text)[] Levels =
        {
            (0, "الهدوء غريب، بس مفيش حاجة مخيفة لسه."),
            (20, "قلبك بيدق أسرع شوية من غير سبب واضح."),
            (40, "بتحس إن فيه حد بيراقبك من بعيد."),
            (60, "الصوت في البيت بقى أعلى. خطوات، همس، مش فاكر إيه بالظبط."),
            (80, "مش قادر تفكر صح. البيت بقى حي، وبيكرهك."),
        };

        public static string Describe(int tension)
        {
            string description = Levels[0].text;
            foreach (var (threshold, text) in Levels)
            {
                if (tension >= threshold) description = text;
            }
            return description;
        }

        // 0..1 — يستخدم في تعتيم/فليكر الإضاءة كل ما التوتر يعلى
        public static float NormalizedIntensity(int tension) => Mathf_Clamp01(tension / 100f);

        private static float Mathf_Clamp01(float v)
        {
            if (v < 0f) return 0f;
            if (v > 1f) return 1f;
            return v;
        }
    }
}
