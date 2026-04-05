# Blog Automation — How to Get All API Keys

> Step-by-step guide for every key needed in your `.env` file.

---

## Keys You Need

Configure which platforms to use in `config.json`, then add the corresponding keys to `.env`.

**Always Required (3 keys):**
- `GEMINI_API_KEY`
- `HF_TOKEN`
- `IMGBB_API_KEY`

**Publishing Platforms** — add keys for whichever you enable in `config.json`:
- `DEVTO_API_KEY` — enable `"devto": true`
- `MEDIUM_TOKEN` — enable `"medium": true`
- `MEDIUM_AUTHOR_ID` — required alongside `MEDIUM_TOKEN`

**Social Sharing** — add keys for whichever you enable in `config.json`:
- `TWITTER_API_KEY` — enable `"twitter": true`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`
- `LINKEDIN_ACCESS_TOKEN` — enable `"linkedin": true`
- `LINKEDIN_PERSON_URN`

---

## Key 1: `GEMINI_API_KEY`

| | |
|---|---|
| **Service** | Google Gemini — writes your entire blog |
| **Cost** | FREE — 1,500 requests/day on free tier |
| **Time** | ~3 minutes |

1. Go to https://aistudio.google.com
2. Sign in with your Google account
3. Click **"Get API key"** in the top navigation bar
4. Click **"Create API key"**
5. Choose **"Create API key in new project"** (or select existing)
6. Copy the key — it starts with `AIza...`

```env
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> - No credit card required
> - Free tier is more than enough for daily blogging
> - Model used: `gemini-2.5-flash` (auto-falls back to `gemini-1.5-flash`)
> - Key is tied to your Google account — keep it private

---

## Key 2: `HF_TOKEN`

| | |
|---|---|
| **Service** | Hugging Face — generates AI images via FLUX.1-schnell |
| **Cost** | FREE — generous free tier for inference |
| **Time** | ~5 minutes |

1. Go to https://huggingface.co
2. Click **"Sign Up"** (top right) — use your email or GitHub
3. Verify your email address
4. Click your profile picture → **"Settings"**
5. In the left sidebar, click **"Access Tokens"**
6. Click **"New token"**
7. Fill in: **Name:** `blog-automation` · **Role:** `Read`
8. Click **"Generate a token"**
9. Copy the token — it starts with `hf_...`

```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> - The token only needs "Read" access for the inference API
> - Model used: `black-forest-labs/FLUX.1-schnell`
> - Free tier can be slow (5–15s per image) — that's expected
> - If the model is loading, the script auto-waits and retries

---

## Key 3: `MEDIUM_TOKEN`

| | |
|---|---|
| **Service** | Medium — publishes your blog post |
| **Cost** | FREE |
| **Time** | ~5 minutes |

> ⚠️ **Note:** Medium has restricted new API token generation. Some accounts can get tokens from Settings; others may find the option missing.

1. Go to https://medium.com and log in
2. Click your profile picture → **"Settings"**
3. Scroll down to **"Security and apps"**
4. Look for **"Integration tokens"**
5. In the description box, type `blog-automation`
6. Click **"Get integration token"**
7. Copy the token immediately — it won't be shown again

```env
MEDIUM_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**If the Integration tokens section is missing, use one of these instead:**

- **Option A: Dev.to** — instant, no waiting (see [Key 3-Alt: Dev.to](#key-3-alt-devto-api-key) below)
- **Option B: Hashnode** — instant (see [Key 3-Alt: Hashnode](#key-3-alt-hashnode-api-key) below)
- **Option C: Playwright** — browser automation, no token needed (ask in chat)

---

## Key 3-Alt: Dev.to API Key

| | |
|---|---|
| **Service** | Dev.to — popular tech blog platform, growing fast |
| **Cost** | FREE |
| **Time** | ~3 minutes |

1. Go to https://dev.to and create a free account
2. Click your profile picture → **"Settings"**
3. In the left sidebar scroll to **"Account"** → **"DEV Community API Keys"**
4. In the **"Description"** box type `blog-automation`
5. Click **"Generate API Key"**
6. Copy the key

```env
DEVTO_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Dev.to post API reference:**
```
POST https://dev.to/api/articles
Header: api-key: YOUR_KEY
Body: { "article": { "title": "...", "body_markdown": "...", "published": true } }
```

---

## Key 3-Alt: Hashnode API Key

| | |
|---|---|
| **Service** | Hashnode — professional dev blogging platform |
| **Cost** | FREE |
| **Time** | ~5 minutes |

1. Go to https://hashnode.com and sign up
2. Create your blog (choose a subdomain like `yourname.hashnode.dev`)
3. Click your profile picture → **"Account Settings"**
4. Scroll to the **"Developer"** section
5. Click **"Generate New Token"**
6. Copy the token

You also need your **Publication ID:**
- Go to your blog dashboard (URL: `hashnode.com/yourname/dashboard`)
- Your publication host is: `yourname.hashnode.dev`

**Hashnode uses GraphQL API:**
```
Endpoint: https://gql.hashnode.com
Header: Authorization: YOUR_TOKEN
```

---

## Key 4: `MEDIUM_AUTHOR_ID`

| | |
|---|---|
| **What** | Your unique Medium user ID — needed to post via API |
| **Cost** | FREE |
| **Time** | ~2 minutes (requires `MEDIUM_TOKEN` first) |

**Using the terminal:**

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.medium.com/v1/me
```

Response will look like:

```json
{
  "data": {
    "id": "1a2b3c4d5e6f...",
    "username": "yourname",
    "name": "Your Name"
  }
}
```

Copy the `"id"` value (the long alphanumeric string).

```env
MEDIUM_AUTHOR_ID=1a2b3c4d5e6f7g8h9i0j...
```

**Alternative — Hoppscotch (no terminal needed):**

1. Go to https://hoppscotch.io
2. Set method to `GET`, URL: `https://api.medium.com/v1/me`
3. Add header: `Authorization: Bearer YOUR_MEDIUM_TOKEN`
4. Click **"Send"** and copy the `"id"` value

> - This ID never changes — you only need to fetch it once
> - It's not your username — it's a long internal ID

---

## Key 5: `IMGBB_API_KEY`

| | |
|---|---|
| **Service** | imgbb — hosts your AI images as public URLs |
| **Cost** | FREE forever |
| **Time** | ~3 minutes |

**Why this is needed:** Publishing APIs only accept public image URLs (`https://...`), not local file uploads. imgbb hosts your AI-generated images and returns public URLs the platforms accept.

1. Go to https://imgbb.com
2. Click **"Sign up"** (top right)
3. Register with your email (or Google/Facebook)
4. Verify your email
5. Once logged in, go to https://api.imgbb.com
6. Your API key is shown on that page — copy it

```env
IMGBB_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> - Images are hosted permanently for free
> - No watermarks
> - If imgbb is down, the script continues without that image

---

## Key 6: Twitter API Keys *(4 keys total)*

| | |
|---|---|
| **Service** | Twitter / X — share a catchy tweet after publishing |
| **Cost** | FREE for posting to your own account |
| **Time** | ~15 minutes |

**Why 4 keys?** Twitter uses OAuth 1.0a — the App lock (`API Key` + `Secret`) and your Account lock (`Access Token` + `Secret`). You need all four to post a tweet as yourself.

### Step A — Create a Developer Account

1. Go to https://developer.x.com *(formerly developer.twitter.com)*
2. Click **"Sign in"** — use your existing Twitter/X account
3. Click **"Sign up for Free Account"**
4. Fill in your use-case:
   > *"Personal blog automation tool to auto-share new blog posts I publish. Will only post to my own account."*
5. Agree to the Developer Agreement and submit *(Free tier access is usually immediate)*

### Step B — Create a Project and App

6. In the Developer Portal, click **"Create Project"** → name it `blog-automation`
7. Inside the project, click **"+ Create App"**
8. App name: `blog-automation` *(must be globally unique — add your name if taken)*
9. Copy your **API Key** and **API Key Secret** immediately — shown only once

```env
TWITTER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step C — Set App Permissions to Read + Write

10. In your app's dashboard, click the **"Settings"** tab
11. Scroll to **"User authentication settings"** → click **"Set up"**
12. Fill in:
    - **App permissions:** `Read and Write`
    - **Type of App:** `Automated App or Bot`
    - **Callback URI:** `http://localhost`
    - **Website URL:** `https://github.com` *(or your own site)*
13. Click **"Save"**

> ⚠️ After changing permissions, you **must** regenerate your Access Token and Secret — old ones carry old permissions.

### Step D — Generate Access Token and Secret

14. Go to your app's **"Keys and Tokens"** tab
15. Under **"Authentication Tokens"** → **"Access Token and Secret"**, click **"Generate"**
16. Copy both values — shown only once

```env
TWITTER_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_ACCESS_TOKEN_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> - Free tier: up to 1,500 tweets/month — more than enough
> - If you see a 403 error, app permissions are wrong — repeat Step C and regenerate tokens in Step D
> - Never share these keys — anyone with them can tweet as you

---

## Key 7: LinkedIn API Keys *(2 keys total)*

| | |
|---|---|
| **Service** | LinkedIn — share a professional post after publishing |
| **Cost** | FREE |
| **Time** | ~25 minutes *(OAuth flow is slightly involved)* |

**Why more complex?** LinkedIn uses OAuth 2.0 — you go through a browser-based login once to get an access token. The token lasts 60 days, then you repeat the flow.

You will get 2 things:
- `LINKEDIN_ACCESS_TOKEN` — your auth token *(expires in 60 days)*
- `LINKEDIN_PERSON_URN` — your unique LinkedIn user ID *(never changes)*

### Step A — Create a LinkedIn Developer App

1. Go to https://developer.linkedin.com
2. Click **"Create App"** *(sign in with LinkedIn if needed)*
3. Fill in:
   - **App name:** `blog-automation`
   - **LinkedIn Page:** your profile URL *(e.g. `https://www.linkedin.com/in/yourname/`)*
   - **App logo:** any small image *(even a placeholder)*
4. Check the legal agreement and click **"Create app"**
5. In the app dashboard, go to the **"Auth"** tab
6. Note down your **Client ID** and **Client Secret**

### Step B — Request API Access (Products)

7. Click the **"Products"** tab
8. Find **"Share on LinkedIn"** → click **"Request access"** *(grants `w_member_social` scope — needed to post)*
9. Find **"Sign In with LinkedIn using OpenID Connect"** → Request access *(grants profile + openid scopes — needed to get your ID)*
10. Both are usually approved instantly

### Step C — Set OAuth Redirect URL

11. Go back to the **"Auth"** tab
12. Under **"OAuth 2.0 settings"** → Authorized redirect URLs, click **"Add redirect URL"**
13. Add exactly: `http://localhost:8080/callback`
14. Click **"Update"**

### Step D — Get Your Access Token

15. Open your browser and paste this URL *(replace `YOUR_CLIENT_ID`)*:

```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8080/callback&scope=openid%20profile%20w_member_social
```

16. Log in and click **"Allow"**
17. Your browser redirects to `http://localhost:8080/callback?code=XXXXXX`
    *(Page shows an error — that's fine. Copy the `code` value from the URL bar.)*
18. Exchange the code for an access token:

```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_CODE_FROM_STEP_17" \
  -d "redirect_uri=http://localhost:8080/callback" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

19. Response:

```json
{
  "access_token": "AQX...",
  "expires_in": 5183944,
  "token_type": "Bearer"
}
```

```env
LINKEDIN_ACCESS_TOKEN=AQXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step E — Get Your LinkedIn Person URN

20. Run:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" https://api.linkedin.com/v2/me
```

21. Response:

```json
{
  "id": "abc123xyz",
  "localizedFirstName": "Your",
  "localizedLastName": "Name"
}
```

```env
LINKEDIN_PERSON_URN=abc123xyz
```

*(Just the `id` value — not the full URN string)*

> - Access token expires in ~60 days — to refresh, repeat Step D only
> - `LINKEDIN_PERSON_URN` never changes — save it permanently
> - If you get a 403 error, "Share on LinkedIn" product access may still be pending — wait a few minutes and retry

---

## Final `.env` File

Create a file named exactly `.env` *(with the dot)* in the `blog-automation/` folder. Leave keys blank for platforms you haven't enabled yet.

```env
# ── Core (always required) ───────────────────────────────
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
IMGBB_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ── Publishing platforms ──────────────────────────────────
DEVTO_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MEDIUM_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MEDIUM_AUTHOR_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ── Social sharing ────────────────────────────────────────
TWITTER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_ACCESS_TOKEN_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LINKEDIN_ACCESS_TOKEN=AQXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LINKEDIN_PERSON_URN=abc123xyz
```

> ⚠️ **Security Reminders:**
> - Never share this file with anyone
> - Never paste these keys in a chat, email, or GitHub issue
> - The `.gitignore` already excludes `.env` from git commits
> - If a key is accidentally shared, regenerate it immediately

---

## Quick Status Tracker

Tick these off as you go:

**Always Required:**
- [ ] `GEMINI_API_KEY` — [aistudio.google.com](https://aistudio.google.com)
- [ ] `HF_TOKEN` — [huggingface.co](https://huggingface.co) → Settings → Access Tokens
- [ ] `IMGBB_API_KEY` — [api.imgbb.com](https://api.imgbb.com)

**Publishing** — add for platforms you enable in `config.json`:
- [ ] `DEVTO_API_KEY` — dev.to → Settings → API Keys
- [ ] `MEDIUM_TOKEN` — medium.com → Settings → Security and apps
- [ ] `MEDIUM_AUTHOR_ID` — `curl https://api.medium.com/v1/me`

**Social Sharing** — add for platforms you enable in `config.json`:
- [ ] `TWITTER_API_KEY` — developer.x.com → App → Keys and Tokens
- [ ] `TWITTER_API_SECRET` — same page as above
- [ ] `TWITTER_ACCESS_TOKEN` — same page, under Access Token
- [ ] `TWITTER_ACCESS_TOKEN_SECRET` — same page, under Access Token
- [ ] `LINKEDIN_ACCESS_TOKEN` — OAuth flow (Key 7, Step D above)
- [ ] `LINKEDIN_PERSON_URN` — `curl https://api.linkedin.com/v2/me`

Once your core 3 keys + at least 1 publish platform are in `.env`, run:

```bash
source venv/bin/activate
python main.py "Your First Blog Title" --draft --no-images
```

> Use `--draft` and `--no-images` for your first test run — fastest way to confirm everything is connected before doing a full image-generation + public publish run.

---

## Time Estimates

| Key | Time |
|-----|------|
| `GEMINI_API_KEY` | ~3 min *(instant on Google AI Studio)* |
| `HF_TOKEN` | ~5 min *(signup + settings navigation)* |
| `IMGBB_API_KEY` | ~3 min *(signup + api page)* |
| `DEVTO_API_KEY` | ~3 min *(instant from Dev.to settings)* |
| `MEDIUM_TOKEN` | ~5 min *(if settings page works)* |
| `MEDIUM_AUTHOR_ID` | ~2 min *(one curl command)* |
| Twitter *(all 4 keys)* | ~15 min *(developer account + app setup)* |
| LinkedIn *(token + URN)* | ~25 min *(app setup + OAuth flow)* |
| LinkedIn token refresh | ~5 min *(every 60 days, Step D only)* |

| Setup Scenario | Total Time |
|----------------|-----------|
| Minimum *(Dev.to only)* | ~14 min |
| With Twitter sharing | ~29 min |
| With LinkedIn sharing | ~39 min |
| Full setup *(all platforms)* | ~59 min |
