# Auto YouTube Channel — Tech/AI News (Fully Automated, No Server, No Card)

Ye app har din khud topic uthata hai, script likhta hai, voice-over banata hai,
stock footage jodta hai, video assemble karta hai, thumbnail banata hai, aur
YouTube par upload kar deta hai — **GitHub Actions par chalega, koi server ya
credit card nahi chahiye.**

## Pipeline

```
News Topic -> AI Script (Groq) -> Voice-over (Piper) -> Stock Footage (Pexels)
   -> Final Video -> Thumbnail -> YouTube Upload
```

## Setup — ek baar karna hai (~20-30 min)

### Step 1: Free API keys lo (sab free, koi card nahi chahiye)

| Service | Kya milega | Link |
|---|---|---|
| NewsAPI | News topics | https://newsapi.org/register |
| Pexels | Free stock video | https://www.pexels.com/api/ |
| Groq | Free, fast AI script writer | https://console.groq.com/keys |

Teeno par signup karo, apni **API key copy** kar lo (baad mein chahiye hongi).

### Step 2: YouTube API access setup karo

1. https://console.cloud.google.com par jaake naya project banao
2. "YouTube Data API v3" search karke **Enable** karo
3. Left menu -> Credentials -> **Create Credentials -> OAuth Client ID**
   - Agar consent screen maange to "External" choose karo, apna email daal ke save karo (Testing mode chalega)
   - Application type: **Desktop app**
4. JSON file download karo, naam badal ke `client_secrets.json` rakho

### Step 3: Apne PC par ek baar YouTube authorize karo

Apne computer par (server nahi, apna hi laptop/PC):

```bash
git clone <tumhara-repo-url>
cd auto-youtube-channel
pip install -r requirements.txt
```

`client_secrets.json` ko `config/` folder mein daalo, phir:

```bash
python generate_youtube_token.py
```

Browser khulega — apne YouTube channel wale Google account se login/authorize karo.
Terminal mein ek JSON print hoga — **ise copy kar lo**, ye tumhara `YOUTUBE_TOKEN_JSON` secret banega.

### Step 4: Code ko GitHub par daalo

Agar zip file se shuru kar rahe ho:

```bash
cd auto-youtube-channel
git init
git add .
git commit -m "Initial setup"
```

GitHub.com par naya **repository** banao (public rakho, taaki Actions minutes free/unlimited milein), phir:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 5: GitHub Secrets add karo

Apne repo par jaake: **Settings -> Secrets and variables -> Actions -> New repository secret**

Ye 5 secrets add karo:

| Secret Name | Value |
|---|---|
| `NEWS_API_KEY` | NewsAPI se mili key |
| `PEXELS_API_KEY` | Pexels se mili key |
| `GROQ_API_KEY` | Groq se mili key |
| `YOUTUBE_CLIENT_SECRETS_JSON` | `config/client_secrets.json` file ka **pura content** paste karo |
| `YOUTUBE_TOKEN_JSON` | Step 3 mein jo JSON print hua tha, **wahi** paste karo |

### Step 6: Test run karo

Repo mein **Actions** tab par jaao -> "Daily AI News Video" workflow select karo ->
**Run workflow** button dabao (manual trigger). 5-10 minute mein pura pipeline
chalega aur video YouTube par upload ho jayegi.

Agar error aaye, "pipeline-output" artifact download karke dekh sakte ho ya
logs padh sakte ho — error message paste karke bata dena, fix kar denge.

### Step 7: Automatic daily run

Kuch nahi karna — `.github/workflows/daily_video.yml` mein already schedule
set hai (**roz subah 9 AM IST**). Ab ye khud chalega, forever, free.

Time change karna ho to workflow file mein `cron: "30 3 * * *"` line edit karo
(UTC time hota hai, IST se 5:30 ghante peeche).

## Important Notes

- **YouTube policy risk**: Fully automated, zero-edit, mass-produced content
  YouTube ki spam/reused-content policy ke under demonetize ya remove ho sakta
  hai — khaaskar agar frequency badhaoge.
- **Free tier limits**: NewsAPI 100 req/day, Groq generous free tier, GitHub
  Actions public repo = unlimited free minutes (2000 min/month agar private
  repo rakha to).
- **YouTube quota**: Default daily upload quota ~6 videos/day tak safe hai.
- **Security**: `client_secrets.json` aur `token.json` kabhi bhi repo mein
  commit mat karo — sirf GitHub Secrets mein rakho (`.gitignore` already
  inhe block karta hai).

## File Structure

```
auto-youtube-channel/
├── .github/workflows/daily_video.yml   # roz automatic chalane wala workflow
├── config/settings.yaml                # non-secret settings
├── topic_fetcher.py                    # Step 1: news topic uthata hai
├── script_writer.py                    # Step 2: Groq se AI script likhta hai
├── voice_generator.py                  # Step 3: Piper se voice-over banata hai
├── visual_fetcher.py                   # Step 4: Pexels se stock footage
├── video_builder.py                    # Step 5: final video assemble karta hai
├── thumbnail_generator.py              # Step 6: thumbnail banata hai
├── youtube_uploader.py                 # Step 7: YouTube par upload karta hai
├── generate_youtube_token.py           # ONE-TIME: apne PC par chalao
├── secrets_loader.py                   # environment variables se secrets padhta hai
├── main.py                             # sabko ek saath chalata hai
└── requirements.txt
```
