
import json
import urllib.request
from pathlib import Path

PLAYLIST = Path("IPTVMIA 1.m3u")

CHANNELS = {
    "Videolina": "xa0aoxk",
    "T.C.S. TeleCostaSmeralda": "xb5d7v6",
    "L'Unione TV": "xabqoj4",
    "Sardegna Uno": "x893du6",
}


def get_stream(video_id):
    endpoint = (
        "https://www.dailymotion.com/player/metadata/video/"
        + video_id
    )

    request = urllib.request.Request(
        endpoint,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    if not isinstance(data, dict):
        raise Exception("Risposta Dailymotion non valida")

    if "error" in data:
        raise Exception(str(data["error"]))

    qualities = data.get("qualities", {})
    found = []

    for quality, items in qualities.items():
        if isinstance(items, dict):
            items = [items]

        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, dict):
                continue

            stream_url = item.get("url", "")
            stream_type = str(item.get("type", "")).lower()

            if not stream_url:
                continue

            if (
                "mpegurl" in stream_type
                or ".m3u8" in stream_url.lower()
            ):
                found.append((quality, stream_url))

    if found:
        print("Formati HLS trovati:", [x[0] for x in found])
        return found[0][1]

    details = []
    for quality, items in qualities.items():
        if isinstance(items, dict):
            items = [items]

        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    details.append(
                        quality
                        + ": tipo="
                        + str(item.get("type", "assente"))
                        + ", URL presente="
                        + str(bool(item.get("url")))
                    )

    print("Titolo risposta:", data.get("title", "non disponibile"))
    print("Dettagli qualità:", details)
    raise Exception("Nessun indirizzo HLS riconosciuto")


def main():
    if not PLAYLIST.exists():
        raise FileNotFoundError("Playlist non trovata")

    lines = PLAYLIST.read_text(
        encoding="utf-8-sig"
    ).splitlines(True)

    updated = 0

    for channel, video_id in CHANNELS.items():
        try:
            new_url = get_stream(video_id)
            found = False

            for i, line in enumerate(lines):
                if not line.startswith("#EXTINF"):
                    continue

                if channel.lower() not in line.lower():
                    continue

                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith("#"):
                        ending = (
                            "\r\n" if lines[j].endswith("\r\n")
                            else "\n" if lines[j].endswith("\n")
                            else ""
                        )
                        lines[j] = new_url + ending
                        found = True
                        updated += 1
                        break
                break

            print(channel + ": " + (
                "aggiornato" if found else "non trovato nella playlist"
            ))

        except Exception as error:
            print(channel + ": non aggiornato - " + str(error))

    if updated:
        PLAYLIST.write_text("".join(lines), encoding="utf-8")
        print("Playlist salvata. Canali aggiornati:", updated)
    else:
        print("Nessun canale aggiornato.")


if __name__ == "__main__":
    main()
