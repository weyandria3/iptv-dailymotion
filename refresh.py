
import json
import re
import urllib.request
from pathlib import Path

PLAYLIST = Path("IPTVMIA 1.m3u")

CHANNELS = {
    "Videolina": "xa0aoxk",
    "TeleCostaSmeralda": "xb5d7v6",
    "L'Unione TV": "xabqoj4",
    "Sardegna Uno": "x893du6",
}


def get_stream(video_id):
    url = (
        "https://www.dailymotion.com/player/metadata/video/"
        + video_id
    )
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))

    qualities = data.get("qualities", {})
    for quality in ("auto", "1080", "720", "480", "380", "240"):
        for item in qualities.get(quality, []):
            if item.get("type") == "application/x-mpegURL":
                return item["url"]

    raise Exception("Nessun indirizzo HLS disponibile")


def main():
    if not PLAYLIST.exists():
        raise FileNotFoundError("Playlist non trovata: " + str(PLAYLIST))

    lines = PLAYLIST.read_text(encoding="utf-8-sig").splitlines(True)
    updated = 0

    for channel, video_id in CHANNELS.items():
        try:
            new_url = get_stream(video_id)
            found = False

            for i, line in enumerate(lines):
                if line.startswith("#EXTINF") and channel.lower() in line.lower():
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith("#"):
                            ending = "\r\n" if lines[j].endswith("\r\n") else "\n"
                            lines[j] = new_url + ending
                            found = True
                            updated += 1
                            break
                    break

            print(channel + ": " + ("aggiornato" if found else "non trovato"))

        except Exception as error:
            print(channel + ": non aggiornato - " + str(error))

    if updated:
        PLAYLIST.write_text("".join(lines), encoding="utf-8")
        print("Playlist salvata. Canali aggiornati:", updated)
    else:
        print("Nessun canale aggiornato.")


if __name__ == "__main__":
    main()
