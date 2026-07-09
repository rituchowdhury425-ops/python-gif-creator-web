from flask import Flask, render_template, request, send_file, session
import os
from PIL import Image

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

        # Clear old uploads
        for file in os.listdir(upload_folder):
            os.remove(os.path.join(upload_folder, file))

        # Save new images
        for image in images:
            image.save(os.path.join(upload_folder, image.filename))

        print("Images saved successfully!")

        gif_images = []

        for file in sorted(os.listdir(upload_folder)):

            if file.endswith((".jpg", ".jpeg", ".png")):

                path = os.path.join(upload_folder, file)

                img = Image.open(path)

                img.thumbnail((500, 500))

                background = Image.new("RGB", (500, 500), "white")

                x = (500 - img.width) // 2
                y = (500 - img.height) // 2

                background.paste(img, (x, y))

                gif_images.append(background)


        if gif_images:

            output_path = os.path.join(output_folder, "animation.gif")

            gif_images[0].save(
                output_path,
                save_all=True,
                append_images=gif_images[1:],
                duration=500,
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