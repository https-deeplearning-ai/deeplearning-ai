# How to Set Up Jupyter AI Locally?

This repo contains the notebooks for the DeepLearning.AI course: **Jupyter AI: AI coding in notebooks**.

To set up  <a href="https://github.com/jupyterlab/jupyter-ai" target="_blank">Jupyter AI</a> locally and run the notebooks on your machine, follow the steps in this guide.

## Installing Jupyter AI

This course uses Jupyter AI v3 beta (3.0.0b7), as Jupyter AI v3 is not yet officially released. To install the beta version, run this command in your terminal:

`pip install "jupyter-ai==3.0.0b7"`

Once installation is complete, navigate to your working directory and launch JupyterLab by typing `jupyter lab`. You should now see the chat bubble in the left sidebar.

Note: 3.0.0b8 beta version was released after the course was filmed. Feel free to explore the newest version as it has enhanced UI. 

## Setting Up the Model Provider in JupyterLab

Before you can start interacting with Jupyter AI, you need to configure the model provider and API key:

- Click **Settings** in the top menu bar
- Select **AI Settings** from the drop-down menu
- Under `Chat model`, select your preferred model (this course uses `openai/gpt-5-chat-latest`) and click `Update Chat Model`
- Under `Secrets and API keys`, enter your API key
  
## Accessing Course Notebooks

You can download the notebook of each exercise by clicking on **File** in the top menu bar and then selecting **Download** from the drop-down menu. Or you can access them at this <a href="https://github.com/https-deeplearning-ai/sc-jupyterAI-notebooks" target="_blank">repo</a>.

- You can find the dependencies in this <a href="https://github.com/https-deeplearning-ai/sc-jupyterAI-notebooks/blob/main/requirements.txt" target="_blank">requirements file</a>.
- For the third notebook, you can get the Serper API key by signing up for a free account at <a href="https://serper.dev/" target="_blank">serper.dev</a>

## Additional Features - AI Personas

In the course, you mainly interacted with Jupyternaut, the default AI Persona. In the current beta version, the AI persona does not come with any additional tools to read, edit, or search for files. These features are currently being developed and will make the default AI persona more powerful.

You can also create your own custom AI persona to tailor the assistant's behavior to your specific needs and equip it with the tools you want. You can read more about AI personas <a href="https://jupyter-ai.readthedocs.io/en/v3/developers/entry_points_api/personas_group.html" target="_blank">here</a>.
