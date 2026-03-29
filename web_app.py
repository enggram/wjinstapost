from flask import Flask, request, render_template_string, send_file
from PIL import Image, ImageOps
import io

app = Flask(__name__)

# This is the HTML code for your webpage
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>White Jersey Collage Maker</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 40px; background-color: #f4f4f9; color: #333; text-align: center; }
        .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h2 { color: #2c3e50; }
        input[type="file"] { margin: 20px 0; padding: 10px; border: 2px dashed #bdc3c7; border-radius: 5px; width: 100%; box-sizing: border-box; }
        button { background-color: #27ae60; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 5px; cursor: pointer; transition: background 0.3s; }
        button:hover { background-color: #2ecc71; }
        .note { font-size: 12px; color: #7f8c8d; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🏏 Insta Collage Maker</h2>
        <form action="/generate" method="post" enctype="multipart/form-data">
            <input type="file" name="photos" accept="image/jpeg, image/png, image/jpg" multiple required>
            <button type="submit">Generate & Download</button>
        </form>
        <p class="note">Please select exactly 2, 3, or 4 photos at once.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/generate', methods=['POST'])
def generate():
    # Get the uploaded files
    files = request.files.getlist('photos')
    num_images = len(files)
    
    if num_images not in [2, 3, 4]:
        return "<h3>Error: You must upload exactly 2, 3, or 4 images. Go back and try again.</h3>", 400

    # Load images directly from the web request (no saving to Mac required)
    try:
        images = [Image.open(f.stream) for f in files]
    except Exception as e:
        return f"Error reading images: {e}", 400

    canvas = Image.new('RGB', (1080, 1080), 'white')
    top_heavy = (0.5, 0.15)
    center_top = (0.5, 0.25)

    # --- 2 IMAGE LAYOUT ---
    if num_images == 2:
        w1, h1 = images[0].size
        if (w1 / h1) < 1: 
            img1 = ImageOps.fit(images[0], (540, 1080), centering=top_heavy)
            img2 = ImageOps.fit(images[1], (540, 1080), centering=top_heavy)
            canvas.paste(img1, (0, 0))
            canvas.paste(img2, (540, 0))
        else:
            img1 = ImageOps.fit(images[0], (1080, 540), centering=center_top)
            img2 = ImageOps.fit(images[1], (1080, 540), centering=center_top)
            canvas.paste(img1, (0, 0))
            canvas.paste(img2, (0, 540))

    # --- 3 IMAGE LAYOUT ---
    elif num_images == 3:
        aspect_ratios = [(img.width / img.height, i, img) for i, img in enumerate(images)]
        aspect_ratios.sort(reverse=True, key=lambda x: x[0])
        widest_img = aspect_ratios[0][2]
        other_imgs = [img for _, _, img in aspect_ratios[1:]]

        if aspect_ratios[0][0] > 1.1:
            top = ImageOps.fit(widest_img, (1080, 540), centering=center_top)
            bl = ImageOps.fit(other_imgs[0], (540, 540), centering=top_heavy)
            br = ImageOps.fit(other_imgs[1], (540, 540), centering=top_heavy)
            canvas.paste(top, (0, 0))
            canvas.paste(bl, (0, 540))
            canvas.paste(br, (540, 540))
        else:
            left_img = ImageOps.fit(images[0], (540, 1080), centering=top_heavy)
            tr_img = ImageOps.fit(images[1], (540, 540), centering=top_heavy)
            br_img = ImageOps.fit(images[2], (540, 540), centering=top_heavy)
            canvas.paste(left_img, (0, 0))
            canvas.paste(tr_img, (540, 0))
            canvas.paste(br_img, (540, 540))

    # --- 4 IMAGE LAYOUT ---
    elif num_images == 4:
        for i, img in enumerate(images):
            resized = ImageOps.fit(img, (540, 540), centering=top_heavy)
            row = i // 2
            col = i % 2
            canvas.paste(resized, (col * 540, row * 540))

    # Prepare the image to be downloaded by the browser
    img_io = io.BytesIO()
    canvas.save(img_io, 'JPEG', quality=95)
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='instagram_ready.jpg')

if __name__ == '__main__':
    # Run the web server on port 5000
    app.run(host='0.0.0.0', port=5000)