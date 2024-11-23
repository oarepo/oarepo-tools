import click

@click.command("format")
@click.argument("file_path", required=False, multiple=True, default=["."])
def main(file_paths):
    print(file_paths)