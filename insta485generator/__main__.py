"""Build static HTML site from directory of HTML templates and plain files."""
import pathlib
import shutil
import click
import jinja2
import json


# read configuration file
def read_config(config_filename):
    config_filename = pathlib.Path(config_filename)
    try:
        with config_filename.open() as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        click.echo(f"insta485generator error: '{config_filename}' not found",
                   err=True)
        exit(1)


@click.command()
@click.argument("input_dir", nargs=1, type=click.Path(exists=True))
# make the output directory always be defined
# (if the output directory is not given, mark it as "None")
@click.option("-o", "--output", type=click.Path(), default=None,
              help="Output directory.")
@click.option("-v", "--verbose", is_flag=True, help="Print more output.")
def main(input_dir, output, verbose):
    """Templated static website generator."""
    try:
        input_dir = pathlib.Path(input_dir)
        # read configuration file
        config = read_config(input_dir/"config.json")
        # read templates
        template_dir = pathlib.Path(input_dir/"templates")
        template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        # render template with context
        for item in config:
            try:
                temp_name = item['template']
                template_selected = template_env.get_template(temp_name)
                render_result = template_selected.render(item['context'])
            except jinja2.TemplateError as e:
                click.echo(f"insta485generator error:
                           '{temp_name}'\n{e.message}", err=True)
                exit(1)
            # write rendered content to output file
            if output:
                output_dir = pathlib.Path(output)
            else:
                output_dir = input_dir/"html"
            output_file = output_dir/item["url"].lstrip("/")/"index.html"
            # Check if the output directory already exists
            if output_dir.exists():
                raise FileExistsError(f"'{output_dir}' already exists")
            output_file.parent.mkdir(parents=True, exist_ok=False)
            with output_file.open("w") as file:
                file.write(render_result)
                # could not use output_file here
                # since we will use output_file later
            if verbose:
                print(f"Rendered {temp_name} -> {output_file}")
            # copy static directory
            static_dir = input_dir / 'static'
            if static_dir.exists():
                # shutil.copy() is very useful for copying directories
                shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)
                if verbose:
                    print(f"Copied {static_dir} -> {output_dir}")
    except json.JSONDecodeError as e:
        click.echo(f"insta485generator error: '{config}'\n{e.msg}", err=True)
        exit(1)
    except FileExistsError as e:
        click.echo(f"insta485generator error: {e}", err=True)
        exit(1)


# ==============================main=============================================
if __name__ == "__main__":
    main()
