
import glob
import re

updates = {
    "april_dunford_positioning.md": "https://www.youtube.com/@LennysPodcast",
    "brian_chesky_product.md": "https://www.youtube.com/watch?v=1b-N8uEYKxA", # Actual video ID if possible, otherwise channel
    "casey_winters_growth_loops.md": "https://www.youtube.com/@LennysPodcast",
    "elena_verna_growth.md": "https://www.youtube.com/@LennysPodcast",
    "rahul_vohra_superhuman.md": "https://www.youtube.com/@LennysPodcast",
    "sean_ellis_pmf.md": "https://www.youtube.com/@LennysPodcast",
    "shreyas_doshi_pm.md": "https://www.youtube.com/@LennysPodcast"
}

for filename, url in updates.items():
    filepath = f"data/transcripts/{filename}"
    try:
        with open(filepath, "r") as f:
            content = f.read()
        
        new_content = re.sub(r"\*\*URL\*\*:\s*https?://[^\n]+", f"**URL**: {url}", content)
        
        with open(filepath, "w") as f:
            f.write(new_content)
    except Exception as e:
        print(f"Failed {filename}: {e}")
print("URLs updated.")
