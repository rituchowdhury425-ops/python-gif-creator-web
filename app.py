from flask import Flask, render_template, request, send_file, session
import os
from PIL import Image

print("✅ THIS IS MY APP.PY")

app = Flask(__name__)
app.secret_key = "gif_creator_secret"


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "GET":
        session["gif_ready"] = False

    gif_ready = session.get("gif_ready", False)

    if request.method == "POST":

        upload_folder = "uploads"
        output_folder = "output"

        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)

        images = request.files.getlist("images")
        print(f"Received {len(images)} image(s)")

        # Remove old uploaded images
        for file in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Save uploaded images
        for image in images:
            if image.filename != "":
                image.save(os.path.join(upload_folder, image.filename))

        print("Images saved successfully!")

        # -----------------------------
        # Animation Speed
        # -----------------------------
        speed = request.form["speed"]

        if speed == "slow":
            duration = 900
        elif speed == "medium":
            duration = 500
        else:
            duration = 200

        # -----------------------------
        # GIF Size
        # -----------------------------
        size = int(request.form["size"])

        gif_images = []

        # Process uploaded images
        for file in sorted(os.listdir(upload_folder)):

            if file.lower().endswith((".jpg", ".jpeg", ".png")):

                path = os.path.join(upload_folder, file)

                img = Image.open(path).convert("RGB")

                img.thumbnail((size, size))

                background = Image.new("RGB", (size, size), "white")

                x = (size - img.width) // 2
                y = (size - img.height) // 2

                background.paste(img, (x, y))

                gif_images.append(background)

        if gif_images:

            output_path = os.path.join(output_folder, "animation.gif")

            # =====================================
            # SINGLE IMAGE → Floating Animation
            # =====================================
            if len(gif_images) == 1:

                original = gif_images[0]

                frames = []

                movement = [0, 4, 8, 12, 16, 20, 16, 12, 8, 4, 0]

                for move in movement:

                    frame = Image.new("RGB", (size, size), "white")

                    frame.paste(original, (move, 0))

                    frames.append(frame)

                frames[0].save(
                    output_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=duration,
                    loop=0
                )

            # =====================================
            # MULTIPLE IMAGES → Normal GIF
            # =====================================
            else:

                gif_images[0].save(
                    output_path,
                    save_all=True,
                    append_images=gif_images[1:],
                    duration=duration,
                    loop=0
                )

            print("GIF created successfully!")

            gif_ready = True
            session["gif_ready"] = True

    return render_template("index.html", gif_ready=gif_ready)


@app.route("/output/<filename>")
def output_file(filename):
    return send_file(os.path.join("output", filename))


@app.route("/download")
def download():
    return send_file("output/animation.gif", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)