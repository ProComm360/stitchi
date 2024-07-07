import datetime
from typing import Optional

import typer
from rich import box
from rich.align import Align
from rich.prompt import Prompt, Confirm

from rich.console import Console
from rich.table import Table
from rich.text import Text

from backend.classes import VideoEditor
from backend.funcs import pull_from_directory, return_current_directory, change_current_directory

console = Console()
app = typer.Typer(no_args_is_help=True)


@app.command(short_help="stiches a video together. takes base index, addon index, and output name")
def add(base_video_index: int, add_video_index: int, output_name: Optional[str] = None):
    videos = pull_from_directory(recurse=True)
    v1 = videos[base_video_index]
    v2 = videos[add_video_index]

    if output_name:
        if output_name[-1:-4] != ".mp4":
            raise ValueError(f"output name {output_name} is missing the '.mp4' extension!")
    if not output_name:
        output_name = f"COMBINED - {str(datetime.date.today())} - {v1.stem}-{v2.stem}.mp4"
    # We can change this in the config later on if we want to make this configurable
    export_path = f"{v1.folder_path}/{output_name}"

    VideoEditor.join_and_save(v1, v2, export_path)
    typer.echo(f"[red]Complete! Combined {v2.filename} to the end of {v2.filename}")


@app.command(short_help="trims a video. takes index, start (in seconds), end or duration (seconds), and output name.")
def cut(
        video_index: int,
        start: int,
        end: Optional[int] = None,
        duration: Optional[int] = None,
        output_name: Optional[str] = None
):
    videos = pull_from_directory(recurse=True)
    v1 = videos[video_index]

    if output_name:
        if output_name[-1:-4] != ".mp4":
            raise ValueError(f"output name {output_name} is missing the '.mp4' extension!")
    if not output_name:
        output_name = f"Trimmed - {str(datetime.date.today())} - {v1.stem} - from {start}.mp4"
    # We can change this in the config later on if we want to make this configurable
    export_path = f"{v1.folder_path}/{output_name}"

    VideoEditor.cut_and_save(v1, export_path, start, end, duration)

    typer.echo(f"Complete!")
    typer.echo(f"Trimmed {v1.filename}: (start: {start}, end: {end}, duration: {duration})")
    typer.echo(f"Saved to {export_path}")


@app.command(short_help="plays the video. takes an index integer as an argument.")
def play(video_index: int):
    videos = pull_from_directory(recurse=True)
    typer.launch(videos[video_index].filepath)

    video_text = Text(f"Opened: {videos[video_index].filename}", justify="center")
    video_text.stylize("bold green on white", 0, 7)
    video_text.stylize("bold red on white", 8)
    console.print(video_text, justify="center")


@app.command(short_help="shows the video list. first column is the index integer used for the app.")
def show():
    videos = pull_from_directory(recurse=True)
    console.clear()

    table = Table(title="Available Videos", box=box.HORIZONTALS, leading=True, row_styles=["steel_blue3"])
    table_centered = Align.center(table)

    table.add_column("#")
    table.add_column("filename")
    table.add_column("full-path")
    table.add_column("size")
    table.add_column("date created")
    table.add_column("date modified")
    table.add_column("date accessed")

    for idx, video in enumerate(videos):
        table.add_row(
            f"{idx}",
            video.filename,
            video.folder_path,
            video.size,
            video.date_created,
            video.date_last_modified,
            video.date_last_opened
        )
    console.log(table_centered)


@app.command(short_help="changes the directory and overwrites the JSON file")
def change_directory():
    curr_folder = return_current_directory()

    console.print(f"[bold cyan]({curr_folder})[/bold cyan]", new_line_start=True)
    cwd = Prompt.ask(
        f"Where would you like your working directory to be?",
        default=curr_folder
    )
    if cwd != curr_folder:
        confirmed = Confirm.ask(f"Are you sure you would like to change the default directory?", default=False)
        if confirmed:
            change_current_directory(cwd)
            console.print(f"Changed directory to [green on white]{str(cwd)}[/green on white]!")
            return
    console.print(f"[green]Directory is the same![/green]")


if __name__ == "__main__":
    app()
