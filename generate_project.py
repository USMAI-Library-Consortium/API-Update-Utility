import argparse
import os
import json


def main(project_name: str):
    disallowed_chars: set = ("*", "/", "\\", ":", "?",
                             '"', "'", ">", "<", "|", ".", "@")

    for char in disallowed_chars:
        if char in project_name:
            raise ValueError(f"Project name '{
                             project_name}' includes disallowed characters '{char}'")
    project_path = f"projects/{project_name}/"

    # Check if the project already exists
    if os.path.exists(project_path):
        raise ValueError(f"Project with name '{project_name}' already exists.")

    # If the project does not exist, create the folder
    os.makedirs(project_path)

    # Move the boilerplate files into the new project
    with open("src/projectfiles/config_template.json", "r") as f:
        config = json.load(f)

    with open(f"{project_path}/config.json", "w") as f:
        json.dump(config, f, indent=2)

    with open("src/projectfiles/instructions.txt", "r") as inst_f:
        instructions = inst_f.read()

    with open(f"{project_path}/instructions.txt", "w") as inst_f_out:
        inst_f_out.write(instructions)

    with open("src/projectfiles/progress.csv", "r", encoding="utf-8-sig") as prog_f:
        progress_file = prog_f.read()

    with open(f"{project_path}/progress.csv", "w", encoding="utf-8-sig") as prog_f_out:
        prog_f_out.write(progress_file)

    with open(f"{project_path}/__init__.py", "w") as f:
        f.write("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "project_name", help="The name of the project to generate.", type=str)
    args = parser.parse_args()

    main(args.project_name)
