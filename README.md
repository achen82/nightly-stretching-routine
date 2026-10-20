# Nightly Stretching Routine

A mobile-first stretching timer web app: a 30-step nightly routine
(19:10 total — 16:45 of stretching plus 29 × 5-second transitions), with a
large countdown, audible cues, and editable steps. Includes a Plan & Tiers
tab: rank exercises in tiers A (most important) to F, drag the time slider
(5:00 up to the full routine, 30-second steps) and the app builds tonight's
routine from your top tiers; skip exercises for the night, and add your own
exercises with custom durations (30 seconds by default). The whole app is
one self-contained `index.html` file — no build step, no dependencies.

## Run it on a Raspberry Pi (Docker)

Requires Docker with the Compose plugin on the Pi.

First time (the clone creates the `nightly-stretching-routine` folder):

```bash
git clone https://github.com/achen82/nightly-stretching-routine.git
cd nightly-stretching-routine
docker compose up -d --build
```

To update later:

```bash
cd nightly-stretching-routine
git pull
docker compose up -d --build
```

Then open it from any device on your network:

```
http://<your-pi-ip>:8080
```

Find the Pi's IP with `hostname -I` on the Pi.

To stop it: `docker compose down`.

## Add it to your iPhone home screen

1. Open `http://<your-pi-ip>:8080` in Safari.
2. Tap **Share** → **Add to Home Screen** → **Add**.
3. It launches full-screen like a native app. Your step edits and settings
   are saved in the browser on that device.

Note: iOS limits web apps in the background — keep the app on screen with
the display on while a routine runs so the timer and sounds stay reliable
(the app asks the phone to keep the screen awake where supported).

## No Docker? Any static server works

The app is a single HTML file, e.g.:

```bash
python3 -m http.server 8080
```

then open `http://<your-pi-ip>:8080/index.html`.
