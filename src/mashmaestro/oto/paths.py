from mashmaestro import resources
from mashmaestro.paths import find_resources, repo_path

download_path = f"{repo_path}/downloads/try1"
processed_path = f"{repo_path}/downloads/proc"
bot2_pickle = find_resources(resources_package=resources, resource_name="bot2.pickle")
bot_path = f"{repo_path}/downloads/bot"
kaggle_csv = find_resources(resources_package=resources, resource_name="recipeData.csv")
