# Ads-Wise — Google & Meta verification status

Last checked: 2026-10-28 ~13:30 UTC.

## Google — Analytics project (spa-management-511514 / 56808345708)
- Branding verified; data access under review.
- Thread "[Action Needed] OAuth Verification Request Acknowledgement" (gmail thread 1a1820f8d0bbe76d):
  Google 2026-10-28 10:30Z "unable to access the video link" → we replied 12:49Z with https://youtu.be/e8Ldys5oOh8.
- e8Ldys5oOh8 is publicly reachable signed-out (YouTube oEmbed 200 on 2026-10-28).
- No new Google request since our reply. Action: none until Google writes again.

## Google — Ads project (spa-ads-agent / 86860594118)
- Thread gmail 1a167da9dda3735c. Google 2026-10-26 22:23Z: previous video (https://youtu.be/RjiSDy5AYiM)
  "does not present the OAuth consent screen workflow". Needs a new video + reply in that thread.
- Verified 2026-10-28 from a clean browser:
  - Reviewer login `ahmedabuseif1997+google-review@gmail.com` (password in our 25 Oct reply) works;
    it owns exactly one workspace, "Google OAuth Review Workspace".
  - Ad Accounts → Connect Google Ads sends: client_id 86860594118-hqdubqidu3tbeohtfj6j4i65se64e1mt,
    scope = `https://www.googleapis.com/auth/adwords` only, prompt=select_account consent,
    access_type=offline, redirect https://ads-wise.com/api/integrations/google/callback.
    Scope matches the single scope under review.
  - The Analytics reviewer login `ahmedabuseif1997+adswise-google-review@gmail.com` also works
    (workspaces: "Google OAuth Review Workspace 2", "Google OAuth Review Workspace").
- Recording shot list (keep it ~2–3 min, 1080p, blur emails/customer IDs, never show passwords/tokens):
  1. Browser address bar visible on https://ads-wise.com/app (already signed in, or type email only and cut the password entry).
  2. Workspace selector → "Google OAuth Review Workspace".
  3. Ad Accounts → Connect Google Ads.
  4. Google account chooser (address bar shows accounts.google.com, client is Ads-Wise).
  5. Consent screen: click "Show all services"/expand so "See, edit, create and delete your Google Ads accounts and data"
     (https://www.googleapis.com/auth/adwords) is readable; pause 3 s.
  6. Allow → back in Ads-Wise → choose an accessible Google Ads customer → Connect selected account.
  7. Sync → Analytics shows live campaign metrics.
  8. Campaigns → create a test campaign draft → Approvals → approve.
  9. Publish ("Create paused campaign") → confirm status PAUSED in Ads-Wise.
  10. ads.google.com → same customer → Campaigns → show the new campaign with status Paused.
  11. Optional: Ad Accounts → Disconnect, to show revocation.
- Then: YouTube upload as Unlisted → test in a private window → Cloud Console (spa-ads-agent)
  → Google Auth Platform → Data Access → replace demo video URL → Save → reply in thread 1a167da9dda3735c.

## Meta — Ads-Wise Agent (app 1418356733153531, business 1401711459689233)
- Original admin blocked by Meta security checkpoint; ahmedabuseif1997@gmail.com has full business access and is a registered developer.
- Pending: assign that profile as app Administrator (App Dashboard → App roles → Roles → Add people → Administrator),
  after current admins complete Meta's developer confirmation. Do not recreate or delete the app.
- To confirm once inside the dashboard: app mode (Development/Live), App Review submission status,
  and permissions ads_management / ads_read / business_management (Advanced access).
- No Meta emails in Gmail in the last 30 days; this session has no Meta login or Graph API token.
