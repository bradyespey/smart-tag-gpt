#!/usr/bin/env python3
"""
Script to convert all markdown files in provided directory to a single .enex file for importing into Evernote.
Also counts and verifies that all notes, images, and attachments are included in the output.
(c) 2022, 2023, 2024 Karl Brown
"""

import datetime
import logging
import os
import pathlib
import platform
import base64
import urllib.parse
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional, Tuple

import pypandoc
import typer
from lxml import etree


# Enum for App Configuration Constants with functions
class Appconfig(Enum):
    APP_NAME = "md2enex"
    APP_VERSION = "1.0.0"  # Hardcoded version number


class Doctypes(Enum):
    ENEX_DOCTYPE = '<!DOCTYPE en-export SYSTEM "http://xml.evernote.com/pub/evernote-export4.dtd">'
    ENML_DOCTYPE = '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'


IMPORT_TAG_WITH_DATETIME = (
    Appconfig.APP_NAME.value + "-import" + ":" + datetime.datetime.now().isoformat(timespec="seconds")
)

app = typer.Typer(add_completion=False)


# Function to get creation date in seconds since Jan 1, 1970
def creation_date_seconds(path_to_file):
    if platform.system() == "Windows":
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            return stat.st_mtime


def create_title(file: str) -> etree.Element:
    title = Path(file).stem
    title_el = etree.Element("title")
    title_el.text = title.strip()
    return title_el


def create_creation_date(file: str) -> etree.Element:
    creation_date_ts = creation_date_seconds(file)
    creation_date = enex_date_format(datetime.datetime.fromtimestamp(creation_date_ts, tz=datetime.timezone.utc))
    created_el = etree.Element("created")
    created_el.text = creation_date
    return created_el


def create_updated_date(file: str) -> etree.Element:
    # Preserve the original modified date
    modification_date_ts = os.path.getmtime(file)
    modification_date = enex_date_format(
        datetime.datetime.fromtimestamp(modification_date_ts, tz=datetime.timezone.utc)
    )
    updated_el = etree.Element("updated")
    updated_el.text = modification_date
    return updated_el


def create_tag() -> etree.Element:
    tag_el = etree.Element("tag")
    tag_el.text = IMPORT_TAG_WITH_DATETIME
    return tag_el


def create_note_attributes() -> etree.Element:
    note_attributes_el = etree.Element("note-attributes")
    note_attributes_el.text = os.linesep
    return note_attributes_el


def strip_note_el(en_note_el: etree.Element) -> etree.Element:
    etree.strip_attributes(en_note_el, "id", "class", "data", "data-cites")


def embed_images(html_text: str, file_dir: str, embedded_images: list) -> str:
    """
    Embed images as base64 within the HTML content and count the images.
    """
    def replace_image(match):
        img_src = match.group(1)
        img_path = os.path.join(file_dir, urllib.parse.unquote(img_src))  # Decode URL encoding
        if os.path.exists(img_path):
            with open(img_path, "rb") as img_file:
                img_data = img_file.read()
                encoded_img = base64.b64encode(img_data).decode('utf-8')
                embedded_images.append(img_src)  # Count embedded image
                return f'<img src="data:image/png;base64,{encoded_img}" />'
        else:
            logging.warning(f"Image {img_src} not found, skipping embedding.")
            return match.group(0)  # Leave the original img tag

    # Replace img tags with embedded base64 images
    import re
    html_text = re.sub(r'<img src="([^"]+)"', replace_image, html_text)
    return html_text


def check_invalid_tags(en_note_el: etree.Element):
    if len(en_note_el.findall(".//img")) or len(en_note_el.findall(".//figure")):
        logging.warning("Found image tags - attempting to embed images...")


def create_note_content(file: str, embedded_images: list) -> etree.Element:
    content_text = ""
    html_text = pypandoc.convert_file(
        file, to="html", format="markdown+hard_line_breaks-smart-auto_identifiers", extra_args=["--wrap=none"]
    )

    # Embed images within the HTML content
    file_dir = os.path.dirname(file)
    html_text = embed_images(html_text, file_dir, embedded_images)

    for index, line in enumerate(html_text.splitlines()):
        line_trimmed = line.strip()
        if index == 0 and line_trimmed.startswith("<h1"):
            continue
        content_text += line_trimmed

    en_note_el = etree.XML(f"<en-note>{content_text}</en-note>")
    strip_note_el(en_note_el)

    en_note_bytes = etree.tostring(
        en_note_el,
        encoding="UTF-8",
        method="xml",
        xml_declaration=True,
        pretty_print=False,
        standalone=False,
        doctype=Doctypes.ENML_DOCTYPE.value,
    )

    check_invalid_tags(en_note_el)

    content_el = etree.Element("content")
    content_el.text = etree.CDATA(en_note_bytes.decode("utf-8"))

    return content_el


def process_note(file: str, embedded_images: list) -> etree.Element:
    note_el = etree.Element("note")

    note_el.append(create_title(file))
    note_el.append(create_note_content(file, embedded_images))
    note_el.append(create_creation_date(file))
    note_el.append(create_updated_date(file))
    note_el.append(create_tag())
    note_el.append(create_note_attributes())

    return note_el


def enex_date_format(date: datetime) -> str:
    date_str = date.strftime("%Y%m%d") + "T" + date.strftime("%H%M%S") + "Z"
    return date_str


def create_en_export() -> etree.Element:
    now = datetime.datetime.now(datetime.timezone.utc)
    now_str = enex_date_format(now)
    en_export = etree.Element("en-export")
    en_export.set("export-date", now_str)
    en_export.set("application", Appconfig.APP_NAME.value)
    en_export.set("version", Appconfig.APP_VERSION.value)
    return en_export


def count_notes_and_images(target_directory: pathlib.Path) -> Tuple[int, int, int]:
    notes_count = 0
    images_count = 0
    attachments_count = 0

    for file in target_directory.glob("**/*.md"):
        notes_count += 1
        file_dir = os.path.dirname(file)
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            images_count += content.lower().count("![")
            attachments_count += content.lower().count("[[")
    
    return notes_count, images_count, attachments_count


def write_enex(target_directory: pathlib.Path, output_file: str):
    notes_count, images_count, attachments_count = count_notes_and_images(target_directory)
    typer.echo(f"Source directory contains: {notes_count} notes, {images_count} images, and {attachments_count} attachments.")

    files = sorted(target_directory.glob("*.md"), key=lambda fn: str.lower(fn.name))
    if len(files) <= 0:
        typer.echo("No markdown files found in " + target_directory.name, err=True)
        raise typer.Exit(code=1)

    root = create_en_export()
    embedded_images = []

    count = 0
    error_list = []
    for file in files:
        filename = str(file)
        try:
            root.append(process_note(filename, embedded_images))
            count += 1
        except (etree.LxmlError, ValueError) as e:
            error_list.append(filename)
            logging.warning("Parsing error " + str(e.__class__) + " occurred with file " + filename)
            logging.warning(e)

    tree = etree.ElementTree(root)
    tree.write(
        output_file,
        encoding="UTF-8",
        method="xml",
        pretty_print=True,
        xml_declaration=True,
        doctype=Doctypes.ENEX_DOCTYPE.value,
    )

    if len(error_list) > 0:
        logging.warning(
            "Some files were skipped - these need to be cleaned up manually and reimported: " + str(error_list)
        )

    typer.echo(f"Output ENEX file contains: {count} notes, {len(embedded_images)} images embedded.")
    if count == notes_count and len(embedded_images) == images_count:
        typer.echo("All notes and images were successfully processed!")
    else:
        typer.echo("Warning: Some notes or images may not have been processed correctly. Please verify manually.")

    if count > 0:
        typer.echo(f"Successfully wrote {count} markdown files to {output_file}")
    else:
        logging.error("Error - no files written.")
        raise typer.Exit(code=2)


def version_callback(value: bool):
    if value:
        typer.echo(Appconfig.APP_NAME.value + " (version " + Appconfig.APP_VERSION.value + ")")
        raise typer.Exit(code=0)


@app.command()
def cli(
    directory: Annotated[Path, typer.Argument(exists=True, file_okay=False, dir_okay=True, path_type=pathlib.Path)],
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            exists=False,
            dir_okay=False,
            path_type=pathlib.Path,
            help="Output file name. Existing file will be overwritten.",
        ),
    ] = "export.enex",
    version: Annotated[
        Optional[bool],  # noqa: UP007
        typer.Option("--version", "-v", callback=version_callback, help="Program version number"),
    ] = None,
):
    """Converts all markdown files in a directory into a single .enex file for importing to Evernote."""
    write_enex(directory, str(output))


def main():
    app()


if __name__ == "__main__":
    main()
