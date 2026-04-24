# How to Launch Your Website — Beginner's Step-by-Step Guide

You have your domain through Squarespace and your code is ready. Here's exactly what to do next.

---

## The Big Picture (What We're Doing)

```
Your Code → GitHub → GitHub Pages (free hosting) → Your Custom Domain
```

GitHub will store AND host your website for free. Then we tell Squarespace to point your domain at it.

---

## PART 1 — Create a GitHub Account

1. Go to **github.com**
2. Click **"Sign up"** in the top right corner
3. Enter your email address, create a password, and choose a username
   - Your username will be part of your temporary website link, so pick something clean (e.g., `angelagallitano`)
4. Verify your email when GitHub sends you a confirmation message
5. When asked "What kind of work do you do?" — you can skip this
6. Choose the **Free** plan

✅ You now have a GitHub account.

---

## PART 2 — Create a Repository (This is Your Website's Home)

A "repository" (or "repo") is just a folder on GitHub that holds your website files.

1. Once logged in, click the **green "New"** button on the left side, OR click the **"+"** icon in the top right → **"New repository"**

2. Fill in the form:
   - **Repository name:** Type exactly this → `yourusername.github.io`
     - Replace `yourusername` with your actual GitHub username
     - Example: if your username is `angelagallitano`, type `angelagallitano.github.io`
     - ⚠️ This exact format is required for GitHub Pages to work
   - **Description:** Optional — you can write "My website" or leave it blank
   - **Public or Private:** Select **Public** (required for free GitHub Pages hosting)
   - **Add a README file:** Check this box ✅

3. Click the green **"Create repository"** button

✅ Your repository is created.

---

## PART 3 — Upload Your Website Files

Now we put your actual website code into GitHub.

1. You should be on your new repository page. Click **"Add file"** → **"Upload files"**

2. Open the Finder on your Mac and navigate to:
   `/Users/agallitano/Documents/Claude/Projects/endgame.archive`

3. Select all your website files (press **⌘ + A** to select all)
   - Make sure `index.html` is in there — this is the most important file

4. Drag and drop all the selected files into the GitHub upload area in your browser

5. Wait for them all to finish uploading (you'll see a list appear)

6. Scroll down to the **"Commit changes"** section
   - In the first text box, you can type something like: `Add website files`
   - Leave everything else as-is

7. Click the green **"Commit changes"** button

✅ Your files are now on GitHub.

---

## PART 4 — Turn On GitHub Pages (Free Hosting)

1. On your repository page, click **"Settings"** (it's in the top menu bar of your repo)

2. In the left sidebar, scroll down and click **"Pages"**

3. Under **"Branch"**, click the dropdown that says `None` and select **`main`**

4. Leave the folder set to `/ (root)`

5. Click **"Save"**

6. Wait about 1–2 minutes, then refresh the page

7. You should now see a message that says:
   **"Your site is live at https://yourusername.github.io"**

8. Click that link to confirm your website is showing up! 🎉

✅ Your website is live on the internet (on a github.io address).

---

## PART 5 — Connect Your Custom Domain (Squarespace → GitHub)

This step makes your website show up at YOUR domain instead of the github.io address.

### Step A — Tell GitHub your domain name

1. Go back to **Settings → Pages** in your GitHub repo

2. Under **"Custom domain"**, type in your domain name
   - Example: `endgame-archive.com` (use your actual domain, no "https://")

3. Click **"Save"**

4. GitHub will show a message about DNS — leave this tab open, we'll come back to it

---

### Step B — Update DNS in Squarespace

This tells Squarespace where your website actually lives (on GitHub).

1. Log in to **squarespace.com**

2. Go to **Domains** in your account (or **Account → Domains**)

3. Click on your domain name

4. Look for **"DNS Settings"** or **"Advanced DNS"** — click it

5. You need to add 4 "A Records" and 1 "CNAME Record." These are like address labels that point to GitHub.

**Delete any existing A Records first** (if there are any pointing somewhere old).

Then add these **4 A Records:**

| Type | Host | Value |
|------|------|-------|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |

Then add this **1 CNAME Record:**

| Type | Host | Value |
|------|------|-------|
| CNAME | www | yourusername.github.io |

(Replace `yourusername` with your actual GitHub username)

6. Save all the records

---

### Step C — Wait for it to connect

DNS changes take time to spread across the internet. This can take anywhere from **15 minutes to 48 hours** — usually it's under an hour.

You'll know it's working when:
- You go back to GitHub → Settings → Pages and see a green checkmark ✅ next to your domain
- You type your domain in a browser and your website loads

---

## PART 6 — Enable HTTPS (Makes Your Site Secure)

Once your domain is connected and GitHub shows the green checkmark:

1. Go to **Settings → Pages** one more time

2. Check the box that says **"Enforce HTTPS"**

3. Click Save

This gives your site the padlock 🔒 icon in the browser and makes it trusted.

---

## Quick Troubleshooting

**My site shows a 404 error:**
Make sure your main file is named exactly `index.html` (lowercase, no spaces)

**DNS isn't connecting after 24 hours:**
Double-check that the A Records are saved correctly in Squarespace with no typos

**GitHub Pages says "Your site is not published":**
Make sure your repository name is exactly `yourusername.github.io` and the branch is set to `main`

---

## You're Done! 🎉

Once everything connects, anyone in the world can type your domain and see your website.

Going forward, whenever you update your website:
1. Go to your GitHub repository
2. Click the file you want to update → click the pencil ✏️ icon to edit, OR use "Add file → Upload files" for new files
3. Commit the changes — your website will update automatically within a minute or two
