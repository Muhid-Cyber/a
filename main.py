from flask import Flask, request, jsonify
import yt_dlp
from urllib.parse import urlparse

app = Flask(__name__)

def is_valid_youtube_url(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc in ['youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be']:
        if parsed_url.netloc in ['youtube.com', 'www.youtube.com', 'm.youtube.com']:
            return "v" in dict(p.split("=",1) for p in parsed_url.query.split("&")) if parsed_url.query else False
        return parsed_url.path[1:] if parsed_url.netloc == 'youtu.be' else False
    return False


@app.route('/audio', methods=['GET'])
def get_audio_info():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter."}), 400
    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid Youtube link format."}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'format': 'bestaudio',
            'extractaudio': True,
             'nocheckcertificate':True,
             'cookiefile': 'cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if info_dict:
                return jsonify({
                    "title": info_dict.get('title', "Unknown Title"),
                    "best_audio_url": info_dict.get('url', "N/A")
                }), 200
            return jsonify({"error": "Video not found"}), 404

    except yt_dlp.utils.DownloadError as e:
        if 'This video is unavailable' in str(e):
            return jsonify({"error": "Video is unavailable or deleted"}), 404
        if 'Please check your internet connection or try again in a few minutes' in str(e):
            return jsonify({"error": "Temporary Server Error"}), 503
        return jsonify({"error": f"An unexpected error happened: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
