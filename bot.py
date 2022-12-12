from flask import Flask, render_template, request
import os
import aiml
from autocorrect import spell

from bta.controller import converter_bpmn_aiml

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'tmp_dir/bpmn_files'
app.config['CATEGORIES_FOLDER'] = 'categories'
app.config['BPMN_FILES'] = 'tmp_dir/bpmn_files'
app.config['BPMN_FINITE_STATE'] = 'tmp_dir/bpmn_finite_state'
app.config['BPMN_SIMPLIFIED'] = 'tmp_dir/bpmn_simplified'
app.config['CATEGORY_FOLDER'] = 'categories'
app.config['STATIC_FOLDER'] = 'static'


BRAIN_FILE="./pretrained_model/aiml_pretrained_model.dump"
k = aiml.Kernel()


def load_data():
    if os.path.exists(BRAIN_FILE):
        print("Loading from brain file: " + BRAIN_FILE)
        k.loadBrain(BRAIN_FILE)
    else:
        print("Parsing aiml files")
        k.bootstrap(learnFiles="./pretrained_model/learningFileList.aiml", commands="load aiml")
        print("Saving brain file: " + BRAIN_FILE)
        # k.saveBrain(BRAIN_FILE)

load_data()

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/reload_knowledge")
def reload_knowledge():
    load_data()

    return ({})

@app.route("/get")
def get_bot_response():
    query = request.args.get('msg')
    query = [spell(w) for w in (query.split())]
    question = " ".join(query)
    response = k.respond(question)
    if response:
        return (str(response))
    else:
        return (str(":)"))

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':



        f = request.files['file']
        filename = f.filename
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        converter_bpmn_aiml(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        load_data()


        return '''<html><body><h2>BPMN file loaded sucessfully.</h2>
                <p><input type="button" value="back to the chatbot" onclick="voltar()"></p>
                <script>
                    function voltar() {
                        
                        window.history.back();
                    }
                    
                </script></body></html>'''


if __name__ == "__main__":
    # app.run()
    app.run(host='0.0.0.0', port='5000')


