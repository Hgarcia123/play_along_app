from flask import (
    Flask, render_template, request
)

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        #TODO: Validate URL with regex
        url = request.form.get('youtube_url')

        #TODO:Call function get_audiotrack

        print(url)

    return render_template('base.html')

def get_audiotrack():
    ...

if __name__ == '__main__':
    main()
