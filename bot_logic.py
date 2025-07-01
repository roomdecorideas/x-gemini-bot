# bot_logic.py
import tweepy
import google.generativeai as genai
import requests
import random
import os

def get_us_trends(client):
    """Mendapatkan trending hashtag dari Amerika Serikat."""
    USA_WOEID = 23424977  # Where On Earth ID untuk USA
    try:
        trends = client.get_place_trends(id=USA_WOEID)
        hashtags = [trend['name'] for trend in trends[0]['trends'] if trend['name'].startswith('#')]
        return hashtags[:5] # Ambil 5 teratas
    except Exception as e:
        print(f"Error mendapatkan tren: {e}")
        return None

def generate_content_with_gemini(api_key, hashtag, custom_link=""):
    """Membuat tweet dan prompt gambar menggunakan Gemini."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Create a viral tweet in English about the trending hashtag: {hashtag}.
    The tweet must be engaging, relevant, and under 280 characters.
    If a custom link is provided, include it naturally in the tweet. Custom link: {custom_link}
    
    After the tweet, on a new line, write '||' and then a short, descriptive prompt for an AI image generator to create a relevant, photorealistic image for this tweet.
    
    Example format:
    This is the generated tweet text about {hashtag}. Check this out! {custom_link}
    ||A photorealistic image of a cat programming on a laptop, dark room, glowing screen.
    """
    
    try:
        response = model.generate_content(prompt)
        parts = response.text.split('||')
        tweet_text = parts[0].strip()
        image_prompt = parts[1].strip() if len(parts) > 1 else hashtag # fallback
        return tweet_text, image_prompt
    except Exception as e:
        print(f"Error dengan Gemini: {e}")
        return None, None

def get_image(image_prompt):
    """Mencari dan mengunduh gambar dari Unsplash (sebagai contoh)."""
    # NOTE: Unsplash API lebih baik, tapi untuk simple, kita 'scrap' source-nya.
    # Ini tidak direkomendasikan untuk produksi. Gunakan API resmi Pexels/Unsplash.
    try:
        url = f"https://source.unsplash.com/800x450/?{image_prompt.replace(' ', ',')}"
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open("temp_image.jpg", "wb") as f:
                f.write(response.content)
            return "temp_image.jpg"
    except Exception as e:
        print(f"Error mengunduh gambar: {e}")
        return None

def run_bot_instance(x_creds, gemini_keys, custom_link):
    """Menjalankan satu siklus penuh untuk satu akun."""
    try:
        # 1. Setup Klien X.com
        client = tweepy.Client(
            consumer_key=x_creds['api_key'],
            consumer_secret=x_creds['api_secret'],
            access_token=x_creds['access_token'],
            access_token_secret=x_creds['access_secret']
        )
        auth = tweepy.OAuth1UserHandler(
            x_creds['api_key'], x_creds['api_secret'],
            x_creds['access_token'], x_creds['access_secret']
        )
        api_v1 = tweepy.API(auth) # Dibutuhkan untuk upload media

        # 2. Dapatkan Tren US
        trends = get_us_trends(client)
        if not trends:
            print("Tidak ada tren yang ditemukan.")
            return
        
        selected_hashtag = random.choice(trends)
        print(f"Memilih hashtag: {selected_hashtag}")

        # 3. Hasilkan Konten dengan Gemini
        gemini_api_key = random.choice(gemini_keys)
        tweet_text, image_prompt = generate_content_with_gemini(gemini_api_key, selected_hashtag, custom_link)
        if not tweet_text:
            print("Gagal membuat konten.")
            return

        # 4. Dapatkan Gambar
        image_path = get_image(image_prompt)
        if not image_path:
            print("Gagal mendapatkan gambar, memposting tanpa gambar.")
            client.create_tweet(text=tweet_text)
            return

        # 5. Posting ke X.com dengan Gambar
        media = api_v1.media_upload(filename=image_path)
        client.create_tweet(text=tweet_text, media_ids=[media.media_id_string])
        print(f"Postingan berhasil dikirim dengan hashtag {selected_hashtag}!")
        
        # Hapus file gambar sementara
        os.remove(image_path)

    except Exception as e:
        print(f"Terjadi kesalahan besar: {e}")
