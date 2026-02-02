import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("LASTFM_API_KEY")
api_secret = os.environ.get("LASTFM_SHARED_SECRET")

import pylast

network = pylast.LastFMNetwork(
    api_key=api_key,
    api_secret=api_secret
)

artist_name = "Drake"
artist = network.get_artist(artist_name)

top_tracks = artist.get_top_tracks(limit=10)

rows = []

for track_obj, weight_obj in top_tracks:
    track_name = track_obj.get_title()

    # popularity proxies
    playcount = track_obj.get_playcount()
    listeners = track_obj.get_listener_count()

    # duration in milliseconds (may be None or 0)
    duration_ms = track_obj.get_duration() or 0

    rows.append({
        "track_name": track_name,
        "playcount": int(playcount) if playcount is not None else 0,
        "listeners": int(listeners) if listeners is not None else 0,
        "duration_ms": int(duration_ms),
        "duration_min": (int(duration_ms) / 60000) if duration_ms else None
    })

df = pd.DataFrame(rows)
print("Top 10 Drake Tracks on Last.fm:")
print(df.to_string())
print("\n")

df_sorted = df.sort_values("listeners", ascending=True)
print("Bottom 3 tracks by listeners:")
print(df_sorted.head(3))
print("\n")

df_clean = df.dropna(subset=["duration_min"]).copy()

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_clean, x="duration_min", y="listeners", s=100)
plt.title(f"{artist_name}: Duration vs Listeners (Last.fm)", fontsize=14, fontweight="bold")
plt.xlabel("Duration (minutes)", fontsize=12)
plt.ylabel("Listeners", fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

def get_top_tags(track_obj, max_tags=5):
    tags = track_obj.get_top_tags(limit=max_tags)
    # tags are (TagObject, WeightObject)
    return [tag.item.get_name() for tag in tags]

df["top_tags"] = [
    get_top_tags(network.get_track(artist_name, name), max_tags=5)
    for name in df["track_name"]
]

df["n_tags"] = df["top_tags"].apply(len)

print("Tracks with their top tags:")
for idx, row in df.iterrows():
    print(f"  {row['track_name']}: {', '.join(row['top_tags'])}")
print("\n")

tags_exploded = df[["track_name", "listeners", "top_tags"]].explode("top_tags")
tag_counts = tags_exploded["top_tags"].value_counts()
print("Top 15 most common track tags:")
print(tag_counts.head(15))
print("\n")

plt.figure(figsize=(12, 6))
tag_counts.head(15).plot(kind="bar", color="steelblue")
plt.title(f"{artist_name}: Most Common Track Tags (Top 10 Tracks)", fontsize=14, fontweight="bold")
plt.xlabel("Tag", fontsize=12)
plt.ylabel("Count", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.show()

